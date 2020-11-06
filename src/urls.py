from django.urls import path

from src.views import Profits

app = "src"

urlpatterns = [path("", Profits.as_view(), name="profits")]
