import json
import os
from dotenv import load_dotenv


from langchain.tools import tool
from langchain_mistralai import ChatMistralAI

load_dotenv()
if "MISTRAL_API_KEY" not in os.environ:
    os.environ['MISTRAL_API_KEY'] = os.getenv("MISTRAL_API_KEY")

@tool
def read_json(file_path: str) -> list[dict]:
    """
    Read articles from json path.
    Args:
        file_path: path to json file
    Returns:
        List of articles dict
    """
    with open(file_path, "r", encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, dict):
        raise "Unknown format. Should be dict"
    
    return data


@tool
def summarize_article(text: str) -> str:
    """
    Create a short summary of one article.
    Args:
        text: text of an article.
    Return:
        Summarized text of an article.
    """
    
    summarize_llm = ChatMistralAI(
        model="mistral-small-latest",
        temperature=0
    )
    
    response = summarize_llm.invoke(
        f"Сделай краткую суммаризацию следующую текста:\n\n{text}"
    )
    
    return response.content