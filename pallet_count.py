import utils.nulogy as nu
import utils.sql as sql
import csv

report_code = "inventory_snapshot"
columns = ["pallet_number", "item_type", "customer_name"]
filters = []

report = nu.get_report(report_code=report_code, columns=columns, filters=filters).decode("utf-8")
report = [line.replace('"', '') for line in report.split('\n')[1:] if len(line) > 1]


nulogy_items = dict()
for row in report:
    row = row.split(',')
    nulogy_items[row[1]] = {'item_number': row[0], "item_type": row[2], "customer_name": row[3]}


report_code = "pallet_aging"
columns = ["location", "pallet_number"]
filters = [{"column": "location", "operator": ""}]

report = nu.get_report(report_code=report_code, columns=columns).decode("utf-8")
report = [line.replace('"', '') for line in report.split('\n')[1:] if len(line) > 1]


for row in report:
    row = row.split(',')
    nulogy_items[row[1]]["location"] = row[0]

with open('output/pallet_counts.csv', 'w', newline='') as csvfile:

    fieldnames = ["pallet_number", "item_number", "item_type", "customer_name", "location"]

    csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    csv_writer.writeheader()

    for pallet_number, details in nulogy_items.items():

        if not details.get("location"):
            details["location"] = ""

        csv_writer.writerow({
            "pallet_number"     : pallet_number,
            "item_number"       : details["item_number"],
            "item_type"         : details["item_type"],
            "customer_name"     : details["customer_name"],
            "location"          : details["location"]
        })
