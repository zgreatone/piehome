import sys
import sqlite3 as lite

sqlite3_db = 'db/app.db'

def get_connection():
    """
    get connection to sqlite3 database

    :return: sqlite3 Conneciton
    """
    con = lite.connect(sqlite3_db)
    con.row_factory = lite.Row
    return con