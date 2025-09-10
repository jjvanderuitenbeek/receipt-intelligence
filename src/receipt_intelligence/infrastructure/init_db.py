import sqlite3
from pathlib import Path
import sys

#python src\receipt_intelligence\infrastructure\init_db.py
#print(Path().resolve())

DB_PATH = Path("data/cleaned/receipts.db")

def init_db():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS receiptTable")

    cursor.execute('''
        CREATE TABLE receiptTable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
                   
            submitted_by TEXT NOT NULL,
            filename TEXT NOT NULL,
            receipt_date DATE NOT NULL,
            store_cod TEXT NOT NULL,
                    
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price_unit REAL NOT NULL,
            price_total REAL NOT NULL,       
            discount_ind TEXT NOT NULL,
                   
            load_date DATE NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()

