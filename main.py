from credentials import secret_key
from typing import List
from time import sleep
import requests
import json


def Download_Report(download_url: str) -> bool:

    response = requests.get(download_url)

    if response.status_code != 200:
        print(response.status_code)
        return False

    with open('output.csv', 'wb') as f:
        f.write(response.content)
    
    return True


def Poll_Report_URL(url: str) -> bool:

    headers = {
        "Authorization": f"Basic {secret_key}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json"
    }

    response = requests.get(url=url, headers=headers)

    if response.status_code != 200:
        print(f"Error in polling: {response.status_code}")
        return False

    while response.json()['status'] != 'COMPLETED':
        sleep(60)
        response = requests.get(url=url, headers=headers)

    return Download_Report(response.json()['url'])

def Get_Report(report_code: str, columns: List[str], filters: List[dict]=[], sort_by: List[dict]=[]) -> bool:
    url = "https://training.app.nulogy.net/api/reports/report_runs"

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
    result_url = Poll_Report_URL(status_url)

    return ''


Get_Report("receive_order", ["receive_order_code", "item_code", "item_description", "item_material_cost_per_unit"])

