import sys
import sqlite3 as lite
import logging as log

sqlite3_db = 'db/piehome.db'


def get_connection():
    """
    get connection to sqlite3 database

    :return: sqlite3 Conneciton
    """
    con = lite.connect(sqlite3_db)
    con.row_factory = lite.Row
    return con


def initialize_database():
    log.info("initializing database tables")
    con = get_connection()
    try:
        with con:
            cur = con.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS 'device'(identifier TEXT PRIMARY KEY NOT NULL, "
                "name TEXT NOT NULL, controller TEXT NOT NULL, controller_device_id TEXT NOT NULL );")
            cur.execute(
                "CREATE TABLE IF NOT EXISTS 'device_capabilty'(device_identifier TEXT NOT NULL, "
                "capability INT NOT NULL );")
            cur.execute(
                "CREATE TABLE IF NOT EXISTS 'device_attribute'(device_identifier TEXT NOT NULL, "
                "attribute_key TEXT NOT NULL, attribute_value TEXT NOT NULL );")
            log.info("database tables initialization complete")
    except Exception as e:
        log.exception(e)
