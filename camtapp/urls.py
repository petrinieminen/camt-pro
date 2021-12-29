
from django.db.models.query import QuerySet
from django.urls import path, re_path
from camtapp import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from camtapp.models import ApiResource


home_list_view = views.HomeListView.as_view(
    queryset=ApiResource.objects.order_by("-log_date")[:5],  # :5 limits the results to the five most recent
    context_object_name="message_list",
    template_name="camtapp/home.html",
)

api_resource_list_view = views.ApiResourceView.as_view(
    queryset=ApiResource.objects.order_by("-log_date")[:5],
    context_object_name="api_resource_list",
    template_name="camtapp/api_resources.html",
)

urlpatterns = [
    path("", home_list_view, name="home"),
    path("hello/<name>", views.hello_there, name="hello_there"),
    path("yesterday", views.yesterdays_bank, name="yesterdays_bank"),
    path("yesterday_compact", views.yesterdays_bank_compact, name="yesterdays_bank_compact"),
    path("api_resource/", views.api_resource, name="api_resource"),
    path("api_resources/", api_resource_list_view, name="api_resources"),
    path("api_resources/", api_resource_list_view, name="api_resources"),
    path("delete_resource/<api_id>", views.delete_resource, name='delete_resource'),
    path("update_resource/<api_id>", views.update_resource, name='update_resource'),
]

urlpatterns += staticfiles_urlpatterns()

