import sys
sys.path.append(".")

from app.agent.graph import sql_agent

def ask(question: str):
    print(f"\n Question: {question}\n")
    result = sql_agent.invoke({"question": question})

    print("─" * 60)
    print(f" SQL V1:\n{result['sql_v1']}\n")
    print(f" Reflection feedback:\n{result['feedback']}\n")
    print(f" Final SQL:\n{result['sql_current']}\n")
    print(f" Answer:\n{result['final_answer']}")
    print("─" * 60)

if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "Which product has the highest total sales?"
    ask(question)