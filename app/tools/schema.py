from sqlalchemy import create_engine, inspect
from app.config import settings

engine = create_engine(settings.database_url)

def get_schema() -> str:
    inspector = inspect(engine)
    lines = []
    for table in inspector.get_table_names():
        lines.append(f"Table: {table}")
        for col in inspector.get_columns(table):
            lines.append(f"  {col['name']} ({col['type']})")
        lines.append("")
    return "\n".join(lines)