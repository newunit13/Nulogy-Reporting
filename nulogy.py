from credentials import secret_key
from typing import List
from time import sleep
import requests
import json


def downlad_report(download_url: str) -> str:

    response = requests.get(download_url)

    if response.status_code != 200:
        raise Exception(f"Invalid Status code downloading report: {response.status_code}")
    
    return response.content


def poll_report_url(url: str) -> str:

    headers = {
        "Authorization": f"Basic {secret_key}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json"
    }

    response = requests.get(url=url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Error in polling: {response.status_code}")

    while response.json()['status'] != 'COMPLETED':
        sleep(60)
        response = requests.get(url=url, headers=headers)

    return response.json()['url']

def get_report(report_code: str, columns: List[str], filters: List[dict]=[], sort_by: List[dict]=[]) -> bool:
    url = "https://app.nulogy.net/api/reports/report_runs"

    headers = {
        "Authorization": f"Basic {secret_key}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json"
    }

    data = json.dumps({
        "report" : report_code,
        "columns" : columns,
        "filters": filters,
        "sort_by": sort_by
    })

    response = requests.post(url=url, headers=headers, data=data)

    if response.status_code != 201:
        print(f"Error: {response.status_code}")
        return 'Error'

    status_url = response.json()['status_url']
    result_url = poll_report_url(status_url)
    report = downlad_report(result_url)

    return report



get_report("pallet_aging",
    ["location",
     "pallet_number",
     "item_code",
     "time_in_storage_minutes"
    ]
    ,[
        {
            "column": "location",
            "operator": "starts with",
            "threshold": "Line"
        },
        {
            "column": "item_type_name",
            "operator": "starts with",
            "threshold": "F"
        }
    ]
)

