import zeep

import csv
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

def get_yesterday():
    
    configs = get_configs()
    for v in configs.values_list():
        print("it's a " + v[3])

    session = Session()
    session.auth = HTTPBasicAuth(config_module.api_credentials.username, config_module.api_credentials.password)

    wsdl_location = config_module.api_locations.first


    client = zeep.Client(wsdl=wsdl_location, transport=Transport(session=session))


    today = date.today() - timedelta(days=0)
    previous_workday = previous_working_day(today)

    demofilter = {
        "Field": "Banking_Date",
        "Criteria": f"{previous_workday}"
    }
    demo = client.service.ReadMultiple(demofilter, None, 1000)

    return demo


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

