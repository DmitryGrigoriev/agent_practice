from tools import read_json
from langchain.agents import create_agent

from langchain_mistralai import ChatMistralAI

import os
from dotenv import load_dotenv

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
        tools=[read_json]
    )
    
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Прочитай файл data/articles.json и скажи, сколько в нем статей?"
                }
            ]
        }
    )
    
    return result
    

if __name__ == "__main__":
    print(main())