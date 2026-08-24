import json
import os
import time

from dotenv import load_dotenv
from langchain.tools import tool
from langchain_mistralai import ChatMistralAI

load_dotenv()
mistral_api_key = os.getenv("MISTRAL_API_KEY")

if not mistral_api_key:
    raise ValueError("API keys are not configured")
    
@tool
def summarize_article(id: str, title: str, text: str) -> dict:
    """
    Create a short summary of one article.
    Args:
        id: id of one article.
        title: title of one article.
        text: text of one article.
    Return:
        dict with id, title, summary of a text.
    """
    
    start = time.perf_counter()

    summarize_llm = ChatMistralAI(
        model="mistral-small-latest",
        api_key=mistral_api_key,
        temperature=0,
        max_tokens=100,
        timeout=120,
        max_retries=3
    )

    response = summarize_llm.invoke(
        f"""
        Сожми текст до 2 предложений и максимум 45 слов.

        Передай только:
        1. основную мысль;
        2. 1–2 самых важных факта.

        Большинство чисел, сроков, лимитов и технических деталей нужно отбросить.
        Не перечисляй несколько однотипных показателей.
        Не пытайся сохранить все важные детали исходника.
        Цель — сильное информационное сжатие, а не сокращённый пересказ.

        Текст:
        {text}
        """    
    )
    
    elapsed = time.perf_counter() - start
    
    print(f"SUMMARY id={id}: {elapsed:.2f} sec")

    return {
        "id": id,
        "title": title,
        "summary": response.content,
        "status": "summary_ready",
        "next_action": "save_result"
    }
