import utils.nulogy as nu
import csv

report_code = "job_productivity"
columns = ["line_name", "machine_hours"]
filters = [{"column": "actual_job_start_at", "operator": "yesterday"}]

report = nu.get_report(report_code=report_code, columns=columns, filters=filters).decode("utf-8")
report = [line.replace('"', '') for line in report.split('\n')[1:] if len(line) > 1]


ds = dict()
for row in report:
    row = row.split(',')
    ds[row[0]] = {'line_number': row[1], "machine_hours": float(row[2]) if row[2] else 0}

report_code = "job_downtime"
columns = ["job_id", "downtime_duration"]
filters = [{"column": "actual_job_start_at", "operator": "yesterday"},
           {"column": "paid_downtime", "operator": "=", "threshold": "false"}]

report = nu.get_report(report_code=report_code, columns=columns, filters=filters).decode("utf-8")
report = [line.replace('"', '') for line in report.split('\n')[1:] if len(line) > 1]

for row in report:
    row = row.split(',')
    ds[row[0]]["downtime_minutes"] = float(row[1]) if row[1] else 0
    if ds[row[0]]["machine_hours"] > 0:
        ds[row[0]]["toc_payble_hours"] = round(((ds[row[0]]["machine_hours"]*60) - ds[row[0]]["downtime_minutes"])/60, 2)
    else:
        ds[row[0]]["toc_payble_hours"] = 0

with open('toc_payable_hours.csv', 'w', newline='') as csvfile:

    fieldnames = ['Job ID', 'Line Number', 'TOC Hours', 'Downtime Minutes', 'TOC Payable Hours']
    csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    csv_writer.writeheader()
    
    for item, record in ds.items():
        csv_writer.writerow({"Job ID"            : item, 
                             "Line Number"       : record.get("line_number"), 
                             "TOC Hours"         : record.get("machine_hours"), 
                             "Downtime Minutes"  : record.get("downtime_minutes"),
                             "TOC Payable Hours" : record.get("toc_payble_hours"),
                             }
                            )

