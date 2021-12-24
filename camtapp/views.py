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

def iban_filter(ibanfilter):
    data = api.get_iban_filtered_statements(ibanfilter)
    return data

def balance_difference_filter():
    data = api.get_balance_difference_statements()
    return data

def yesterdays_bank(request):
    if request.method == "POST":
        if request.POST.get('IbanFilter', False):
            data = iban_filter(request.POST["ibanfiltertext"])
        elif request.POST.get('BalanceDifference', False):
            data = balance_difference_filter()
        else:
            data = api.get_yesterday()
    else:
        print(request)
        data = api.get_yesterday()

    return render(request,
    'camtapp/yesterday.html',
    { 'data': data})


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


def pretty_request(request):
    headers = ''
    for header, value in request.META.items():
        if not header.startswith('HTTP'):
            continue
        header = '-'.join([h.capitalize() for h in header[5:].lower().split('_')])
        headers += '{}: {}\n'.format(header, value)

    return (
        '{method} HTTP/1.1\n'
        'Content-Length: {content_length}\n'
        'Content-Type: {content_type}\n'
        '{headers}\n\n'
        '{body}'
    ).format(
        method=request.method,
        content_length=request.META['CONTENT_LENGTH'],
        content_type=request.META['CONTENT_TYPE'],
        headers=headers,
        body=request.body,
    )