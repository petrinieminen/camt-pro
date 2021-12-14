
from django.urls import path
from camtapp import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from camtapp.models import ApiResource

home_list_view = views.HomeListView.as_view(
    queryset=ApiResource.objects.order_by("-log_date")[:5],  # :5 limits the results to the five most recent
    context_object_name="message_list",
    template_name="camtapp/home.html",
)

urlpatterns = [
    path("", home_list_view, name="home"),
    path("hello/<name>", views.hello_there, name="hello_there"),
    path("yesterday", views.yesterdays_bank, name="yesterdays_bank"),
    path("yesterday_snug", views.yesterdays_bank_snug, name="yesterdays_bank_snug"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("api_resource/", views.api_resource, name="api_resource"),
]

urlpatterns += staticfiles_urlpatterns()

