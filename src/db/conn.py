from sqlite3 import connect
from os import path

DB_PATH = path.join(path.dirname(path.abspath(__file__)), "dev.db")

def db_connect():
    return connect(DB_PATH)
