import os
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI

from tools import read_json, summarize_article

load_dotenv()
if "MISTRAL_API_KEY" not in os.environ:
    os.environ['MISTRAL_API_KEY'] = os.getenv("MISTRAL_API_KEY")

def main():
    
    llm = ChatMistralAI(
        model="mistral-small-latest",
        temperature=0,
    )
        
    agent = create_agent(
        model=llm,
        tools=[
            read_json,
            summarize_article
        ]
    )
    
    #result = agent.invoke(
    #    {
    #        "messages": [
    #            {
    #                "role": "user",
    #                "content": "Прочитай файл data/articles.json и кратко суммаризируй статью с id=1"
    #            }
    #        ]
    #    }
    #)
    
    for step in agent.stream(
        {
            "messages":
                [
                    {
                        "role": "user",
                        "content": (
                                    "Прочитай файл data/articles.json. "
                                    "Для каждой статьи вызови summarize_article. "
                                    "Суммаризируй все 10 статей. "
                )
                    }
                ]
        },
        stream='updates'
    ):
        print(step)
    
    #or message in result["messages"]:
    #   print(type(message).__name__)

    #   if hasattr(message, "tool_calls"):
    #       print(message.tool_calls)

    #   print(message.content)
    #   print("-" * 50)
    

if __name__ == "__main__":
    main()