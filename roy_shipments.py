import utils.nulogy as nu
import csv
from utils.email import Email
from utils.credentials import o365
from datetime import datetime

OUTPUT_FILE = f"output/{datetime.now().strftime('%Y%m%d-%H%M')}-Shipments.csv"
SEND_TO = 'rkraemer@accu-tec.com'

report_code = "shipment_item"
columns = ["actual_ship_at", "ship_order_code", "bill_of_lading_number", "ship_order_shipped", "ship_order_customer_name", "carrier_code", "trailer_number", "ship_to"]
filters = [{"column": "actual_ship_at", "operator": "today"}]

report = nu.get_report(report_code=report_code, columns=columns, filters=filters)

with open(OUTPUT_FILE, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)

    temp = set()
    for line in report:
        line_str = ''.join(line)
        if line_str not in temp:
            csv_writer.writerow(line)
            temp.add(line_str)

msg = Email(o365["username"], o365["password"])
msg.addAttachment(OUTPUT_FILE)
msg.sendMessage(SEND_TO, f"{datetime.now().strftime('%m/%d/%Y-%H:%M')} Shipments", '')
