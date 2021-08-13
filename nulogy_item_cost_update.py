import utils.nulogy as nu
import utils.sql as sql
import csv

report_code = "item_master"
columns = ["code", "cost_per_unit", "item_type", "uuid"]
filters = [{"column": "item_type", "operator": "starts with", "threshold": "A"},
           {"column": "inactive", "operator": "=", "threshold": "false"}]

report = nu.get_report(report_code=report_code, columns=columns, filters=filters, headers=False)


nulogy_items = dict()
for row in report:
    nulogy_items[row[0]] = {'nulogy_cost': row[1], "UUID": row[3]}


query = """
SELECT
	ivt.NAMEALIAS				[ItemID]
	,ivtp.PRICE/CASE 
		WHEN ivtp.PRICEUNIT = 0 
		THEN 1 
		ELSE ivtp.PRICEUNIT END	[Cost]
    ,ivt.ITEMID                 [DAX ItemID]
FROM INVENTTABLE ivt
LEFT JOIN INVENTTABLEMODULE ivtp ON ivtp.ITEMID = ivt.ITEMID and ivtp.DATAAREAID = ivt.DATAAREAID and ivtp.MODULETYPE = 0
WHERE ivt.DATAAREAID = 'act'
  and ivt.ITEMGROUPID = 'AI'
  and ivt.NAMEALIAS <> ''
"""

r = sql.query(query=query)

for item, cost, dax_id in r:
    item = item.strip()
    if item in nulogy_items:
        nulogy_items[item]["dax_cost"] = f"{round(cost, 5):.5f}"

with open('output/item_cost_update.csv', 'w', newline='') as csvfile:

    fieldnames = ['Code', 'Old Cost Per Unit', 'Cost Per Unit', 'UUID']
    csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    csv_writer.writeheader()
    
    for item, record in nulogy_items.items():
        if record.get("nulogy_cost") != record.get("dax_cost"):
            csv_writer.writerow({"Code"             : item, 
                                 "Old Cost Per Unit": record.get("nulogy_cost"), 
                                 "Cost Per Unit"    : record.get("dax_cost"), 
                                 "UUID"             : record.get("UUID")})

