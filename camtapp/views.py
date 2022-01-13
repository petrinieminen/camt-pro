from typing import List
import time
from django.http import HttpResponse
import re
from django.utils.timezone import datetime
import datetime as dt

from requests.sessions import Request
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


class ApiResourceView(ListView):
    model = ApiResource

    def get_context_data(self, **kwargs):
        context = super(ApiResourceView, self).get_context_data(**kwargs)
        return context


def hello_there(request, name):
    start_date = dt.datetime(2022, 1, 1)
    end_date = dt.datetime(2022, 1, 5)
    api.form_success_report(start_date.strftime("%m.%d.%Y"),end_date.strftime("%m.%d.%Y"))
    return render(
        request,
        'camtapp/hello_there.html',
        {
            'name': name,
            'date': datetime.now()
        }
    )

def camt_dashboard (request):
    data = None
    startdate = None
    enddate = None

    if request.method == "POST":
        if request.POST.get('startdate', False) and request.POST.get('enddate', False):
            startdate = dt.datetime.strptime(request.POST["startdate"], '%Y-%m-%d').strftime("%m.%d.%Y")
            enddate = dt.datetime.strptime(request.POST["enddate"], '%Y-%m-%d').strftime("%m.%d.%Y")
            data = api.form_success_report(startdate, enddate)


    return render(request,
                'camtapp/camt_dashboard.html',
                {
                    'data': data,
                    'startdate':  dt.datetime.strptime(startdate,"%m.%d.%Y").strftime("%d.%m.%Y") if startdate else startdate,
                    'enddate': dt.datetime.strptime(enddate,"%m.%d.%Y").strftime("%d.%m.%Y")  if enddate else enddate
                    
                })



def iban_filter(ibanfilter):
    data = api.get_iban_filtered_statements(ibanfilter)
    return data


def balance_difference_filter():
    data = api.get_balance_difference_report()
    return data


def unmatched_statements(request):
    t1 = time.time()
    data = None

    if request.method == "POST":
        if request.POST.get('BalanceDifference', False):
            data = api.get_balance_difference_statements()
        elif request.POST.get('Unhandled', False):
            data = api.get_unhandled_statements()            
    
    t2 = time.time()
    time_elapsed = t2 - t1
    pretty_time = str(dt.timedelta(seconds=time_elapsed))

    return render(request,
                  'camtapp/unmatched_statements.html',
                  {
                      'data': data,
                      'time_elapsed': pretty_time
                  })


def yesterdays_bank(request):
    if request.method == "POST":
        if request.POST.get('IbanFilter', False):
            data = iban_filter(request.POST["IbanFilter"])
        elif request.POST.get('BalanceDifference', False):
            data = balance_difference_filter()
        else:
            data = api.get_yesterday()
    else:
        print(request)
        data = api.get_yesterday()

    balance_difference_count = len([statement for statement in data if statement["Balance_Difference"] != 0])


    locations = api.get_location_names()
    return render(request,
                  'camtapp/yesterday.html',
                  {'data': data,
                   'locations': locations,
                   'total_count': len(data),
                   'balance_difference_count': balance_difference_count
                   })


def yesterdays_bank_compact(request):
    if request.method == "POST":
        if request.POST.get('IbanFilter', False):
            data = iban_filter(request.POST["IbanFilter"])
        elif request.POST.get('BalanceDifference', False):
            data = balance_difference_filter()
        else:
            data = api.get_yesterday()
    else:
        print(request)
        data = api.get_yesterday()

    balance_difference_count = len([statement for statement in data if statement["Balance_Difference"] != 0])

    locations = api.get_location_names()
    return render(request,
                  'camtapp/yesterday_compact.html',
                  {'data': data,
                   'locations': locations,
                   'total_count': len(data),
                   'balance_difference_count': balance_difference_count
                   })


def delete_resource(request, api_id=None):
    object = ApiResource.objects.get(id=api_id)

    object.delete()
    return redirect('api_resource')


def update_resource(request, api_id=None):
    object = ApiResource.objects.get(id=api_id)
    form = ApiResourceForm(request.POST or None, instance=object)

    if form.is_valid():
        transaction = form.save(commit=False)
        transaction.log_date = datetime.now()
        transaction.save()
        return redirect('api_resource')

    return render(request, 'camtapp/update_resource.html',
                  {
                      'resource': object,
                      'form': form
                  })


def api_resource(request):
    form = ApiResourceForm(request.POST or None)

    api_resource_list = ApiResource.objects.order_by("-log_date")

    if request.method == "POST":
        if form.is_valid():
            message = form.save(commit=False)
            message.log_date = datetime.now()
            message.save()
            return redirect("api_resource")
    else:
        return render(request, "camtapp/api_resource.html",
                      {
                          "form": form,
                          "resources": api_resource_list,
                      })
