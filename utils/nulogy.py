from utils.credentials import nulogy
from typing import List
from time import sleep
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
        "Authorization": f"Basic {nulogy['secret_key']}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json"
    }

    response = requests.get(url=url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Error in polling: {response.status_code}")

    while response.json()['status'] != 'COMPLETED':
        print('Report not yet ready, sleeping 60 seconds before next poll')
        sleep(60)
        response = requests.get(url=url, headers=headers)

    return response.json()['url']

def get_report(report_code: str, columns: List[str], filters: List[dict]=[], sort_by: List[dict]=[], headers: bool=True) -> bool:
    url = "https://app.nulogy.net/api/reports/report_runs"

    _headers = {
        "Authorization": f"Basic {nulogy['secret_key']}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json"
    }

    _data = json.dumps({
        "report" : report_code,
        "columns" : columns,
        "filters": filters,
        "sort_by": sort_by
    })

    response = requests.post(url=url, headers=_headers, data=_data)

    if response.status_code != 201:
        print(f"Error: {response.status_code}")
        return 'Error'

    # small sleep to give the report a chance to generate before polling for a download link
    sleep(30)

    status_url = response.json()['status_url']
    result_url = poll_report_url(status_url)
    report = downlad_report(result_url)

    report = csv.reader(report.split('\n'), delimiter=',', quotechar='"')

    if not headers:
        next(report)

    return report

if __name__ == '__main__':

    report_code = "pallet_aging"
    columns = ["location", "pallet_number", "item_code", "time_in_storage_minutes"]
    filters = [{"column": "location", "operator": "starts with", "threshold": "Line"}, 
               {"column": "item_type_name", "operator": "starts with", "threshold": "F"}]

    report = get_report(report_code=report_code, columns=columns, filters=filters)

    with open('output.csv', 'wb') as f:
        f.write(report)
