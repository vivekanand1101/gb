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


class UserAccount(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    iteration = models.ForeignKey(Iteration, on_delete=models.CASCADE)

    def __str__(self):
        return "user: {}, id: {}".format(self.user, self.pk)

    class Meta:
        db_table = "user_account"
        verbose_name = "User Account"
        verbose_name_plural = "User Accounts"
