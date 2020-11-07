from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.views import View

from src.models import Iteration
from src.utils import get_all_account_deposit_monthwise
from src.utils import get_all_installment_dates
from src.utils import get_all_loan_deposit_monthwise
from src.utils import get_optimum_amount
from src.utils import get_total_threshold_amount


class Profits(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "/login/"

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request):
        iteration = Iteration.objects.first()
        months = get_all_installment_dates(iteration)

        account_paid = get_all_account_deposit_monthwise(months)
        loan_paid = get_all_loan_deposit_monthwise(months)
        threshold_paid = get_total_threshold_amount(iteration)
        optimum_paid = get_optimum_amount(iteration)

        interest_data = []
        penalty_data = []
        interest_plus_penalty_data = []
        threshold_data = []
        optimum_data = []

        datum = {"interest": 0, "penalty": 0, "interest_penalty": 0, "threshold": 0, "optimum": 0}
        for _date in months:
            for pay in account_paid:
                if pay.get("date") == _date:
                    datum["penalty"] += pay["total_penalty"]
                    datum["interest_penalty"] += pay["total_penalty"]
            datum["threshold"] = threshold_paid
            datum["optimum"] = optimum_paid

            for pay in loan_paid:
                if pay.get("date") == _date:
                    datum["penalty"] += pay["total_penalty"]
                    datum["interest"] += pay["total_interest"]
                    datum["interest_penalty"] += pay["total_penalty"] + pay["total_interest"]
            interest_data.append({"date": _date.strftime("%m/%d/%Y"), "y": datum["interest"]})
            penalty_data.append({"date": _date.strftime("%m/%d/%Y"), "y": datum["penalty"]})
            interest_plus_penalty_data.append(
                {"date": _date.strftime("%m/%d/%Y"), "y": datum["interest_penalty"]}
            )
            threshold_data.append({"date": _date.strftime("%m/%d/%Y"), "y": datum["threshold"]})
            optimum_data.append({"date": _date.strftime("%m/%d/%Y"), "y": datum["optimum"]})

        context = {
            "interestData": interest_data,
            "penaltyData": penalty_data,
            "interestPlusPenaltyData": interest_plus_penalty_data,
            "thresholdData": threshold_data,
            "optimumData": optimum_data,
        }
        return render(request, "src/profits.html", context)
