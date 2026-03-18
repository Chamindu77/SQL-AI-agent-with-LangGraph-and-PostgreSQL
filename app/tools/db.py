from sqlalchemy import create_engine, text
import pandas as pd
from app.config import settings

engine = create_engine(settings.database_url)

def execute_query(sql: str) -> tuple[pd.DataFrame | None, str | None]:
    """
    Execute a SQL query. Returns (dataframe, error_message).
    error_message is None on success.
    """
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)
        return df, None
    except Exception as e:
        return None, str(e)