import asyncio
import os
from pathlib import Path
import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_mistralai import ChatMistralAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq

from .tools import summarize_article

load_dotenv()
mistral_api_key = os.getenv("MISTRAL_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

if not mistral_api_key or not groq_api_key:
    raise ValueError("API keys are not configured")

PROJECT_ROOT = Path(__file__).parent.parent
MCP_SERVER_PATH = PROJECT_ROOT / "src" / "mcp_server.py"
    

async def main():
    
    client = MultiServerMCPClient(
        {
            "articles": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [
                    str(MCP_SERVER_PATH)
                ]
            }
        }
    )
    
    mcp_tools = await client.get_tools()
    
    agent_llm = ChatGroq(
    model="qwen/qwen3.6-27b",
    api_key=groq_api_key,
    timeout=30,
    max_retries=3,
)
    
    summary_prompt = """
    Создай компактное состояние текущей агентной задачи.

    Обязательно сохрани:
    - исходную цель пользователя;
    - все id статей, которые нужно обработать;
    - id уже обработанных и сохранённых статей;
    - текущий id, если его обработка ещё не завершена;
    - id, которые ещё осталось обработать;
    - обязательную последовательность для каждой статьи:
    read_json -> summarize_article -> save_result;
    - если summarize_article уже был вызван для текущего id, но save_result ещё не был вызван,
    явно укажи, что следующим действием должен быть save_result;
    - агент не должен завершать работу, пока не обработаны все id.

    Не включай полные тексты статей и длинные summaries.
    Сохраняй только состояние, необходимое для продолжения работы.

    <messages>
    {messages}
    """
    
    prompt =    """
                Сначала вызови read_json без article_id из data/articles.json, чтобы получить только список id и title статей.

                Затем обработай все полученные id строго по одному.

                Для каждого id:
                1. вызови read_json с article_id для получения полного текста только этой статьи;
                2. сразу вызови summarize_article;
                3. после получения результата сразу вызови save_result. Результат сохрани в results/results.json;
                4. только после успешного сохранения переходи к следующему id.
                
                Не завершай работу, пока не обработаешь все id.
                Не запрашивай полные тексты нескольких статей одновременно.
                """
    
    
    summarize_llm = ChatMistralAI(
        model="mistral-small-latest",
        api_key=mistral_api_key,
        temperature=0,
        timeout=120,
        max_retries=3
    )
        
    agent = create_agent(
        model=agent_llm,
        tools=[
            *mcp_tools,
            summarize_article,
        ],
        middleware=[
            SummarizationMiddleware(
                model=summarize_llm,
                trigger=("tokens", 4000),
                keep=("messages", 8),
                summary_prompt=summary_prompt
            )
        ]
    )
    
    async for step in agent.astream(
        {"messages": [{"role": "user", "content": prompt}]}
    ):
        if "model" in step:
            message = step["model"]["messages"][-1]
            print("MODEL CONTENT:", message.content)
            print("TOOL CALLS:", message.tool_calls)


if __name__ == "__main__":
    asyncio.run(main())