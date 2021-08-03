from os import utime
import utils.nulogy as nu
import utils.sql as sql
import csv
import io

report_code = "item_master"
columns = ["code", "cost_per_unit", "item_type"]
filters = [{"column": "item_type", "operator": "starts with", "threshold": "A"}]

report = nu.get_report(report_code=report_code, columns=columns, filters=filters).decode("utf-8")
report = [line.replace('"', '') for line in report.split('\n')[1:] if len(line) > 1]


#with open('output2.csv', 'wb') as f:
#    f.write(report)

for row in report:
    print(row.split(',')[0])



query = """
SELECT
	ivt.ITEMID					[DAX ItemID]
	,ivt.NAMEALIAS				[ItemID]
	,ivtp.PRICE/ivtp.PRICEUNIT	[Cost]
FROM INVENTTABLE ivt
LEFT JOIN INVENTTABLEMODULE ivtp ON ivtp.ITEMID = ivt.ITEMID and ivtp.DATAAREAID = ivt.DATAAREAID and ivtp.MODULETYPE = 0
WHERE ivt.DATAAREAID = 'act'
  and ivt.ITEMGROUPID = 'AI'
  and ivt.NAMEALIAS <> ''
  and ivtp.PRICEUNIT <> 0
"""

#r = sql.query(query=query)

