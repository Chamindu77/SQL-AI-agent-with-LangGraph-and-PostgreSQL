import sys
sys.path.append(".")

from app.agent.graph import sql_agent
from app.agent.edges import should_reflect, after_reflection

print("Testing LangGraph graph...")
print("-" * 50)

# Test 1: edge — first pass should reflect
state_first_pass = {"error": None, "retries": 0, "df_result": None}
edge = should_reflect(state_first_pass)
assert edge == "reflect_and_refine", f"Expected reflect_and_refine, got {edge}"
print("Edge — first pass      → reflect_and_refine")

# Test 2: edge — error should reflect 
state_with_error = {"error": "syntax error", "retries": 1, "df_result": None}
edge = should_reflect(state_with_error)
assert edge == "reflect_and_refine", f"Expected reflect_and_refine, got {edge}"
print("Edge — error present   → reflect_and_refine")

# Test 3: edge — after reflection re-executes 
state_after_reflect = {"retries": 1, "sql_current": "SELECT 1"}
edge = after_reflection(state_after_reflect)
assert edge == "execute_sql", f"Expected execute_sql, got {edge}"
print("Edge — after reflect   → execute_sql")

# Test 4: edge — max retries reached → format
from app.config import settings
state_max = {"error": "still failing", "retries": settings.max_reflection_retries, "df_result": None}
edge = should_reflect(state_max)
assert edge == "format_answer", f"Expected format_answer, got {edge}"
print(f"Edge — max retries ({settings.max_reflection_retries})  → format_answer")

# Test 5: full graph invoke
print("\nRunning full graph invoke (this calls LLM + DB)...")
result = sql_agent.invoke({"question": "Show me all sale transactions"})

assert result["sql_v1"],       "sql_v1 missing"
assert result["sql_current"],  "sql_current missing"
assert result["feedback"],     "feedback missing"
assert result["final_answer"], "final_answer missing"
assert result["retries"] >= 1, "reflection never ran"

print("Graph invoke complete!")
print(f"   SQL V1      : {result['sql_v1'][:60]}")
print(f"   Feedback    : {result['feedback'][:60]}")
print(f"   Final SQL   : {result['sql_current'][:60]}")
print(f"   Retries     : {result['retries']}")
print(f"   Answer      : {result['final_answer'][:60]}")

print("-" * 50)
print("Graph fully working!")