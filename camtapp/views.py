from django.http import HttpResponse
import re
from django.utils.timezone import datetime
from camtapp import api
from django.shortcuts import render

def home(request):
    return render(request, "camtapp/home.html")

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
    

