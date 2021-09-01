from typing import Dict
import utils.nulogy as nu
import datetime
import utils.sql

START_DATE = (datetime.datetime.now() - datetime.timedelta(30)).strftime("%Y-%m-%d 00:00:00")
END_DATE = datetime.datetime.now().strftime("%Y-%m-%d 23:59:00")
CURRENT_TIMESTAMP = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")


report_code = "job_productivity"
columns = ["line_leader_name", "actual_job_end_at", "item_code", "line_name", "expected_units_per_person_hour", 
           "actual_person_hours_payable", "units_produced", "unit_of_measure", "machine_hours", "job_status",
           "actual_job_start_at"]
filters = [{"column": "actual_job_start_at", "operator": "between", "from_threshold": START_DATE, "to_threshold": END_DATE}]

report = nu.get_report(report_code=report_code, columns=columns, filters=filters, headers=False)

for line in report:
    job_number              = line[0]
    line_leader             = line[1]
    job_end_date            = line[2]
    item_code               = line[3]
    line_name               = line[4]
    expected_ppmh           = float(line[5])
    actual_payble_hours     = float(line[6])
    units_produced          = float(line[7])
    unit_of_measure         = line[8]
    machine_hours           = line[9]
    base_units_produced     = nu.convertToBaseUnits(item_code, unit_of_measure, units_produced)
    base_unit_of_measure    = nu.uoms[item_code]['base_unit']
    base_expected_ppmh      = nu.convertToBaseUnits(item_code, unit_of_measure, expected_ppmh)
    expected_hours          = units_produced / expected_ppmh
    expected_units          = expected_ppmh * actual_payble_hours
    acutal_ppmh             = units_produced / actual_payble_hours
    base_actual_ppmh        = base_units_produced / actual_payble_hours
    line_effeciency         = acutal_ppmh / expected_ppmh
    overspend_dollars       = 0 if actual_payble_hours <= expected_hours else (actual_payble_hours - expected_hours) * 14.2
    job_status              = line[10]
    job_start_date          = line[11]


    record = {
        "Job ID"                    : job_number, 
        "Line Leader"               : line_leader, 
        "Actual Job Start Date"     : job_start_date,
        "Actual Job End Date"       : job_end_date,
        "Item code"                 : item_code, 
        "Line Name"                 : line_name, 
        "Expected PPMH"             : expected_ppmh, 
        "Actual Hours"              : actual_payble_hours, 
        "Units Produced"            : units_produced, 
        "Unit of Measure"           : unit_of_measure, 
        "Base Units Produced"       : base_units_produced, 
        "Base Unit of Measure"      : base_unit_of_measure, 
        "Base UoM Expected PPMH"    : base_expected_ppmh, 
        "Expected Hours"            : expected_hours, 
        "Expected Units"            : expected_units, 
        "Actual PPMH"               : acutal_ppmh, 
        "Base Actual PPMH"          : base_actual_ppmh,
        "Line Effeciency"           : line_effeciency, 
        "Overspend $"               : overspend_dollars,
        "Train Hours"               : machine_hours,
        "Job Status"                : job_status,
        "Modified Date"             : CURRENT_TIMESTAMP
    }

    if job_status == "Started":

        utils.sql.insert(table="PRODUCTION_RECORDS", 
                        record=record, 
                        azure=True
                        )

    else:

        utils.sql.update(table="PRODUCTION_RECORDS",
                         key_column="Job ID",
                         key_value=job_number,
                         record=[(column, value) for column, value in record.items()],
                         azure=True)
