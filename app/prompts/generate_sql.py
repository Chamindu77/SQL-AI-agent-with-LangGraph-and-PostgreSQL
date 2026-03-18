GENERATE_SQL_PROMPT = """
You are an expert SQL assistant for PostgreSQL.

Given the database schema and the user's question, write a SQL query that
correctly answers the question. Return ONLY the raw SQL, no explanation.

Schema:
{schema}

User question:
{question}
"""