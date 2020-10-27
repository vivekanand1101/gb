from datetime import datetime

from dateutil import relativedelta
from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from src.models import Account
from src.models import AccountDeposit
from src.models import Address
from src.models import Customer
from src.models import Iteration
from src.models import Loan
from src.models import LoanDeposit


class SuperUserAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False


class AccountForm(forms.ModelForm):

    number_of_accounts = forms.CharField()

    def save(self, commit=True):
        number_of_accounts = self.cleaned_data.get("number_of_accounts", None)
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
        fields = "__all__"


class AccountAdmin(admin.ModelAdmin):

    add_form = AccountForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "created_by",
                    "modified_by",
                    "customer",
                    "iteration",
                    "number_of_accounts",
                ),
            },
        ),
    )
    list_display = (
        "account_id",
        "customer_url",
        "iteration",
        "dues",
        "account_deposits",
        "last_deposit_date",
        "new_deposits",
    )
    list_filter = ("customer__address",)
    search_fields = ("=id", "customer__name", "customer__address")
    readonly_fields = tuple()
    list_per_page = 50
    autocomplete_fields = ("customer",)

    def dues(self, obj):
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

    def last_deposit_date(self, obj):
        objs = obj.deposits.order_by("-date")
        if objs.count() > 0:
            return objs[0].date
        return None

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs["form"] = self.add_form
        return super().get_form(request, obj, **kwargs)

    def customer_url(self, obj):
        customer = obj.customer
        url = reverse(
            f"admin:{customer._meta.app_label}_{customer._meta.model_name}_change",
            args=[customer.id],
        )
        return format_html(f'<a href="{url}">{customer.name}, {customer.address}</a>')

    def account_id(self, obj):
        url = reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=[obj.id])
        return format_html(f'<a href="{url}">{obj.pk}</a>')

    def account_deposits(self, obj):
        deposits = obj.deposits.count()
        if deposits > 0:
            url = reverse(f"admin:src_accountdeposit_changelist") + f"?account__id__exact={obj.id}"
            return format_html(f'<a href="{url}">{deposits}</a>')
        else:
            return 0

    def new_deposits(self, obj):
        url = reverse(f"admin:src_accountdeposit_add") + f"?account__id__exact={obj.id}"
        return format_html(f'<a href="{url}">Add New Deposit</a>')


class AccountDepositAdmin(admin.ModelAdmin):

    fieldsets = (
        (
            None,
            {"fields": ("created_by", "modified_by", "date", "principal", "penalty", "account")},
        ),
    )

    list_display = (
        "account_deposit_id",
        "customer_url",
        "date",
        "principal",
        "penalty",
        "account_url",
    )
    search_fields = ("=id", "account__customer__name", "account__customer__address")
    autocomplete_fields = ("account",)
    list_per_page = 50

    def customer_url(self, obj):
        customer = obj.account.customer
        url = reverse(
            f"admin:{customer._meta.app_label}_{customer._meta.model_name}_change",
            args=[customer.id],
        )
        return format_html(
            f'<a href="{url}">{customer.name}, {customer.address}, {customer.id}</a>'
        )

    def account_deposit_id(self, obj):
        url = reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=[obj.id])
        return format_html(f'<a href="{url}">{obj.id}</a>')

    def account_url(self, obj):
        account = obj.account
        url = reverse(
            f"admin:{account._meta.app_label}_{account._meta.model_name}_change", args=[account.id],
        )
        return format_html(f'<a href="{url}">{account.pk}</a>')


class CustomerAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {"fields": ("created_by", "modified_by", "name", "address", "phone_number")},),
    )
    list_display = (
        "customer_id",
        "name",
        "address",
        "phone_number",
        "accounts",
        "loans",
        "account_dues",
        "loan_dues",
        "total_dues",
        "account",
        "loan",
    )

    list_filter = ("address",)
    search_fields = ("=id", "name", "address", "phone_number")
    list_per_page = 50

    def account(self, obj):
        url = reverse(f"admin:src_account_add")
        return format_html(f'<a href="{url}">New</a>')

    def loan(self, obj):
        url = reverse(f"admin:src_loan_add")
        return format_html(f'<a href="{url}">New</a>')

    def customer_id(self, obj):
        return obj.id

    def accounts(self, obj):
        accounts = obj.accounts.count()
        if accounts > 0:
            url = reverse(f"admin:src_account_changelist") + f"?customer__id__exact={obj.id}"
            return format_html(f'<a href="{url}">{obj.accounts.count()}</a>')
        else:
            return 0

    def loans(self, obj):
        accounts = obj.loans.count()
        if accounts > 0:
            url = reverse(f"admin:src_loan_changelist") + f"?customer__id__exact={obj.id}"
            return format_html(f'<a href="{url}">{obj.loans.count()}</a>')
        else:
            return 0

    def account_dues(self, obj):
        total_iteration_dues = 0
        # current_date = datetime.today().date()
        # for account in obj.accounts.all():
        #     iteration = account.iteration
        # iteration_start_date = iteration.start_date
        # diff = relativedelta.relativedelta(current_date, iteration_start_date)
        # total_months = (diff.years * 12) + diff.months
        # total_days = diff.days
        # import pdb; pdb.set_trace()
        # total_dues = (total_months * iteration.deposit_amount) + (total_days * iteration.late_deposit_fine)
        # account_deposits = AccountDeposit.objects.filter(account=account).all()
        # total_deposit = 0
        # total_days_late = 0
        # for deposit in account_deposits:
        #     total_deposit += deposit.amount
        #     total_days_late += max((deposit.date.day - iteration.start_date.day), 0)
        # total_iteration_dues += (total_dues - total_deposit)
        return total_iteration_dues

    def loan_dues(self, obj):
        return 0

    def total_dues(self, obj):
        return self.account_dues(obj) + self.loan_dues(obj)


class LoanAdmin(admin.ModelAdmin):

    fieldsets = (
        (
            None,
            {"fields": ("created_by", "modified_by", "customer", "iteration", "amount", "status")},
        ),
    )
    list_display = (
        "loan_url",
        "customer_url",
        "iteration",
        "amount",
        "dues",
        "loan_deposits_url",
        "last_deposit_date",
        "status",
    )
    list_filter = ("customer__address",)
    search_fields = ("=id", "customer__name", "customer__address", "customer__phone_number")
    list_per_page = 50
    autocomplete_fields = ("customer",)

    def dues(self, obj):
        return 0

    def last_deposit_date(self, obj):
        objs = obj.deposits.order_by("-date")
        if objs.count() > 0:
            return objs[0].date
        return None

    def loan_url(self, obj):
        url = reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=[obj.id])
        return format_html(f'<a href="{url}">{obj.id}</a>')

    def customer_url(self, obj):
        customer = obj.customer
        url = reverse(
            f"admin:{customer._meta.app_label}_{customer._meta.model_name}_change",
            args=[customer.id],
        )
        return format_html(
            f'<a href="{url}">{customer.name}, {customer.address}, {customer.id}</a>'
        )

    def loan_deposits_url(self, obj):
        deposits = obj.deposits.count()
        if deposits > 0:
            url = reverse(f"admin:src_loandeposit_changelist") + f"?loan__id__exact={obj.id}"
            return format_html(f'<a href="{url}">{deposits}</a>')
        else:
            return 0


class LoanDepositAdmin(admin.ModelAdmin):

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "created_by",
                    "modified_by",
                    "loan",
                    "date",
                    "principal",
                    "interest",
                    "penalty",
                )
            },
        ),
    )

    list_display = (
        "loan_deposit_id",
        "customer_url",
        "date",
        "principal",
        "interest",
        "penalty",
        "loan_url",
    )
    search_fields = ("=id", "loan__id", "loan__customer__name", "loan__customer__address")
    list_per_page = 50
    autocomplete_fields = ("loan",)

    def customer_url(self, obj):
        customer = obj.loan.customer
        url = reverse(
            f"admin:{customer._meta.app_label}_{customer._meta.model_name}_change",
            args=[customer.id],
        )
        return format_html(
            f'<a href="{url}">{customer.name}, {customer.address}, {customer.id}</a>'
        )

    def loan_deposit_id(self, obj):
        url = reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=[obj.id])
        return format_html(f'<a href="{url}">{obj.id}</a>')

    def loan_url(self, obj):
        loan = obj.loan
        url = reverse(
            f"admin:{loan._meta.app_label}_{loan._meta.model_name}_change", args=[loan.id],
        )
        return format_html(f'<a href="{url}">{loan.pk}</a>')


admin.site.register(Iteration)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Loan, LoanAdmin)
admin.site.register(LoanDeposit, LoanDepositAdmin)
admin.site.register(AccountDeposit, AccountDepositAdmin)
admin.site.register(Address)
