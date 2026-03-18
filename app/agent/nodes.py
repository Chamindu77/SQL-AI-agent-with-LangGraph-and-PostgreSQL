import json
# from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from app.agent.state import AgentState
from app.tools.schema import get_schema
from app.tools.db import execute_query
from app.prompts.generate_sql import GENERATE_SQL_PROMPT
from app.prompts.reflect_sql import REFLECT_SQL_PROMPT
# from app.config import settings
from langchain_openai import ChatOpenAI
from app.config import settings

# llm = ChatOpenAI(model=settings.llm_model, temperature=0)
llm = ChatOpenAI(
    model=settings.llm_model,
    temperature=0,
    openai_api_key=settings.openrouter_api_key,
    openai_api_base="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost",   
        "X-Title": "SQL AI Agent",          
    }
)



# ── Node 1: Extract schema ──────────────────────────────────────────
def extract_schema(state: AgentState) -> AgentState:
    state["schema"] = get_schema()
    state["retries"] = 0
    return state

# ── Node 2: Generate SQL (V1) ───────────────────────────────────────
def generate_sql(state: AgentState) -> AgentState:
    prompt = GENERATE_SQL_PROMPT.format(
        schema=state["schema"],
        question=state["question"],
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    sql = response.content.strip().strip("```sql").strip("```").strip()
    state["sql_v1"] = sql
    state["sql_current"] = sql
    return state

# ── Node 3: Execute SQL ─────────────────────────────────────────────
def execute_sql(state: AgentState) -> AgentState:
    df, error = execute_query(state["sql_current"])
    state["df_result"] = df
    state["error"] = error
    return state

# ── Node 4: Reflect and refine ──────────────────────────────────────
def reflect_and_refine(state: AgentState) -> AgentState:
    df = state.get("df_result")
    output_str = df.to_markdown(index=False) if df is not None else "No output"

    prompt = REFLECT_SQL_PROMPT.format(
        question=state["question"],
        sql=state["sql_current"],
        output=output_str,
        error=state.get("error") or "None",
        schema=state["schema"],
    )
    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        content = response.content.strip().strip("```json").strip("```")
        obj = json.loads(content)
        state["feedback"] = obj.get("feedback", "")
        state["sql_current"] = obj.get("refined_sql", state["sql_current"])
        state["retries"] = state.get("retries", 0) + 1
    except Exception as e:
        state["feedback"] = f"Parse error: {e}"

    return state

# ── Node 5: Format final answer ─────────────────────────────────────
def format_answer(state: AgentState) -> AgentState:
    df = state.get("df_result")
    if df is not None and not df.empty:
        state["final_answer"] = df.to_markdown(index=False)
    elif state.get("error"):
        state["final_answer"] = f"Could not answer: {state['error']}"
    else:
        state["final_answer"] = "No results found."
    return state