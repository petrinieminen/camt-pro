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
from collections import defaultdict, OrderedDict


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
        tenant_id = v[5]
        api_username = v[6]
        api_pass = v[7]

        if tenant_id:
            report_url = base_url + service_name + '/WS/' + default_company + '/Page/' + config_module.endpoints.report_endpoint + '?tenant=' + tenant_id
        else:
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
        tenant_id = v[5]
        api_username = v[6]
        api_pass = v[7]

        if tenant_id:
            report_url = base_url + service_name + '/WS/' + default_company + '/Page/' + config_module.endpoints.report_endpoint + '?tenant=' + tenant_id
        else:
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


def form_success_report(start_date, end_date):
    all_data = {}
    total_refs = 0
    total_payments = 0
    total_ref_success = 0
    total_ref_fails = 0
    total_payments_success = 0
    total_payments_fail = 0

    configs = get_configs()

    for v in configs.values_list():
        instance_name = v[1]
        base_url = v[2]
        service_name = v[3]
        default_company = html.escape(v[4])
        tenant_id = v[5]
        api_username = v[6]
        api_pass = v[7]
        
        if tenant_id:
            statement_url =  base_url + service_name + '/WS/' + default_company + '/Page/' + config_module.endpoints.report_endpoint + '?tenant=' + tenant_id
        else:
            statement_url =  base_url + service_name + '/WS/' + default_company + '/Page/' + config_module.endpoints.report_endpoint
    
        client = open_session(statement_url, api_username, api_pass)

        filter = [{
            "Field": "Banking_Date",
            "Criteria": f'{start_date}..{end_date}',                
        },]
        reports = client.service.ReadMultiple(filter, None, 1000)

        if reports:   
            instance_summary = defaultdict(dict)
            instance_ref_total = 0
            instance_payments_total = 0
            for report in reports:       
                comp_key = report["Company_Name"]
                instance = "CustomerEntity"
                ref_success_key = "RefSuccess"
                ref_fail_key = "RefFail"
                paym_success_key = "PaymSuccess"
                paym_fail_key = "PaymFail"   

                #stupid way to init 
                instance_summary[comp_key].setdefault(ref_success_key, 0)
                instance_summary[comp_key].setdefault(ref_fail_key, 0)
                instance_summary[comp_key].setdefault(paym_success_key, 0)
                instance_summary[comp_key].setdefault(paym_fail_key,  0)
                instance_summary[comp_key].setdefault(instance,  instance_name)


                if report["Ref_Payments_Status"] == "Posted":
                    total_refs += 1
                    instance_ref_total += 1
                    total_ref_success += 1
                    
                    try:
                        instance_summary[comp_key][ref_success_key] += 1
                    except KeyError:
                        instance_summary[comp_key].update({f"{ref_success_key}":  1})
                    
                elif report["Ref_Payments_Status"] == "On Journal":
                    total_refs += 1
                    total_ref_fails += 1
                    instance_ref_total += 1
                    
                    try:
                        instance_summary[comp_key][ref_fail_key] += 1
                    except KeyError:
                        instance_summary[comp_key].update({f"{ref_fail_key}":  1})

                if report["Vendor_Payments_Status"] == "Posted":
                    total_payments += 1
                    instance_payments_total += 1
                    total_payments_success += 1
                    try:
                        instance_summary[comp_key][paym_success_key] += 1
                    except KeyError:
                        instance_summary[comp_key].update({f"{paym_success_key}":  1})
                elif report["Vendor_Payments_Status"] == "On Journal":
                    total_payments += 1
                    total_payments_fail += 1
                    instance_payments_total += 1
                    try:
                        instance_summary[comp_key][paym_fail_key] += 1
                    except KeyError:
                        instance_summary[comp_key].update({f"{paym_fail_key}":  1})
            
            for k,v in instance_summary.items():
                ref_successrate = round(safe_div(v["RefSuccess"], (v["RefFail"] + v["RefSuccess"])),2) * 100
                payment_successrate = round(safe_div(v["PaymSuccess"], (v["PaymFail"] + v["PaymSuccess"])),2) * 100
                company_success_rate = round(safe_div(ref_successrate+payment_successrate, 2), 2)
                instance_summary[k].update({
                    "RefSuccessRate": ref_successrate,
                    "PaymentSuccessRate": payment_successrate,
                    "TotalSuccessRate": company_success_rate
                })

            all_data.update(instance_summary)
        else:
            print("No reports on given date range")

    all_data_sorted = OrderedDict(sorted(all_data.items(), key=lambda tup: (tup[1]["TotalSuccessRate"], tup[1]["RefSuccessRate"]), reverse=True))
    total_ref_success_rate = round(safe_div(total_ref_success, total_ref_success + total_ref_fails), 2) * 100
    total_payment_success_rate = round(safe_div(total_payments_success, total_payments_success + total_payments_fail), 2) * 100
    total_success_rate = round(safe_div(total_payment_success_rate + total_ref_success_rate , 2),2)
    totals = {
        "Total": {
            "total_refs": total_refs,
            "total_payments": total_payments,
            "RefFail": total_ref_fails,
            "RefSuccess": total_ref_success,
            "PaymFail": total_payments_fail,
            "PaymSuccess": total_payments_success,
            "RefSuccessRate": total_ref_success_rate,
            "PaymentSuccessRate": total_payment_success_rate,
            "TotalSuccessRate": total_success_rate,

        }
    }

    all_data_sorted.update(totals)
    print("ALL DATA", all_data_sorted)
    return all_data_sorted


def get_unhandled_statements():
    all_data = []
    configs = get_configs()

    for v in configs.values_list():

        base_url = v[2]
        service_name = v[3]
        default_company = html.escape(v[4])
        tenant_id = v[5]
        api_username = v[6]
        api_pass = v[7]

        companies = get_company_names(v)
        for company in companies:
            
            if tenant_id:
                statement_url =  base_url + service_name + '/WS/' + company + '/Page/' + config_module.endpoints.statement_endpoint + '?tenant=' + tenant_id
            else:
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
        tenant_id = v[5]
        api_username = v[6]
        api_pass = v[7]

        companies = get_company_names(v)
        for company in companies:
            if tenant_id:
                statement_url =  base_url + service_name + '/WS/' + company + '/Page/' + config_module.endpoints.statement_endpoint + '?tenant=' + tenant_id
            else:
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
    tenant_id = config[5]
    api_username = config[6]
    api_pass = config[7]

    if tenant_id:
        settings_url = base_url + service_name + '/WS/' + default_company + '/Page/' + config_module.endpoints.settings_endpoint + '?tenant=' + tenant_id
    else:
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
        tenant_id = v[5]
        api_username = v[6]
        api_pass = v[7]

        if tenant_id:
            report_url =  base_url + service_name + '/WS/' + default_company + '/Page/' + config_module.endpoints.report_endpoint + '?tenant=' + tenant_id
        else:
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
        if result:
            all_data += result 

    return all_data


def previous_working_day(date):
    fi_holidays = holidays.FI()
    yesterday = date - timedelta(days=1)

    if yesterday not in fi_holidays and yesterday.weekday() < 5:
        return yesterday

    return previous_working_day(yesterday)

def safe_div(x,y):
    if y == 0:
        return 0
    return x / y

def main():
    pass
    

if __name__ == '__main__':
    main()

