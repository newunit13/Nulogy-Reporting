import utils.nulogy as nu
import utils.sql as sql
import csv

report_code = "inventory_snapshot"
columns = ["item_type", "base_quantity", "base_unit_of_measure"]
filters = [{"column": "customer_name", "operator": "=", "threshold": "Accu-tec"}]

report = nu.get_report(report_code=report_code, columns=columns, filters=filters).decode("utf-8")
report = [line.replace('"', '') for line in report.split('\n')[1:] if len(line) > 1]


nulogy_items = dict()
for row in report:
    row = row.split(',')
    nulogy_items[row[0]] = {'item_type': row[1], "base_qty": f"{float(row[2]):,.2f}", "base_uom": row[3]}


query = """
SELECT
	ivt.NAMEALIAS				[Item ID]
	,SUM(ivs.PHYSICALINVENT)	[Physical Inventory]
	,ivti.UNITID				[Inventory UOM]
FROM INVENTTABLE ivt
LEFT JOIN INVENTTABLEMODULE ivti ON ivti.ITEMID = ivt.ITEMID and ivti.DATAAREAID = ivt.DATAAREAID and ivti.MODULETYPE = 0
LEFT JOIN INVENTSUM ivs ON ivs.ITEMID = ivt.ITEMID and ivs.DATAAREAID = ivt.DATAAREAID
WHERE ivt.DATAAREAID = 'act'
  and ivt.ITEMGROUPID = 'AI'
  and ivs.PHYSICALINVENT <> 0
GROUP BY ivt.NAMEALIAS, ivti.UNITID
"""

r = sql.query(query=query)

for item, qty, uom in r:
    item = item.strip()
    if item in nulogy_items:
        nulogy_items[item]["dax_qty"] = f"{round(qty, 2):,.2f}"
        nulogy_items[item]["dax_uom"] = uom

with open('output/inventory_snapshot.csv', 'w', newline='') as csvfile:

    fieldnames = ['Item ID', 'Item Type', 'Nulogy Qty', 'Nulogy UOM', 'DAX Qty', 'DAX UOM']
    csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    csv_writer.writeheader()
    
    for item, record in nulogy_items.items():
        csv_writer.writerow({"Item ID"      : item, 
                             "Item Type"    : record.get("item_type"), 
                             "Nulogy Qty"   : record.get("base_qty"), 
                             "Nulogy UOM"   : record.get("base_uom"),
                             "DAX Qty"      : record.get("dax_qty"),
                             "DAX UOM"      : record.get("dax_uom")
                             }
                            )
