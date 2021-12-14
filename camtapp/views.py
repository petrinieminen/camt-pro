from django.http import HttpResponse
import re
from django.utils.timezone import datetime
from camtapp import api
from django.shortcuts import render

from django.shortcuts import redirect
from camtapp.forms import ApiResourceForm
from camtapp.models import ApiResource
from django.views.generic import ListView


class HomeListView(ListView):
    """Renders the home page, with a list of all messages."""
    model = ApiResource

    def get_context_data(self, **kwargs):
        context = super(HomeListView, self).get_context_data(**kwargs)
        return context


def about(request):
    return render(request, "hello/about.html")

def contact(request):
    return render(request, "hello/contact.html")


def hello_there(request, name):
    return render(
        request,
        'camtapp/hello_there.html',
        {
            'name': name,
            'date': datetime.now()
        }
    )


def yesterdays_bank(request):
    yesterday_data = api.get_yesterday()
    return render(request,
    'camtapp/yesterday.html',
    { 'data': yesterday_data})

def yesterdays_bank_snug(request):
    yesterday_data = api.get_yesterday()
    return render(request,
    'camtapp/yesterday_snug.html',
    { 'data': yesterday_data})
    

def api_resource(request):
    form = ApiResourceForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            message = form.save(commit=False)
            message.log_date = datetime.now()
            message.save()
            return redirect("home")
    else:
        return render(request, "camtapp/api_resource.html", {"form": form})