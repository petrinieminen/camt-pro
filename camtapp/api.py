import zeep

import csv
from dataclasses import fields
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.
from requests import Session
from zeep.transports import Transport
from zeep.settings import Settings
from lxml import etree
from zeep.plugins import HistoryPlugin
from datetime import date, timedelta
import holidays
from camtapp import config as config_module
from camtapp.models import ApiResource


def get_configs():
    return ApiResource.objects.all()

def open_session(location):
    session = Session()
    session.auth = HTTPBasicAuth(config_module.api_credentials.username, config_module.api_credentials.password)

    wsdl_location = location
    client = zeep.Client(wsdl=wsdl_location, transport=Transport(session=session))

    return client


def get_iban_filtered_statements(iban):

    client = open_session()

    demofilter = {
    "Field": "IBAN",
    "Criteria": f"{iban}"
    }
    demo = client.service.ReadMultiple(demofilter, None, 1000)

    return demo


def get_balance_difference_statements():
    locations = get_locations()

    all_data = []
    for location in locations:

        client = open_session(location)
        demofilter = {
            "Field": "Balance_Difference",
            "Criteria": "<>0"
        }
        
        demo = client.service.ReadMultiple(demofilter, None, 1000)
        all_data += demo

    return all_data

def get_locations():
    locations = []
    for l in fields(config_module.api_locations):
        locations.append(getattr(config_module.api_locations, l.name))
    return locations

def get_yesterday():
    
    locations = get_locations()

    configs = get_configs()
    for v in configs.values_list():
        print("it's a " + v[3])

    all_data = []
    for location in locations:
        print("current location: " + location)
        client = open_session(location)


        today = date.today() - timedelta(days=0)
        previous_workday = previous_working_day(today)
        print(f"previous wdate was {previous_workday}  and today is {today}")

        demofilter = {
            "Field": "Banking_Date",
            "Criteria": f"{previous_workday}"
        }
        demo = client.service.ReadMultiple(demofilter, None, 1000)
        all_data += demo 

    return all_data


def previous_working_day(date):
    fi_holidays = holidays.FI()
    yesterday = date - timedelta(days=1)

    if yesterday not in fi_holidays and yesterday.weekday() < 5:
        return yesterday

    return previous_working_day(yesterday)

def load_conf_file(config_file):
    pass


def main():
    print(config_module.api_credentials.username)
    print(get_configs())
    
if __name__ == '__main__':
    main()

