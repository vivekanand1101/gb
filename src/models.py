from django.db import models
from django.conf import settings

# Create your models here.


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_createdby",
        on_delete=models.CASCADE,
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


class Iteration(BaseModel):
    start_date = models.DateField()
    interest_rate = models.IntegerField()
    no_of_months = models.IntegerField()
    deposit_amount = models.IntegerField()
    late_deposit_fine = models.IntegerField()
    is_active = models.BooleanField()
    day_of_payment = models.IntegerField()

    def __str__(self):
        return "start_date: {}, no_of_months: {}, deposit_amount: {}".format(
            self.start_date, self.no_of_months, self.deposit_amount
        )

    class Meta:
        db_table = "iteration"
        verbose_name = "Iteration"
        verbose_name_plural = "Iterations"


class Customer(BaseModel):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=10)

    def __str__(self):
        return "{}, {}, {}, Customer Id: {}".format(self.name, self.address, self.phone_number, self.pk)

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


class IterationDeposit(BaseModel):
    date = models.DateField()
    amount = models.IntegerField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        customer = self.account.customer
        return "{}, {}, {}, Account Id: {}".format(customer.name, self.amount, self.date, self.account.pk)

    class Meta:
        db_table = "iteration_deposits"
        verbose_name = "Iteration Deposit"
        verbose_name_plural = "Iteration Deposits"


class Loan(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="loans")
    iteration = models.ForeignKey(Iteration, on_delete=models.CASCADE, related_name="loans")
    amount = models.IntegerField()

    def __str__(self):
        return "{}, {}, {}, Loan Id: {}".format(self.customer, self.iteration, self.amount, self.pk)

    class Meta:
        db_table = "loans"
        verbose_name = "Loan"
        verbose_name_plural = "Loans"


class LoanDeposit(BaseModel):
    date = models.DateField()
    amount = models.IntegerField()
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="deposits")

    def __str__(self):
        return "{}, {}, {}, Loan Deposit Id: {}".format(self.loan.pk, self.amount, self.date, self.pk)

    class Meta:
        db_table = "loan_deposits"
        verbose_name = "Loan Deposit"
        verbose_name_plural = "Loan Deposits"
