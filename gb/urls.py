"""gb URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include
from django.urls import path
from django.conf.urls import handler400
from django.conf.urls import handler403
from django.conf.urls import handler404
from django.conf.urls import handler500
from uuid import uuid4
import time


urlpatterns = [path("", admin.site.urls), path("iteration/", include("src.urls"))]

def http_not_found_view(request, *args, **kwargs):
    request_id = str(uuid4())
    request_epoch = time.time() * 1000
    response = 404
    return response
