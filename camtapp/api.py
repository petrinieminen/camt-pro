import zeep
import html
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

def open_session(location, username, password):
    session = Session()
    session.auth = HTTPBasicAuth(username, password)

    wsdl_location = location
    client = zeep.Client(wsdl=wsdl_location, transport=Transport(session=session))

    return client


def get_iban_filtered_statements(iban):
    all_data = []

    configs = get_configs()
    for v in configs.values_list():

        base_url = v[2]
        service_name = v[3]
        default_company = html.escape(v[4])
        api_username = v[5]
        api_pass = v[6]

        report_url = base_url + service_name + '/WS/' + default_company + '/Page/' + config_module.endpoints.report_endpoint
        client = open_session(report_url,api_username, api_pass)


        filter = {
        "Field": "IBAN",
        "Criteria": f"{iban}"
        }
        result = client.service.ReadMultiple(filter, None, 1000)
        if result:
            all_data += result

    return all_data

def get_balance_difference_report():
    all_data = []

    configs = get_configs()
    for v in configs.values_list():
        
        base_url = v[2]
        service_name = v[3]
        default_company = html.escape(v[4])
        api_username = v[5]
        api_pass = v[6]

        report_url = base_url + service_name + '/WS/' + default_company + '/Page/' + config_module.endpoints.report_endpoint
        client = open_session(report_url,api_username, api_pass)

        today = date.today() - timedelta(days=0)
        previous_workday = previous_working_day(today)
        filter = [{
            "Field": "Balance_Difference",
            "Criteria": "<>0"
        }, {
                "Field": "Banking_Date",
                "Criteria": f"{previous_workday}"
            }]

        result = client.service.ReadMultiple(filter, None, 1000)
        if result:
            all_data += result

    return all_data

def get_unhandled_statements():
    all_data = []
    configs = get_configs()

    for v in configs.values_list():

        base_url = v[2]
        service_name = v[3]
        default_company = html.escape(v[4])
        api_username = v[5]
        api_pass = v[6]

        companies = get_company_names(v)
        for company in companies:
            statement_url =  base_url + service_name + '/WS/' + company + '/Page/' + config_module.endpoints.statement_endpoint
        
            client = open_session(statement_url, api_username, api_pass)

            filter = [{
                "Field": "Automation_Handled",
                "Criteria": False,                
            },]
            
            print("We are getting non handled statements for " + company)
            statements = client.service.ReadMultiple(filter, None, 1000)

            if statements:   
                for statement in statements:
                    statement["Company_Name"] = company
                    print("we have no match: ", statement)
                    print("statementin tyyppi:", type(statement))
                    print("statementTTIEn tyyppi:", type(statements))
                    all_data.append(statement)
            else:
                print("all handled")
    print("ALL DATA", all_data)
    return all_data

def get_balance_difference_statements():
    all_data = []
    configs = get_configs()

    for v in configs.values_list():

        base_url = v[2]
        service_name = v[3]
        default_company = html.escape(v[4])
        api_username = v[5]
        api_pass = v[6]

        companies = get_company_names(v)
        for company in companies:
            statement_url =  base_url + service_name + '/WS/' + company + '/Page/' + config_module.endpoints.statement_endpoint
        
            client = open_session(statement_url, api_username, api_pass)
            today = date.today() - timedelta(days=0)
            previous_workday = previous_working_day(today)

            filter = [{
                "Field": "G_L_Account_Balance_Matched",
                "Criteria": False,                
            }, {
                "Field": "Closing_Balance_Date",
                "Criteria": f"{previous_workday}"
            }]
            
            print("We are getting non matched statements for " + company)
            statements = client.service.ReadMultiple(filter, None, 1000)

            if statements:   
                for statement in statements:
                    statement["Company_Name"] = company
                    print("we have no match: ", statement)
                    print("statementin tyyppi:", type(statement))
                    print("statementTTIEn tyyppi:", type(statements))
                    all_data.append(statement)
            else:
                print("all match")
    print("ALL DATA", all_data)
    return all_data


def get_locations():
    locations = []
    for l in fields(config_module.api_locations):
        locations.append(getattr(config_module.api_locations, l.name))


    return locations

def get_location_names():
    locations = []
    configs = get_configs()
    for v in configs.values_list():
        locations.append(v[1])

    return locations


def get_company_names(config):
    company_names = []

    base_url = config[2]
    service_name = config[3]
    default_company = html.escape(config[4])
    api_username = config[5]
    api_pass = config[6]

    settings_url = base_url + service_name + '/WS/' + default_company + '/Page/' + config_module.endpoints.settings_endpoint
    client = open_session(settings_url, api_username, api_pass)
    filter = {
        "Field": "Company_Name",
        "Criteria": "<>''"
    }
    response = client.service.ReadMultiple(filter, None, 1000)

    for row in response:
        company_names.append(row["Company_Name"])

    return company_names

def get_yesterday():
    all_data = []
    configs = get_configs()
    for v in configs.values_list():

        base_url = v[2]
        service_name = v[3]
        default_company = html.escape(v[4])
        api_username = v[5]
        api_pass = v[6]

        report_url =  base_url + service_name + '/WS/' + default_company + '/Page/' + config_module.endpoints.report_endpoint
    
        print("current location: " + report_url)
        client = open_session(report_url, api_username, api_pass)

        today = date.today() - timedelta(days=0)
        previous_workday = previous_working_day(today)
        print(f"previous wdate was {previous_workday}  and today is {today}")

        filter = {
            "Field": "Banking_Date",
            "Criteria": f"{previous_workday}"
        }
        result = client.service.ReadMultiple(filter, None, 1000)
        all_data += result 

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

