import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("articles")

@mcp.tool()
def read_json(
    file_path: str,
    article_id: str | int | None = None
) -> list[dict] | dict:
    """
    Read articles from a JSON file.

    Args:
        file_path: Path to the JSON file.
        article_id: Optional article id.
            If omitted, return id and title for all articles.
            If provided, return the full article with this id.

    Returns:
        List of article metadata or one full article.
    """
    
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    path = PROJECT_ROOT / file_path

    with open(path, "r", encoding="utf-8") as f:
        articles = json.load(f)

    if article_id is None:
        return [
            {
                "id": str(article["id"]),
                "title": article["title"]
            }
            for article in articles
        ]

    for article in articles:
        if article["id"] == str(article_id):
            return article

    raise ValueError(f"Article with id={article_id} not found")

@mcp.tool()
def save_result(file_path: str, article_summary: dict | list[dict]) -> str:
    """
    Save data with summarized articles to json.
    Args:
        file_path: path to save json
        data: list of dicts of summarized articles
    Return:
        Instruction for LLM to save json.
    """
    
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    file_path = PROJECT_ROOT / file_path
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding='utf-8') as f:
            data = json.load(f)
        data.append(article_summary)
    else:
        data = [article_summary]
    
    with open(file_path, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    return {
        "saved_id": article_summary["id"],
        "status": "saved",
        "instruction": "Continue with the next unprocessed article id."
    }

if __name__ == "__main__":
    mcp.run()