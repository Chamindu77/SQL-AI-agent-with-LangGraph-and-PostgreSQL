from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
 
load_dotenv()
 
print("Testing PostgreSQL connection...")
 
engine = create_engine(os.getenv("DATABASE_URL"))
 
with engine.connect() as conn:
    result = conn.execute(text("SELECT version()"))
    version = result.fetchone()[0]
 
print("PostgreSQL connected!")
print(f"   Version : {version}")
print(f"   URL     : {os.getenv('DATABASE_URL')}")
 