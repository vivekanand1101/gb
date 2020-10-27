from datetime import datetime

from dateutil import relativedelta


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


def get_account_dues(obj):
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
    return int(
        (
            total_installments_missed
            * iteration.deposit_amount
            * (100 + iteration.late_deposit_fine)
            * (100 + iteration.interest_rate)
        )
        / (100 * 100)
    )
