import sys; sys.path.append(".")
from sqlalchemy import create_engine, text
from app.config import settings

engine = create_engine(settings.database_url)

with engine.connect() as conn:
    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS transactions (
        id SERIAL PRIMARY KEY,
        product_name TEXT,
        category TEXT,
        color TEXT,
        action TEXT,
        qty_delta INTEGER,
        unit_price NUMERIC,
        ts TIMESTAMP DEFAULT NOW()
    )"""))

    conn.execute(text("""
    INSERT INTO transactions (product_name, category, color, action, qty_delta, unit_price)
    VALUES
      ('Widget A', 'Electronics', 'Blue',  'sale',    -10, 29.99),
      ('Widget B', 'Clothing',    'Red',   'sale',    -5,  49.99),
      ('Widget A', 'Electronics', 'Blue',  'restock',  50, NULL),
      ('Widget C', 'Clothing',    'Green', 'sale',    -20, 19.99)
    """))
    conn.commit()

print("Database seeded.")