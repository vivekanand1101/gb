from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from src.models import Account
from src.models import AccountDeposit
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

    form = AccountForm

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
    list_display = ("account_id", "customer_url", "iteration", "account_deposits_url")
    list_filter = ("customer__address",)
    search_fields = ("=id", "customer__name", "customer__address")
    readonly_fields = tuple()
    list_per_page = 50

    # def get_readonly_fields(self, request, obj):
    #     if obj:
    #         readonly_fields = ("number_of_accounts", )
    #         return readonly_fields
    #     else:
    #         return tuple()

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

    def account_deposits_url(self, obj):
        deposits = obj.deposits.count()
        if deposits > 0:
            url = reverse(f"admin:src_accountdeposit_changelist") + f"?account__id__exact={obj.id}"
            return format_html(f'<a href="{url}">{deposits}</a>')
        else:
            return 0


class CustomerAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {"fields": ("created_by", "modified_by", "name", "address", "phone_number")},),
    )
    list_display = (
        "name",
        "address",
        "phone_number",
        "number_of_accounts",
        "number_of_loans",
        "iteration_dues",
        "loan_dues",
        "total_dues",
    )

    list_filter = ("address",)
    search_fields = ("id", "name", "address")
    list_per_page = 50

    def number_of_accounts(self, obj):
        accounts = obj.accounts.count()
        if accounts > 0:
            url = reverse(f"admin:src_account_changelist") + f"?customer__id__exact={obj.id}"
            return format_html(f'<a href="{url}">{obj.accounts.count()}</a>')
        else:
            return 0

    def number_of_loans(self, obj):
        accounts = obj.loans.count()
        if accounts > 0:
            url = reverse(f"admin:src_loan_changelist") + f"?customer__id__exact={obj.id}"
            return format_html(f'<a href="{url}">{obj.loans.count()}</a>')
        else:
            return 0

    def iteration_dues(self, obj):
        total_iteration_dues = 0
        # current_date = datetime.today().date()
        for account in obj.accounts.all():
            iteration = account.iteration
            # iteration_start_date = iteration.start_date
            # diff = relativedelta.relativedelta(current_date, iteration_start_date)
            # total_months = (diff.years * 12) + diff.months
            # total_days = diff.days
            # import pdb; pdb.set_trace()
            # total_dues = (total_months * iteration.deposit_amount) + (total_days * iteration.late_deposit_fine)
            iteration_deposits = AccountDeposit.objects.filter(account=account).all()
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


class LoanAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {"fields": ("created_by", "modified_by", "customer", "iteration", "amount")},),
    )
    list_display = (
        "loan_url",
        "customer_url",
        "iteration",
        "amount",
        "loan_deposits_url",
    )
    list_filter = ("customer__address",)
    search_fields = ("id", "customer__name", "customer__address")
    list_per_page = 50

    def loan_url(self, obj):
        url = reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=[obj.id])
        return format_html(f'<a href="{url}">{obj.id}</a>')

    def customer_url(self, obj):
        customer = obj.customer
        url = reverse(
            f"admin:{customer._meta.app_label}_{customer._meta.model_name}_change",
            args=[customer.id],
        )
        return format_html(f'<a href="{url}">{customer.name}, {customer.address}</a>')

    def loan_deposits_url(self, obj):
        deposits = obj.deposits.count()
        if deposits > 0:
            url = reverse(f"admin:src_loandeposit_changelist") + f"?loan__id__exact={obj.id}"
            return format_html(f'<a href="{url}">{deposits}</a>')
        else:
            return 0


class LoanDepositAdmin(admin.ModelAdmin):

    fieldsets = ((None, {"fields": ("created_by", "modified_by", "loan", "date", "amount")}),)

    list_display = ("loan_deposit_id", "customer_url", "date", "amount", "loan_url")
    search_fields = ("id", "loan__customer__name", "loan__customer__address")
    list_per_page = 50

    def customer_url(self, obj):
        customer = obj.loan.customer
        url = reverse(
            f"admin:{customer._meta.app_label}_{customer._meta.model_name}_change",
            args=[customer.id],
        )
        return format_html(f'<a href="{url}">{customer.name}, {customer.address}</a>')

    def loan_deposit_id(self, obj):
        url = reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=[obj.id])
        return format_html(f'<a href="{url}">{obj.id}</a>')

    def loan_url(self, obj):
        loan = obj.loan
        url = reverse(
            f"admin:{loan._meta.app_label}_{loan._meta.model_name}_change", args=[loan.id],
        )
        return format_html(f'<a href="{url}">{loan.pk}</a>')


class AccountDepositAdmin(admin.ModelAdmin):

    fieldsets = ((None, {"fields": ("created_by", "modified_by", "date", "amount", "account")}),)

    list_display = (
        "iteration_deposit_id",
        "customer_url",
        "date",
        "amount",
        "account_url",
    )
    search_fields = ("id", "account__customer__name", "account__customer__address")
    raw_id_fields = ("account",)
    list_per_page = 50

    def customer_url(self, obj):
        customer = obj.account.customer
        url = reverse(
            f"admin:{customer._meta.app_label}_{customer._meta.model_name}_change",
            args=[customer.id],
        )
        return format_html(f'<a href="{url}">{customer.name}, {customer.address}</a>')

    def iteration_deposit_id(self, obj):
        url = reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=[obj.id])
        return format_html(f'<a href="{url}">{obj.id}</a>')

    def account_url(self, obj):
        account = obj.account
        url = reverse(
            f"admin:{account._meta.app_label}_{account._meta.model_name}_change", args=[account.id],
        )
        return format_html(f'<a href="{url}">{account.pk}</a>')


admin.site.register(Iteration)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Loan, LoanAdmin)
admin.site.register(LoanDeposit, LoanDepositAdmin)
admin.site.register(AccountDeposit, AccountDepositAdmin)
