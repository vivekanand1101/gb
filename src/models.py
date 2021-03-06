from django.conf import settings
from django.contrib.postgres import fields as pg_fields
from django.db import models

# Create your models here.


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="%(class)s_createdby", on_delete=models.CASCADE,
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_modifiedby",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True


class Address(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        db_table = "address"
        verbose_name = "Address"
        verbose_name_plural = "Addresses"


class Iteration(BaseModel):
    start_date = models.DateField()
    interest_rate = models.IntegerField()
    no_of_months = models.IntegerField()
    deposit_amount = models.IntegerField()
    late_deposit_fine = models.IntegerField()
    is_active = models.BooleanField()
    day_of_payment = models.IntegerField()
    return_amount = models.IntegerField()

    def __str__(self):
        return "{}, {}".format(self.pk, self.start_date)

    class Meta:
        db_table = "iteration"
        verbose_name = "Iteration"
        verbose_name_plural = "Iterations"


class Customer(BaseModel):
    name = models.CharField(max_length=50)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    phone_number = models.CharField(max_length=10)

    def __str__(self):
        return "{}, {}, {}, Customer Id: {}".format(
            self.name, self.address.name, self.phone_number, self.pk
        )

    class Meta:
        db_table = "customers"
        verbose_name = "Customer"
        verbose_name_plural = "Customers"


class Account(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="accounts")
    iteration = models.ForeignKey(Iteration, on_delete=models.CASCADE, related_name="accounts")

    def __str__(self):
        return "{}, {}, Account Id: {}".format(self.customer, self.iteration, self.pk)

    class Meta:
        db_table = "accounts"
        verbose_name = "Account"
        verbose_name_plural = "Accounts"


class AccountDeposit(BaseModel):
    date = models.DateField()
    principal = models.IntegerField()
    penalty = models.IntegerField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="deposits")

    def __str__(self):
        customer = self.account.customer
        return "{}, {}, {}, Account Id: {}".format(
            customer.name, self.principal + self.penalty, self.date, self.account.pk
        )

    class Meta:
        db_table = "account_deposits"
        verbose_name = "Account Deposit"
        verbose_name_plural = "Account Deposits"


class Loan(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="loans")
    iteration = models.ForeignKey(Iteration, on_delete=models.CASCADE, related_name="loans")
    amount = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=[("PENDING", "PENDING"), ("APPROVED", "APPROVED")],
        default="APPROVED",
    )

    def __str__(self):
        return "Loan Id: {}, {}, {}".format(self.pk, self.customer, self.status)

    class Meta:
        db_table = "loans"
        verbose_name = "Loan"
        verbose_name_plural = "Loans"


class LoanDeposit(BaseModel):
    date = models.DateField()
    principal = models.IntegerField()
    interest = models.IntegerField()
    penalty = models.IntegerField()
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="deposits")

    def __str__(self):
        return "{}, {}, {}, Loan Deposit Id: {}".format(
            self.loan.pk, self.principal + self.interest + self.penalty, self.date, self.pk
        )

    class Meta:
        db_table = "loan_deposits"
        verbose_name = "Loan Deposit"
        verbose_name_plural = "Loan Deposits"


class Receipt(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="receipts")
    detail = pg_fields.JSONField()
    accounts = models.ManyToManyField(Account, related_name="receipts")

    def __str__(self):
        return f"{self.id}, {self.created_at}"

    class Meta:
        db_table = "receipts"
        verbose_name = "Receipt"
        verbose_name_plural = "Receipts"
