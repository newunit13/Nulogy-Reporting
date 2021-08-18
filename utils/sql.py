import pyodbc 
from typing import List
from utils.config import DAX_DB_CONNECTION_STRING, AZURE_DB_CONNECTION_STRING


def query(query: str, azure: bool=False) -> List[tuple]:

    cnxn = pyodbc.connect(DAX_DB_CONNECTION_STRING) if not azure else pyodbc.connect(AZURE_DB_CONNECTION_STRING)
    cursor = cnxn.cursor()

    cursor.execute(query)

    result = cursor.fetchall()
    cnxn.close()

    return result
