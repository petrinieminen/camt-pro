
from django.urls import path
from camtapp import views

urlpatterns = [
    path("", views.home, name="home"),
    path("hello/<name>", views.hello_there, name="hello_there"),
    path("yesterday", views.yesterdays_bank, name="yesterdays_bank")
]