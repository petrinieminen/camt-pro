from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("camtapp.urls")),
    path('admin/', admin.site.urls)
]