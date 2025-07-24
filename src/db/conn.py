import sqlite3

DB_PATH = "dev.db"


def db_connect():
    return sqlite3.connect(DB_PATH)

