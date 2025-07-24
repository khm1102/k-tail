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
"""

def coctail_update():
  return 0


"""
Coctail Delete
"""

def coctail_delete():
  return 0
