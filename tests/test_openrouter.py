from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


llm = ChatOpenAI(
    model="z-ai/glm-4.5-air:free",
    openai_api_key="",
    openai_api_base="https://openrouter.ai/api/v1",
    default_headers={"HTTP-Referer": "http://localhost"}
)

response = llm.invoke([HumanMessage(content="Write SELECT 1 in SQL")])
print(response.content)