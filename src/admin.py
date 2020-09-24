from django.contrib import admin
from src.models import Account, Customer, IterationDeposit, Iteration

from datetime import datetime
from django import forms
from dateutil import relativedelta


class AccountForm(forms.ModelForm):

    number_of_accounts = forms.CharField()

    def save(self, commit=True):
        number_of_accounts = self.cleaned_data.get('number_of_accounts', None)
        number_of_accounts = int(number_of_accounts)
        for i in range(number_of_accounts - 1):
            obj = Account(
                customer=self.cleaned_data.get("customer"),
                iteration=self.cleaned_data.get("iteration"),
                created_by=self.cleaned_data.get("created_by"),
                modified_by=self.cleaned_data.get("modified_by"),
            )
            obj.save()
        return super(AccountForm, self).save(commit=commit)

    class Meta:
        model = Account
        fields = '__all__'

class AccountAdmin(admin.ModelAdmin):

    form = AccountForm

    fieldsets = (
        (None, {
            'fields': ('created_by', 'modified_by', 'customer', 'iteration', 'number_of_accounts',),
        }),
    )
    list_display = ("customer", "iteration")


class CustomerAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('created_by', 'modified_by', 'name', 'address', 'phone_number'),
        }),
    )
    list_display = ("name", "address", "phone_number", "number_of_accounts", "iteration_dues", "loan_dues", "total_dues")

    def number_of_accounts(self, obj):
        return obj.accounts.count()

    def iteration_dues(self, obj):
        total_iteration_dues = 0
        current_date = datetime.today().date()
        for account in obj.accounts.all():
            iteration = account.iteration
            iteration_start_date = iteration.start_date
            # diff = relativedelta.relativedelta(current_date, iteration_start_date)
            # total_months = (diff.years * 12) + diff.months
            # total_days = diff.days
            # import pdb; pdb.set_trace()
            # total_dues = (total_months * iteration.deposit_amount) + (total_days * iteration.late_deposit_fine)
            iteration_deposits = IterationDeposit.objects.filter(account=account).all()
            total_deposit = 0
            total_days_late = 0
            for deposit in iteration_deposits:
                total_deposit += deposit.amount
                total_days_late += max((deposit.date.day - iteration.start_date.day), 0)
            # total_iteration_dues += (total_dues - total_deposit)
        return total_iteration_dues

    def loan_dues(self, obj):
        return 0

    def total_dues(self, obj):
        return self.iteration_dues(obj) + self.loan_dues(obj)


admin.site.register(Iteration)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(IterationDeposit)
