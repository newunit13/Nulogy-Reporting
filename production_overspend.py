import utils.nulogy as nu
import csv
from datetime import datetime

short_to_long_uom = {
    'ea'    : 'eaches',
    'cs'    : 'cases',
    'pl'    : 'pallets',
    'rl'    : 'rolls',
    'lbs'   : 'pounds',
    'bdl'   : 'bundles',
    'pk'    : 'packs',
    'kg'    : 'kilograms',
    'ltr'   : 'liters',
    'box'   : 'boxes',
    'gal'   : 'gallons',
    'ft'    : 'feet'
}

report_code = "uom_ratios"
columns = ["code", "unit_of_measure", "ratio", "conversion_unit_of_measure"]

report = nu.get_report(report_code=report_code, columns=columns, headers=False)

uoms = dict()
for line in report:
    item_code   = line[0]
    from_unit   = line[1]
    factor      = float(line[2])
    to_unit     = line[3]

    if item_code not in uoms:
        uoms[item_code] = {
            "conversions" : [{"from_unit": from_unit, "factor": factor, "to_unit": to_unit}]
        }
    else:
        uoms[item_code]["conversions"].append({"from_unit": from_unit, "factor": factor, "to_unit": to_unit})

report_code = "item_master"
columns = ["code", "base_unit_of_measure"]
filters = [{"columns": "inactive", "operator": "=", "threshold": "False"}]

report = nu.get_report(report_code=report_code, columns=columns, headers=False)

for line in report:
    item_code = line[0]
    base_unit = line[1]

    if item_code in uoms:
        uoms[item_code].update({"base_unit": base_unit})
    else:
        uoms[item_code] = {
            "base_unit"     : base_unit,
            "conversions"   : [{"from_unit": base_unit, "factor": 1, "to_unit": base_unit}]
        }

def convertToBaseUnits(item_code: str, unit_of_measure: str, number_of_units: float) -> float:
    '''
        Returns the number of base units for a specified item.

            Parameter:
                item_code (str)         : The Nulogy Item Code
                unit_of_measure (str)   : The unit of measure to be converted from
                number_of_units (float) : The number of units to be converted into base units

            Returns:
                number_of_units (float) : The number of base units 
    '''

    # if a short code UOM is supplied convert it over to the long form
    if unit_of_measure in short_to_long_uom:
        unit_of_measure = short_to_long_uom[unit_of_measure]

    # if the number of units wasn't in a numeric type convert it
    if not isinstance(number_of_units, float):
        number_of_units = float(number_of_units)

    item_base_unit = uoms[item_code]["base_unit"]
    if unit_of_measure == item_base_unit:
        return number_of_units

    for conversion in uoms[item_code]["conversions"]:
        if conversion["from_unit"] == unit_of_measure:
            number_of_units = number_of_units * conversion["factor"]
            unit_of_measure = conversion["to_unit"]
            break
    else:
        raise Exception(f"Unable to find {unit_of_measure} in {item_code} conversions.")

    return convertToBaseUnits(item_code, unit_of_measure, number_of_units)


report_code = "job_productivity"
columns = ["line_leader_name", "actual_job_end_at", "item_code", "line_name", "expected_units_per_person_hour", 
           "actual_person_hours_payable", "units_produced", "unit_of_measure", "machine_hours"]
filters = [{"column": "actual_job_start_at", "operator": "today"}]
sort_by = [{"column": "line_name", "direction": 'asc'}]

report = nu.get_report(report_code=report_code, columns=columns, filters=filters, sort_by=sort_by, headers=False)

with open(f'\\\\b4bfile01\\Accudata\\Accu-tec Daily\\Autoreports\\Raw data\\Job Productivity\\{datetime.now().strftime("%m%d%Y-%H%M")}-job_productivity.csv', 'w', newline='') as csvfile:

    fieldnames = ["Job", "Line Leader", "Actual Job End Date", "Item code", "Line Name", "Expected PPMH", "Actual Hours", "Units Produced", "Unit of Measure",
                  "Base Units Produced", "Base Unit of Measure", "Base UoM Expected PPMH", "Expected Hours", "Expected Units", "Actual PPMH", "Base Actual PPMH",
                  "Line Effeciency", "Overspend $", "Train Hours"]

    csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    csv_writer.writeheader()

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
        base_units_produced     = convertToBaseUnits(item_code, unit_of_measure, units_produced)
        base_unit_of_measure    = uoms[item_code]['base_unit']
        base_expected_ppmh      = convertToBaseUnits(item_code, unit_of_measure, expected_ppmh)
        expected_hours          = units_produced / expected_ppmh
        expected_units          = expected_ppmh * actual_payble_hours
        acutal_ppmh             = units_produced / actual_payble_hours
        base_actual_ppmh        = base_units_produced / actual_payble_hours
        line_effeciency         = acutal_ppmh / expected_ppmh
        overspend_dollars       = 0 if actual_payble_hours <= expected_hours else (actual_payble_hours - expected_hours) * 14.2

        csv_writer.writerow({
            "Job"                       : job_number, 
            "Line Leader"               : line_leader, 
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
            "Train Hours"               : machine_hours
        })

