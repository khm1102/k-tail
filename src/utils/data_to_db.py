"""
정제된 csv 데이터를 db에 저장합니다.
"""

from src.db.conn import db_connect
import pandas as pd

def load_csv_to_sqlite(csv_path: str):
    df = pd.read_csv(csv_path, encoding='utf-8')
    df.columns = [col.strip() for col in df.columns]

    conn = db_connect()
    cursor = conn.cursor()


    for _, row in df.iterrows():
        name = row.get('Cocktail Name')
        ingredients = row.get('Ingredients')
        garnish = row.get('Garnish')
        glassware = row.get('Glassware')
        preparation = row.get('Preparation')
        price = row.get('Price')
        note = row.get('Notes')

        name_txt        = name.strip()        if isinstance(name, str)        else None
        ingredients_txt = ingredients.strip() if isinstance(ingredients, str) else None
        garnish_txt     = garnish.strip()     if isinstance(garnish, str)     else None
        glassware_txt   = glassware.strip()   if isinstance(glassware, str)   else None
        prep_txt        = preparation.strip() if isinstance(preparation, str)  else None
        note_txt        = note.strip()        if isinstance(note, str)        else None
        price_val       = float(price)        if pd.notna(price)               else None

        cursor.execute("""
        INSERT OR REPLACE INTO Cocktail
          (name, ingredients, garnish, glassware, preparation, price, note)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            name_txt,
            ingredients_txt,
            garnish_txt,
            glassware_txt,
            prep_txt,
            price_val,
            note_txt
        ))

    conn.commit()
    conn.close()
    print(f"{len(df)} 저장.")



load_csv_to_sqlite("cocktails.csv")
