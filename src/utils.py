from datetime import datetime

from dateutil import relativedelta
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus.tables import Table
from reportlab.platypus.tables import TableStyle


def _principal_dues(obj, total_months, total_principal_paid):
    principal_should_be_paid = obj.amount * 0.1 * total_months
    return max(principal_should_be_paid - total_principal_paid, 0)


def get_loan_dues(obj, principal=False, interest=False, penalty=False):
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
    total_penalty = (
        total_installments_dues
        * (obj.amount - total_principal_paid)
        * (iteration.late_deposit_fine)
    ) / 100
    if penalty:
        return int(total_penalty)
    return int(total_principal_dues + total_interest + total_penalty)


def get_account_dues(obj, principal=False, penalty=False):
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
    principal_dues = total_installments_missed * iteration.deposit_amount
    if principal:
        return principal_dues
    penalty_dues = total_installments_missed * (
        iteration.late_deposit_fine + iteration.interest_rate
    )
    if penalty:
        return penalty_dues

    return int(principal_dues + penalty_dues)
    # return int(
    #     (
    #         total_installments_missed
    #         * iteration.deposit_amount
    #         * (100 + iteration.late_deposit_fine)
    #         * (100 + iteration.interest_rate)
    #     )
    #     / (100 * 100)
    # )


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
