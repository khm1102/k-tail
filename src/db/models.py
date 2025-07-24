import sqlite3
import hashlib
import datetime
from conn import db_connect

conn = db_connect()
cur = conn.cursor()

"""
Create Admin Table
"""

create_admin = """
Create Table IF NOT Exists Admin(
    id Integer Primary Key AUTOINCREMENT,
    name Text NOT NULL UNIQUE ,
    passwd Text NOT NULL,
    role Text Default 'root',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


cur.execute(create_admin)

"""
Select Admin
"""

def select_admin() -> list:
    select_admin = """
    select * from admin;
    """
    cur.execute(select_admin)
    result = cur.fetchall()
    return result



"""
Insert Admin (add)
"""

def add_admin(name: str, passwd: str, role: str = "root"):
    hashed = hashlib.sha256(passwd.encode('utf-8')).hexdigest()
    now = datetime.datetime.utcnow().isoformat(sep=' ')
    
    insert_admin = """
        Insert into Admin (user, passwd, role, created_at, updated_at)
        Values (?, ?, ?, ?, ?)
    """
    
    cur.execute(insert_admin, (name, hashed, role, now, now))
    conn.commit()
    
"""
Delete Admin
"""

def delete_admin(name: str):
    delete_admin = """
        Delete From Admin where name = ?
    """
    
    cur.execute(delete_admin, (name,))
    conn.commit()


conn.close()