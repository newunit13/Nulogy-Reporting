import utils.nulogy as nu
import csv
from datetime import datetime
from utils.credentials import o365
from utils.email import Email

OUTPUT_FILE = f"output/{datetime.now().strftime('%Y%m%d-%H%M')}-ShipmentItems.csv"
SEND_TO = 'npittman@accu-tec.com'


report_code = "shipment_item"
columns = ["pallet_number", "ship_order_code", "ship_order_reference_number", "ship_order_customer_name", "carrier_code", "trailer_number", "item_code", "item_category_name", "actual_ship_at", "ship_to"]
filters = [{"column": "actual_ship_at", "operator": "today"}]

report = nu.get_report(report_code=report_code, columns=columns, filters=filters, headers=False)

pallets = dict()
for row in report:

    pallet_number = row[1] if row[1] != '' else f'{row[0]}-{row[7]}'
    pallets[pallet_number] = {
        "shipment_code"                 : row[0],
        "ship_order_code"               : row[2],
        "ship_order_reference_number"   : row[3],
        "ship_order_customer_name"      : row[4],
        "carrier_code"                  : row[5],
        "trailer_number"                : row[6],
        "item_code"                     : row[7],
        "item_category_name"            : row[8],
        "actual_ship_at"                : row[9],
        "ship_to"                       : row[10]
    }

report_code = "canned_inventory_transaction_history"
columns = ["id", "inventory_transaction", "pallet", "location_name", "item_code"]
filters = [{"column": "created_at", "operator": "today"}]

report = nu.get_report(report_code=report_code, columns=columns, filters=filters)

transactions = {}
for row in report:

    transaction_type = ' '.join(row[1].split(' ')[:-1])
    transaction_id = row[1].split(' ')[-1]

    if transaction_type not in transactions:
        transactions[transaction_type] = {}

    if transaction_id not in transactions[transaction_type]:
        transactions[transaction_type][transaction_id] = {}

    pallet_number = row[2] if row[2] != '--' else f"{transaction_id}-{row[4]}"
    transactions[transaction_type][transaction_id][pallet_number] = {
            "inventory_transaction_type"    : transaction_type,
            "inventory_transation_id"       : transaction_id,
            "pallet"                        : row[2],
            "location_name"                 : row[3],
            "item_code"                     : row[4]      
    }


with open(OUTPUT_FILE, 'w', newline='') as csvfile:

    fieldnames = ["ship_order_code", "ship_order_reference_number", "ship_order_customer_name", 
                  "carrier_code", "trailer_number", "shipment_code", "item_code", "item_category_name",
                  "pallet_number", "location_name", "actual_ship_at", "ship_to"]

    csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    csv_writer.writeheader()

    for pallet, details in pallets.items():
        details["location_name"] = transactions["Shipment"][details["shipment_code"]][pallet]["location_name"]

        csv_writer.writerow({
            "ship_order_code"               : details["ship_order_code"], 
            "ship_order_reference_number"   : details["ship_order_reference_number"], 
            "ship_order_customer_name"      : details["ship_order_customer_name"], 
            "carrier_code"                  : details["carrier_code"], 
            "trailer_number"                : details["trailer_number"], 
            "shipment_code"                 : details["shipment_code"], 
            "item_code"                     : details["item_code"], 
            "item_category_name"            : details["item_category_name"],
            "pallet_number"                 : pallet,
            "location_name"                 : details["location_name"], 
            "actual_ship_at"                : details["actual_ship_at"],
            "ship_to"                       : details["ship_to"]
        })

msg = Email(o365["username"], o365["password"])
msg.addAttachment(OUTPUT_FILE)
msg.sendMessage(SEND_TO, f"{datetime.now().strftime('%m/%d/%Y-%H:%M')} Shipments", '')
