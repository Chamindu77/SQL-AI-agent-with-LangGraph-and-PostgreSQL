from app.agent.state import AgentState
from app.config import settings

def should_reflect(state: AgentState) -> str:
    """
    After execution: if there's an error OR it's the first run, reflect.
    If retries exhausted, go straight to format.
    """
    error = state.get("error")
    retries = state.get("retries", 0)

    if retries >= settings.max_reflection_retries:
        return "format_answer"   

    if error:
        return "reflect_and_refine"   

    # First pass (retries == 0) — always reflect once to validate output
    if retries == 0:
        return "reflect_and_refine"

    return "format_answer"

def after_reflection(state: AgentState) -> str:
    """After reflecting, always re-execute the refined SQL."""
    return "execute_sql"