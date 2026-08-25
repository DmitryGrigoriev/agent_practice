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
            return {
            "id": str(article["id"]),
            "title": article["title"],
            "text": article["text"],
            "status": "article_loaded",
            "next_action": "summarize_article",
        }

    raise ValueError(f"Article with id={article_id} not found")

@mcp.tool()
def save_result(
    file_path: str,
    article_summary: dict | list[dict],
) -> dict:
    """
    Save one summarized article to a JSON file.

    Args:
        file_path: Path to the output JSON file.
        article_summary: Summary of one article as a dict
            or as a one-item list containing a dict.

    Returns:
        Result of saving and instruction for the agent to continue.
    """

    project_root = Path(__file__).resolve().parent.parent
    output_path = project_root / file_path

    if isinstance(article_summary, list):
        if len(article_summary) != 1:
            raise ValueError("Expected exactly one article summary")
        article_summary = article_summary[0]

    if output_path.exists():
        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(
        {
            "id": article_summary["id"],
            "title": article_summary["title"],
            "summary": article_summary["summary"]
        }
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return {
        "saved_id": article_summary["id"],
        "status": "saved",
        "instruction": "Continue with the next unprocessed article id.",
    }

if __name__ == "__main__":
    mcp.run()