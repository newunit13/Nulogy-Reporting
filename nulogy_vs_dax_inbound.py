import utils.nulogy as nu
import utils.sql as sql
import csv
import re

query = """
select
	pt.PURCHID					[DAX PO]
	,pt.VENDORREF				[Nulogy RO]
	,pt.CREATEDDATETIME			[Date Created]
	,CASE pt.PURCHSTATUS
		WHEN 1 THEN 'Open'
		WHEN 2 THEN 'Received'
	END AS						[Status]
	,pt.PURCHNAME				[Vendor]
	,pl.ITEMID					[DAX Item]
	,ivt.NAMEALIAS				[Nulogy Item]
	,ivt.ITEMNAME				[Item Description]
	,pl.PURCHQTY				[DAX Qty]
	,act.receivedInTotal(pl.INVENTTRANSID)	[DAX Received]
from PURCHTABLE pt
LEFT JOIN PURCHLINE pl ON pl.PURCHID = pt.PURCHID and pl.DATAAREAID = pt.DATAAREAID
LEFT JOIN INVENTTABLE ivt ON ivt.ITEMID = pl.ITEMID and ivt.DATAAREAID = pl.DATAAREAID
where pt.DATAAREAID = 'act'
  and ivt.ITEMGROUPID = 'AI'
  AND pt.PURCHSTATUS IN ('1', '2')
  AND pt.CREATEDDATETIME >= '2021-05-28'
  AND pt.VENDORREF <> 'Pallet IDs'
order by pt.PURCHID
"""

r = sql.query(query=query)

dax_purchase_orders = dict()
for row in r:
    po_code         = row[0]
    po_ref          = row[1]
    po_date         = row[2]
    po_received     = row[3]
    po_vendor       = row[4]
    po_item         = row[5]
    po_item_alias   = row[6]
    po_item_desc    = row[7]
    po_expected     = row[8]
    po_actual       = row[9]

    if po_code not in dax_purchase_orders:
        dax_purchase_orders[po_code] = {
            "po_ref"        : po_ref,
            "po_date"       : po_date,
            "po_received"   : po_received,
            "po_vendor"     : po_vendor,
            "po_items"      : {
                po_item_alias : {
                    "dax_code"      : po_item,
                    "item_code"     : po_item_alias,
                    "qty_expected"  : f'{po_expected:0.05f}',
                    "qty_actual"    : f'{po_actual:0.05f}'
                }
            }
        }
    else:
        dax_purchase_orders[po_code]["po_items"][po_item_alias] = {
            "dax_code"      : po_item,
            "item_code"     : po_item_alias,
            "qty_expected"  : f'{po_expected:0.05f}',
            "qty_actual"    : f'{po_actual:0.05f}'
        }


report_code = "receive_order"
columns = ["ro_date_at", "received", "receive_order_customer", "reference", "item_code", "expected_unit_quantity", "actual_unit_quantity"]
filters = [{"column": "receive_order_customer", "operator": "=", "threshold": "Accu-tec"}]


report = nu.get_report(report_code=report_code, columns=columns, filters=filters, headers=False)


nulogy_receive_orders = dict()
for row in report:
    ro_code     = row[0]
    ro_date     = row[1]
    ro_received = row[2]
    ro_customer = row[3]
    if re.match(r'(PO_\d{8})', row[4]):
        ro_ref = re.findall(r'(PO_\d{8})', row[4])[0]
    else:
        ro_ref = ''
    ro_item     = row[5]
    ro_expected = row[6]
    ro_actual   = row[7]

    if ro_code not in nulogy_receive_orders:
        nulogy_receive_orders[ro_code] = {
            "ro_date"       : ro_date,
            "ro_received"   : ro_received,
            "ro_customer"   : ro_customer,
            "ro_ref"        : ro_ref,
            "ro_items"      : {
                ro_item : {
                    "qty_expected"  : ro_expected,
                    "qty_actual"    : ro_actual
                }
            }
        }
    else:
        nulogy_receive_orders[ro_code]["ro_items"][ro_item] = {
            "qty_expected"  : ro_expected,
            "qty_actual"    : ro_actual
        }

    if ro_ref in dax_purchase_orders:
        nulogy_receive_orders[ro_code].update({
            "po_in_dax"     : 'True',
            "dax_po_status" : dax_purchase_orders[ro_ref]["po_received"]
        })
        if ro_item in dax_purchase_orders[ro_ref]["po_items"]:
            nulogy_receive_orders[ro_code]["ro_items"][ro_item].update({
                "item_in_dax"       : 'True',
                "dax_item_code"     : dax_purchase_orders[ro_ref]["po_items"][ro_item]["dax_code"],
                "dax_qty_expect"    : dax_purchase_orders[ro_ref]["po_items"][ro_item]["qty_expected"],
                "dax_qty_actual"    : dax_purchase_orders[ro_ref]["po_items"][ro_item]["qty_actual"],
            })
        else:
            nulogy_receive_orders[ro_code]["ro_items"][ro_item].update({
                "item_in_dax"       : 'False',
                "dax_item_code"     : '',
                "dax_qty_expect"    : '',
                "dax_qty_actual"    : '',
            })

    else:
        nulogy_receive_orders[ro_code].update({
            "po_in_dax"     : 'False',
            "dax_po_status" : ''
        })
        nulogy_receive_orders[ro_code]["ro_items"][ro_item].update({
            "item_in_dax"       : '',
            "dax_item_code"     : '',
            "dax_qty_expect"    : '',
            "dax_qty_actual"    : '',
        })



with open('output/nulogy_vs_dax_inbound.csv', 'w', newline='') as csvfile:

    fieldnames = ['Nulogy Receive Order', 'RO Date', 'Received in Nulogy', 'PO in DAX', 'DAX PO Number', 'Item Code', 
                  'Item in DAX', 'DAX Item Code', 'Nulogy Expected', 'Nulogy Received', 'DAX Expected', 'DAX Received']
    csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    csv_writer.writeheader()
    
    for receive_order, ro_details in nulogy_receive_orders.items():
        for item_code, item_details in ro_details["ro_items"].items():
            csv_writer.writerow({'Nulogy Receive Order' : receive_order,
                                 'RO Date'              : ro_details.get('ro_date'),
                                 'Received in Nulogy'   : ro_details.get('ro_received'),
                                 'PO in DAX'            : ro_details.get('po_in_dax'),
                                 'DAX PO Number'        : ro_details.get('ro_ref'),
                                 'Item Code'            : item_code,
                                 'Item in DAX'          : item_details.get('item_in_dax'),
                                 'DAX Item Code'        : item_details.get('dax_item_code'),
                                 'Nulogy Expected'      : item_details.get('qty_expected'),
                                 'Nulogy Received'      : item_details.get('qty_actual'),
                                 'DAX Expected'         : item_details.get('dax_qty_expect'),
                                 'DAX Received'         : item_details.get('dax_qty_actual')
                                }
                                )
