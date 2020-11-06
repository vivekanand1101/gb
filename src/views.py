from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.views import View


class Profits(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "/login/"

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request):
        context = {"chartData": []}
        return render(request, "src/profits.html", context)
