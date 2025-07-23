import sqlite3

# 환경변수로 DB_PATH 하나만 관리하면 되서, 따로 conf로 빼지는 않음
DB_PATH = "./src/db/dev.db"


def db_connect():
    return sqlite3.connect(DB_PATH)

