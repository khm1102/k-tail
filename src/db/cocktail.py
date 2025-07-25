from .conn import db_connect

conn = db_connect()
cur = conn.cursor()

"""
Create Cocktail Table
"""

def cockail_create():
  query = """
  CREATE TABLE IF NOT EXISTS Cocktail (
    name TEXT PRIMARY KEY,
    ingredients TEXT NOT NULL,
    garnish TEXT,
    glassware TEXT,
    preparation TEXT,
    price REAL NOT NULL,
    note TEXT
);
"""
  
  cur.execute(query)



"""
Cocktail Select

칵테일 테이블의 전체 조회
"""

def cocktail_select():
    query = """
    select * from Cocktail;
    """
    cur.execute(query)
    result = cur.fetchall()
    return result


"""
Coctail Insert

칵테일 
"""

def coctail_insert(name, ingredients, garnish=None, glassware=None, preparation=None, price=0.0, note=None):
    query = """
    INSERT INTO Cocktail (name, ingredients, garnish, glassware, preparation, price, note)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cur.execute(query, (name, ingredients, garnish, glassware, preparation, price, note))
    conn.commit()
    return True


"""
Coctail Update

칵테일 정보 수정 함수
"""

def coctail_update(name, **kwargs):
    """
    칵테일 정보 수정 함수
    name(필수) 외에 수정할 필드만 키워드 인자로 넘기면 됨.
    예시: coctail_update("Mojito", price=15.0, note="신메뉴")
    """
    allowed_fields = ["ingredients", "garnish", "glassware", "preparation", "price", "note"]
    fields = []
    values = []
    for key in allowed_fields:
        if key in kwargs and kwargs[key] is not None:
            fields.append(f"{key} = ?")
            values.append(kwargs[key])
    if not fields:
        return False
    query = f"UPDATE Cocktail SET {', '.join(fields)} WHERE name = ?"
    values.append(name)
    cur.execute(query, values)
    conn.commit()
    return True


"""
Coctail Delete

칵테일 삭제 함수
name(필수): 삭제할 칵테일 이름
"""

def coctail_delete(name):
    """
    주어진 이름의 칵테일을 Cocktail 테이블에서 삭제합니다.
    """
    query = "DELETE FROM Cocktail WHERE name = ?"
    cur.execute(query, (name,))
    conn.commit()
    return True
