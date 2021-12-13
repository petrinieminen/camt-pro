
from django.urls import path
from camtapp import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", views.home, name="home"),
    path("hello/<name>", views.hello_there, name="hello_there"),
    path("yesterday", views.yesterdays_bank, name="yesterdays_bank"),
    path("yesterday_snug", views.yesterdays_bank_snug, name="yesterdays_bank_snug"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
]

urlpatterns += staticfiles_urlpatterns()
