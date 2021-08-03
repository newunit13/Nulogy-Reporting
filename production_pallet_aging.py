import utils.nulogy as nu
from utils.email import Email
from utils.credentials import o365

MAX_PALLET_AGE_MINUTES = 15

def main ():
    
    report_code = "pallet_aging"
    columns = ["location", "pallet_number", "item_code", "time_in_storage_minutes"]
    filters = [{"column": "location", "operator": "starts with", "threshold": "Line"}, 
               {"column": "item_type_name", "operator": "starts with", "threshold": "F"}]

    report = nu.get_report(report_code=report_code, columns=columns, filters=filters).decode('utf-8')

    # clean up report lines and remove headers and empty lines
    report = [line.replace('"', '') for line in report.split('\n')[1:] if len(line) > 1]

    # counter for how many pallets are beyond the max age threshold
    aged_pallet_count = 0

    if len(report) > 0:

        email_body = """
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=us-ascii">
    <style>
        table, th, td {
            border: 1px solid black;
            border-collapse: collapse;
            padding-left: 15px;
            padding-right: 15px;
        }
    </style>
  </head>
  <body>
    <table style="75%">
      <tr>
        <th>Location</th>
        <th>Pallet</th>
        <th>Item #</th>
        <th>Time in storage (in minutes)</th>
      </tr>"""
        for line in report:
            line = line.split(',')
            
            location = line[0]
            pallet   = line[1]
            item     = line[2]
            age      = int(line[3])
            if age > MAX_PALLET_AGE_MINUTES:
                aged_pallet_count += 1
                email_body += f"""
      <tr>
        <td>{location}</td>
        <td>{pallet}</td>
        <td>{item}</td>
        <td style="text-align: center">{age:,}</td>
      </tr>"""

        else:
            email_body += """
    </table>
  </body>
</html>"""

        if aged_pallet_count > 0:
            email_msg = Email(o365['username'], o365['password'])
            email_msg.sendMessage('erussell@ciservicesnow.com', 'Pallet Aging Report: Production Lines', email_body)


if __name__ == '__main__':
    main()
