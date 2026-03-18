import sys
sys.path.append(".")

from app.tools.schema import get_schema
from app.tools.db import execute_query
from app.agent.nodes import (
    extract_schema,
    generate_sql,
    execute_sql,
    reflect_and_refine,
    format_answer,
)

print("Testing each agent node...")
print("-" * 50)

# Base state
state = {
    "question":     "Show me all sale transactions",
    "schema":       "",
    "sql_v1":       "",
    "sql_current":  "",
    "df_result":    None,
    "error":        None,
    "feedback":     "",
    "retries":      0,
    "final_answer": "",
}

# Node 1: extract_schema 
state = extract_schema(state)
assert state["schema"], "schema is empty"
print("Node 1 extract_schema  →", state["schema"].splitlines()[0])

# Node 2: generate_sql 
state = generate_sql(state)
assert state["sql_v1"], "sql_v1 is empty"
print("Node 2 generate_sql    →", state["sql_v1"][:60])

# Node 3: execute_sql 
state = execute_sql(state)
print("Node 3 execute_sql     →",
      f"{len(state['df_result'])} rows" if state["df_result"] is not None else f"error: {state['error']}")

# Node 4: reflect_and_refine 
state = reflect_and_refine(state)
assert state["feedback"], "feedback is empty"
print("Node 4 reflect_and_refine →", state["feedback"][:60])
print("            refined SQL  →", state["sql_current"][:60])

# Node 5: format_answer 
state = execute_sql(state)   
state = format_answer(state)
assert state["final_answer"], "final_answer is empty"
print("Node 5 format_answer   →", state["final_answer"][:60])

print("-" * 50)
print("All nodes working!")