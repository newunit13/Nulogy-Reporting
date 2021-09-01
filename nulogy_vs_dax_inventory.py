from typing import NamedTuple
import utils.nulogy as nu
import utils.sql as sql
import csv

report_code = "inventory_snapshot"
columns = ["item_type", "base_quantity", "base_unit_of_measure", "item_description"]
filters = [{"column": "customer_name", "operator": "=", "threshold": "Accu-tec"}]

report = nu.get_report(report_code=report_code, columns=columns, filters=filters, headers=False)


nulogy_items = dict()
for row in report:
    nulogy_items[row[0]] = {
        'item_type'         : row[1], 
        "base_qty"          : f"{float(row[2]):,.2f}", 
        "base_uom"          : row[3], 
        "item_description"  : ''.join(row[4:])
    }

query = """
SELECT
    ivt.ITEMID                  [DAX Item ID]
	,ivt.NAMEALIAS              [Nulogy Item ID]
    ,ivt.ITEMNAME               [Item Description]
	,SUM(ivs.PHYSICALINVENT)    [Physical Inventory]
	,lower(ivti.UNITID)         [Inventory UOM]
FROM INVENTTABLE ivt
LEFT JOIN INVENTTABLEMODULE ivti ON ivti.ITEMID = ivt.ITEMID and ivti.DATAAREAID = ivt.DATAAREAID and ivti.MODULETYPE = 0
LEFT JOIN INVENTSUM ivs ON ivs.ITEMID = ivt.ITEMID and ivs.DATAAREAID = ivt.DATAAREAID
WHERE ivt.DATAAREAID = 'act'
  and ivt.ITEMGROUPID = 'AI'
  and ivs.PHYSICALINVENT <> 0
GROUP BY ivt.ITEMID, ivt.NAMEALIAS, ivt.ITEMNAME, ivti.UNITID
"""

r = sql.query(query=query)

items = dict()
nulogy_items_found = list()
for dax_item_id, nulogy_item_id, dax_item_desc, qty, uom in r:
    nulogy_item_id = nulogy_item_id.strip()
    items[dax_item_id] = {
        "DAX Item ID"       : dax_item_id,
        "DAX Item Alias"    : nulogy_item_id,
        "Item Description"  : dax_item_desc,
        "DAX Qty"           : f"{float(qty):,.2f}",
        "DAX UoM"           : uom
    }

    if nulogy_item_id in nulogy_items:
        items[dax_item_id].update({
            "Nulogy Item ID"    : nulogy_item_id,
            "Nulogy Qty"        : nulogy_items[nulogy_item_id].get("base_qty"),
            "Nulogy UoM"        : nulogy_items[nulogy_item_id].get("base_uom"),
            "Item Description"  : nulogy_items[nulogy_item_id].get("item_description"),
            "DAX Qty"           : f"{nu.convertToBaseUnits(nulogy_item_id, uom, qty):,.2f}",
            "DAX UoM"           : nulogy_items[nulogy_item_id].get("base_uom")
        })
        nulogy_items_found.append(nulogy_item_id)

unknown_item_id = 1000000
for item_id, details in nulogy_items.items():
    if item_id not in nulogy_items_found:
        items[unknown_item_id] = {
            "DAX Item ID"       : "",
            "DAX Item Alias"    : "",
            "Nulogy Item ID"    : item_id,
            "Item Description"  : details.get("item_description"),
            "Nulogy Qty"        : details.get("base_qty"),
            "Nulogy UoM"        : details.get("base_uom"),
            "DAX Qty"           : "",
            "DAX UoM"           : ""
        }
        unknown_item_id += 1

with open('output/inventory_snapshot.csv', 'w', newline='') as csvfile:

    fieldnames = ['DAX Item ID', 'DAX Item Alias', 'Nulogy Item ID', "Item Description", 'Nulogy Qty', 'Nulogy UOM', 'DAX Qty', 'DAX UOM']
    csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    csv_writer.writeheader()
    
    for record in items.values():
        csv_writer.writerow({"DAX Item ID"      : record.get("DAX Item ID"),
                             "DAX Item Alias"   : record.get("DAX Item Alias"),
                             "Nulogy Item ID"   : record.get("Nulogy Item ID"),
                             "Item Description" : record.get("Item Description"),
                             "Nulogy Qty"       : record.get("Nulogy Qty"), 
                             "Nulogy UOM"       : record.get("Nulogy UoM"),
                             "DAX Qty"          : record.get("DAX Qty"),
                             "DAX UOM"          : record.get("DAX UoM")
                             }
                            )
