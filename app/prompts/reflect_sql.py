REFLECT_SQL_PROMPT = """
You are a SQL reviewer. A SQL query was executed and returned the output below.
Evaluate whether the output correctly answers the user's question.
If not, provide a fixed SQL query.

User question: {question}

Original SQL:
{sql}

Query output:
{output}

Error (if any): {error}

Schema:
{schema}

Return STRICT JSON:
{{
  "feedback": "<1-3 sentences: what was wrong or confirm correctness>",
  "refined_sql": "<corrected SQL or the original if already correct>",
  "is_correct": true or false
}}
"""