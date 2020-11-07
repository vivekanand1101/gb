import os

from datetime import datetime
from math import pow

from dateutil import relativedelta
from django.conf import settings
from django.db.models import F
from django.db.models import Sum
from pyinvoice.models import ClientInfo
from pyinvoice.models import InvoiceInfo
from pyinvoice.models import Item
from pyinvoice.models import ServiceProviderInfo
from pyinvoice.templates import SimpleInvoice
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus.tables import Table
from reportlab.platypus.tables import TableStyle

from src.models import AccountDeposit
from src.models import LoanDeposit

os.environ["INVOICE_LANG"] = "en"


def _principal_dues(obj, total_months, total_principal_paid):
    principal_should_be_paid = obj.amount * 0.1 * total_months
    return max(principal_should_be_paid - total_principal_paid, 0)


def get_loan_dues(obj, principal=False, interest=False, penalty=False, installments=False):
    deposits = obj.deposits.all()
    iteration = obj.iteration
    current_date = datetime.today().date()
    start_date = iteration.start_date
    diff = relativedelta.relativedelta(current_date, start_date)
    total_months = (diff.years * 12) + (diff.months)
    if diff.days > 0:
        total_months += 1
    total_months -= 1
    total_principal_paid = sum([deposit.principal for deposit in deposits])
    total_principal_dues = _principal_dues(obj, total_months, total_principal_paid)
    if principal:
        return int(total_principal_dues)
    total_installments_dues = int(total_principal_dues / (obj.amount * 0.1))
    total_installments_dues = max(total_installments_dues, 1)
    total_interest = (
        total_installments_dues * (obj.amount - total_principal_paid) * (iteration.interest_rate)
    ) / 100
    if interest:
        return int(total_interest)
    if installments:
        return total_installments_dues
    total_penalty = (
        max((total_installments_dues - 1), 0)
        * (obj.amount - total_principal_paid)
        * (iteration.late_deposit_fine)
    ) / 100
    if penalty:
        return int(total_penalty)
    return int(total_principal_dues + total_interest + total_penalty)


def get_account_dues(obj, principal=False, penalty=False, installments=False):
    deposits = obj.deposits.all()
    iteration = obj.iteration
    current_date = datetime.today().date()
    start_date = iteration.start_date
    diff = relativedelta.relativedelta(current_date, start_date)
    total_months = (diff.years * 12) + (diff.months)
    if diff.days > 0:
        total_months += 1
    total_principal_paid = sum([deposit.principal for deposit in deposits])
    total_installments_paid = int(total_principal_paid / iteration.deposit_amount)
    total_installments_missed = max(total_months - total_installments_paid, 0)
    if installments:
        return total_installments_missed
    principal_dues = total_installments_missed * iteration.deposit_amount
    if principal:
        return principal_dues
    penalty_dues = max((total_installments_missed - 1), 0) * (
        iteration.late_deposit_fine + iteration.interest_rate
    )
    if penalty:
        return penalty_dues

    return int(principal_dues + penalty_dues)


def get_account_installments(obj):
    deposits = obj.deposits.all()
    iteration = obj.iteration
    current_date = datetime.today().date()
    start_date = iteration.start_date
    diff = relativedelta.relativedelta(current_date, start_date)
    total_months = (diff.years * 12) + (diff.months)
    _html = ""
    for i in range(0, total_months + 1):
        installment_date = start_date + relativedelta.relativedelta(months=i)
        principal = 0
        penalty = 0
        for deposit in deposits:
            if deposit.date == installment_date:
                principal = deposit.principal
                penalty = deposit.penalty
        _installment = f"<td>{installment_date.strftime('%d-%m-%Y')}</td><td>{principal}<td>{penalty}</td></td>"
        _html += f"<tr>{_installment}</tr>"
    return _html


def get_loan_installments(obj):
    deposits = obj.deposits.all()
    iteration = obj.iteration
    current_date = datetime.today().date()
    start_date = iteration.start_date
    diff = relativedelta.relativedelta(current_date, start_date)
    total_months = (diff.years * 12) + (diff.months)
    _html = ""
    for i in range(1, total_months + 1):
        installment_date = start_date + relativedelta.relativedelta(months=i)
        principal = 0
        interest = 0
        penalty = 0
        for deposit in deposits:
            if deposit.date == installment_date:
                principal = deposit.principal
                interest = deposit.interest
                penalty = deposit.penalty
        _installment = f"<td>{installment_date.strftime('%d-%m-%Y')}</td><td>{principal}</td><td>{interest}</td><td>{penalty}</td>"
        _html += f"<tr>{_installment}</tr>"
    return _html


