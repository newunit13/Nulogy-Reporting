import utils.nulogy as nu
import utils.sql as sql
import csv

report_code = "item_master"
columns = ["code", "cost_per_unit", "default_unit_of_measure", "uuid"]
filters = [{"column": "item_type", "operator": "starts with", "threshold": "A"},
           {"column": "inactive", "operator": "=", "threshold": "false"}]

report = nu.get_report(report_code=report_code, columns=columns, filters=filters, headers=False)


nulogy_items = dict()
for row in report:
    nulogy_items[row[0]] = {'nulogy_cost': row[1], "nulogy_uom": row[2], "UUID": row[3]}


query = """
SELECT
	ivt.NAMEALIAS				[ItemID]
	,ivti.PRICE/CASE 
		WHEN ivti.PRICEUNIT = 0 
		THEN 1 
		ELSE ivti.PRICEUNIT END	[Cost]
    ,ivt.ITEMID                 [DAX ItemID]
	,ivti.UNITID				[UOM]
FROM INVENTTABLE ivt

LEFT JOIN INVENTTABLEMODULE ivti ON 
	ivti.ITEMID     = ivt.ITEMID and 
	ivti.DATAAREAID = ivt.DATAAREAID and 
	ivti.MODULETYPE = 1

WHERE ivt.DATAAREAID = 'act'
  and ivt.ITEMGROUPID = 'AI'
  and ivt.NAMEALIAS <> ''
"""

r = sql.query(query=query)

for item, cost, dax_id, dax_uom in r:
    item = item.strip()
    if item in nulogy_items:
        nulogy_items[item]["dax_cost"] = f"{round(cost, 5):.5f}"
        nulogy_items[item]["dax_uom"] = f"{dax_uom}"

with open('output/item_cost_update.csv', 'w', newline='') as csvfile:

    fieldnames = ['Code', 'Old Cost Per Unit', 'Cost Per Unit', 'Nulogy UoM', 'DAX UoM', 'UUID']
    csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    csv_writer.writeheader()
    
    for item, record in nulogy_items.items():
        if record.get("nulogy_cost") != record.get("dax_cost"):
            csv_writer.writerow({"Code"             : item, 
                                 "Old Cost Per Unit": record.get("nulogy_cost"), 
                                 "Cost Per Unit"    : record.get("dax_cost"), 
                                 "Nulogy UoM"       : record.get("nulogy_uom"),
                                 "DAX UoM"          : record.get("dax_uom"),
                                 "UUID"             : record.get("UUID")})
