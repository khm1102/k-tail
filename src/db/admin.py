import hashlib
import datetime
from .conn import db_connect

conn = db_connect()
cur = conn.cursor()

"""
Admin 테이블 생성
"""
create_admin = """
Create Table IF NOT Exists Admin(
    id Integer Primary Key AUTOINCREMENT,
    name Text NOT NULL UNIQUE,
    passwd Text NOT NULL,
    role Text Default 'root',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""
cur.execute(create_admin)

"""
Admin 전체 조회
"""
def select_admin() -> list:
    select_admin = """
    select * from admin;
    """
    cur.execute(select_admin)
    result = cur.fetchall()
    return result

"""
Admin 추가
"""
def add_admin(name: str, passwd: str, role: str = "root"):
    hashed = hashlib.sha256(passwd.encode('utf-8')).hexdigest()
    now = datetime.datetime.utcnow().isoformat(sep=' ')
    insert_admin = """
        Insert into Admin (name, passwd, role, created_at, updated_at)
        Values (?, ?, ?, ?, ?)
    """
    cur.execute(insert_admin, (name, hashed, role, now, now))
    conn.commit()


"""
Admin 삭제
"""
def delete_admin(name: str):
    delete_admin = """
        Delete From Admin where name = ?
    """
    cur.execute(delete_admin, (name,))
    conn.commit()

"""
Admin 인증(로그인) 확인 함수
"""
def verify_admin(name: str, passwd: str) -> bool:
    """
    주어진 이름과 비밀번호가 Admin 테이블에 존재하는지 확인합니다.
    비밀번호는 sha256 해시로 비교합니다.
    """
    hashed = hashlib.sha256(passwd.encode('utf-8')).hexdigest()
    query = """
        SELECT * FROM Admin WHERE name = ? AND passwd = ?
    """
    cur.execute(query, (name, hashed))
    result = cur.fetchone()
    return result is not None