def generate_dues_pdf_response(response, data, header_text):
    elements = []
    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    style = ParagraphStyle(name="Header", parent=styles["Heading1"], alignment=TA_CENTER)
    header = Paragraph(header_text, style)
    elements.append(header)
    table_style = TableStyle(
        [
            ["GRID", (0, 0), (-1, -1), 1, colors.black],
            ["ALIGN", (0, 0), (-1, -1), "CENTER"],
            ["FONTNAME", (0, 0), (-1, 0), "Courier-Bold"],
        ]
    )
    _table = Table(data, style=table_style, repeatRows=1,)
    elements.append(_table)
    doc.build(elements)


def _get_customer_active_accounts(customer):
    accounts = customer.accounts.all()
    account_string = ""
    count = 0
    for i in accounts:
        account_string += f"{i.id}, "
        if count == 4:
            account_string += "\n"
        count += 1
    return account_string[:-2]


def generate_invoice(response, invoice_obj):
    customer = invoice_obj.customer
    doc = SimpleInvoice(
        response,
        pagesize="A4",
        provider_header=settings.COMPANY_NAME,
        client_header=customer.name,
        provider_address=settings.COMPANY_ADDRESS,
        client_address=customer.address.name,
    )

    # Paid stamp, optional
    doc.is_paid = True

    doc.service_provider_info = ServiceProviderInfo()
    doc.invoice_info = InvoiceInfo(invoice_obj.id, invoice_obj.created_at)

    doc.client_info = ClientInfo(
        name=customer.name,
        street=customer.address.name,
        city=_get_customer_active_accounts(customer),
    )

    # Add Item
    this_month = datetime.today().replace(day=15).date()
    accounts = invoice_obj.accounts.all()
    monthly_credit_count = 0
    monthly_penalty_count = 0
    total_credit = 0
    total_penalty = 0
    for account in accounts:
        for deposit in account.deposits.all():
            if deposit.date == this_month:
                monthly_credit_count += 1
                total_credit += deposit.principal
                total_penalty += deposit.penalty
                if deposit.penalty > 0:
                    monthly_penalty_count += 1

    total_loan_count = 0
    total_loan_principal = 0
    total_loan_interest = 0
    total_loan_penalty = 0
    total_penalty_count = 0
    for loan in customer.loans.all():
        for deposit in loan.deposits.all():
            if deposit.date == this_month:
                total_loan_count += 1
                total_loan_principal += deposit.principal
                total_loan_penalty += deposit.penalty
                total_loan_interest += deposit.interest
                if deposit.penalty > 0:
                    total_penalty_count += 1

    details = {
        "Account Credit": [monthly_credit_count, total_credit],
        "Account Penalty": [monthly_penalty_count, total_penalty],
        "Loan Principal": [total_loan_count, total_loan_principal],
        "Loan Interest": [total_loan_count, total_loan_interest],
        "Loan Penalty": [total_penalty_count, total_loan_penalty],
    }
    for key, value in details.items():
        doc.add_item(Item(key, value[0], value[1]))

    doc.set_bottom_tip("Don't hesitate to contact us for any questions!")

    doc.finish()

    invoice_obj.detail = details
    invoice_obj.save()


def get_all_installment_dates(iteration):
    start_date = iteration.start_date
    total_months = iteration.no_of_months
    day = iteration.day_of_payment

    months = []
    for i in range(1, total_months + 1):
        months.append((start_date + relativedelta.relativedelta(months=i)).replace(day=day))
    return months


def get_all_loan_deposit_monthwise(months):
    all_loan_deposits = (
        LoanDeposit.objects.filter(date__in=months)
        .values("date")
        .order_by("date")
        .annotate(total_principal=Sum("principal"))
        .annotate(total_interest=Sum("interest"))
        .annotate(total_penalty=Sum("penalty"))
        .annotate(total_amount=F("total_principal") + F("total_interest") + F("total_penalty"))
    )
    all_loan_deposits = list(all_loan_deposits)
    return all_loan_deposits


def get_all_account_deposit_monthwise(months):
    all_account_deposit = (
        AccountDeposit.objects.filter(date__in=months)
        .values("date")
        .order_by("date")
        .annotate(total_principal=Sum("principal"))
        .annotate(total_penalty=Sum("penalty"))
        .annotate(total_amount=F("total_principal") + F("total_penalty"))
    )
    all_account_deposit = list(all_account_deposit)
    return all_account_deposit


def get_total_threshold_amount(iteration):
    deposit_amount = iteration.deposit_amount * iteration.no_of_months
    return (iteration.return_amount - deposit_amount) * iteration.accounts.count()


def get_optimum_amount(iteration):
    _sum = 0
    for i in range(iteration.no_of_months, 0, -1):
        __sum = int(pow((1 + (iteration.interest_rate / 100)), i) * iteration.deposit_amount)
        _sum += __sum
    return (_sum - (iteration.deposit_amount * iteration.no_of_months)) * iteration.accounts.count()
