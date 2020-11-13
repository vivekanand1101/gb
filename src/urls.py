from django.urls import path

from src.views import Analysis

app = "src"

urlpatterns = [path("<iteration_id>/analysis", Analysis.as_view(), name="analysis")]
