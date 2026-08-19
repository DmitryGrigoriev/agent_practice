import json

from langchain.tools import tool

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