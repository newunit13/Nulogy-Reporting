import utils.nulogy as nu
import csv

report_code = "canned_inventory_transaction_history"
columns = ["id", "inventory_transaction", "item_code", "item_description", 
           "location_name", "pallet", "transaction_quantity_value", 
           "transaction_quantity_uom_short_label", "base_quantity_value", "base_quantity_uom_short_label"]
filters = [{"column": "created_at", "operator": "yesterday"}]

report = nu.get_report(report_code=report_code, columns=columns, filters=filters).decode("utf-8")
report = [line.replace('"', '') for line in report.split('\n')[1:] if len(line) > 1]

with open('output/transaction_history.csv', 'w', newline='') as csvfile:

    fieldnames = ["id", "inventory_transaction_type", "inventory_transation_id", "item_code", "item_description", 
                  "location_name", "pallet", "transaction_quantity_value", 
                  "transaction_quantity_uom_short_label", "base_quantity_value", "base_quantity_uom_short_label"]

    csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    csv_writer.writeheader()

    for row in report:
        row = row.split(',')
        csv_writer.writerow({
            "id"                                    : row[0],
            "inventory_transaction_type"            : ' '.join(row[1].split(' ')[:-1]),
            "inventory_transation_id"               : row[1].split(' ')[-1], 
            "item_code"                             : row[2], 
            "item_description"                      : row[3], 
            "location_name"                         : row[4], 
            "pallet"                                : row[5], 
            "transaction_quantity_value"            : row[6], 
            "transaction_quantity_uom_short_label"  : row[7], 
            "base_quantity_value"                   : row[8], 
            "base_quantity_uom_short_label"         : row[9]
        })
