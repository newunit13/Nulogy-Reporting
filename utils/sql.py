import pyodbc 
from typing import List


def query(query: str) -> List[tuple]:
    conn_str = (
        r'Driver={ODBC Driver 17 for SQL Server};'
        r'Server=B4BSQL.accutec.ad;'
        r'Database=DynamicsAX_Prod;'
        r'Trusted_Connection=yes;'
        )
    cnxn = pyodbc.connect(conn_str)
    cursor = cnxn.cursor()

    cursor.execute(query)

    result = cursor.fetchall()
    cnxn.close()

    return result