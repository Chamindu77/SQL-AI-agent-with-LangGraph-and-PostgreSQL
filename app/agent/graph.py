from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import (
    extract_schema,
    generate_sql,
    execute_sql,
    reflect_and_refine,
    format_answer,
)
from app.agent.edges import should_reflect, after_reflection

def build_graph():
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("extract_schema",    extract_schema)
    graph.add_node("generate_sql",      generate_sql)
    graph.add_node("execute_sql",       execute_sql)
    graph.add_node("reflect_and_refine", reflect_and_refine)
    graph.add_node("format_answer",     format_answer)

    # Entry point
    graph.set_entry_point("extract_schema")

    # Linear edges
    graph.add_edge("extract_schema",    "generate_sql")
    graph.add_edge("generate_sql",      "execute_sql")

    # Conditional edges
    graph.add_conditional_edges(
        "execute_sql",
        should_reflect,
        {
            "reflect_and_refine": "reflect_and_refine",
            "format_answer":      "format_answer",
        }
    )

    # After reflection always re-execute
    graph.add_conditional_edges(
        "reflect_and_refine",
        after_reflection,
        {"execute_sql": "execute_sql"}
    )

    graph.add_edge("format_answer", END)

    return graph.compile()

sql_agent = build_graph()