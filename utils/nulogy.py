from utils.config import NULOGY_SECRET_KEY
from typing import List
from time import sleep
from datetime import datetime
import requests
import json
import csv


def downlad_report(download_url: str) -> str:

    response = requests.get(download_url)

    if response.status_code != 200:
        raise Exception(f"Invalid Status code downloading report: {response.status_code}")
    
    return response.content.decode('utf-8')


def poll_report_url(url: str) -> str:

    headers = {
        "Authorization": f"Basic {NULOGY_SECRET_KEY}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json"
    }

    response = requests.get(url=url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Error in polling: {response.status_code}")

    while response.json()['status'] != 'COMPLETED':
        print('Report not yet ready, sleeping 10 seconds before next poll')
        sleep(10)
        response = requests.get(url=url, headers=headers)

    return response.json()['url']

def get_report(report_code: str, columns: List[str], filters: List[dict]=[], sort_by: List[dict]=[], headers: bool=True) -> bool:
    url = "https://app.nulogy.net/api/reports/report_runs"

    _headers = {
        "Authorization": f"Basic {NULOGY_SECRET_KEY}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json"
    }

    _data = json.dumps({
        "report" : report_code,
        "columns" : columns,
        "filters": filters,
        "sort_by": sort_by
    })

    error_count = 0
    while True:
        print(f"Submitting request for {report_code} report")
        response = requests.post(url=url, headers=_headers, data=_data)

        if response.status_code == 201:
            break
        
        if response.status_code != 201:
            with open(F'ERROR-{report_code}-{datetime.now().strftime("%Y%m%d-%H%M")}.txt', 'w') as outfile:
                outfile.write(f'{response.status_code}-{response.text}')
            if error_count > 3:
                raise Exception
            error_count += 1
            sleep(10)

    # small sleep to give the report a chance to generate before polling for a download link
    sleep(15)

    try:
        status_url = response.json()['status_url']
        result_url = poll_report_url(status_url)
        report = downlad_report(result_url)
        report = [line for line in report.split('\n') if line]      # remove blank lines

        report = csv.reader(report, delimiter=',', quotechar='"')

    except Exception as e:
        with open(F'EXCEPTION-{report_code}-{datetime.now().strftime("%Y%m%d-%H%M")}.txt', 'w') as outfile:
            outfile.write(f'{e}')
    
    if not headers:
        next(report)

    return report

if __name__ == '__main__':

    report_code = "pallet_aging"
    columns = ["location", "pallet_number", "item_code", "time_in_storage_minutes"]
    filters = [{"column": "location", "operator": "starts with", "threshold": "Line"}, 
               {"column": "item_type_name", "operator": "starts with", "threshold": "F"}]

    report = get_report(report_code=report_code, columns=columns, filters=filters)

