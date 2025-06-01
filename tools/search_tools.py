import os
import requests

from langchain.tools import tool
from utils.utils import sanitize_input

@tool
def search_place(query: str) -> str:
    """
    Google Serper API를 이용한 장소 검색
    """
    headers = {"X-API-KEY": os.getenv("SERPER_API_KEY", "")}
    params = {"q": sanitize_input(query), "gl": "kr", "hl": "ko"}
    try:
        res = requests.post(
            "https://google.serper.dev/search",
            headers=headers,
            json=params
        )
        res.raise_for_status()
        results = res.json().get("organic", [])[:3]
        return "\n".join([
            f"• {item['title']} ({item.get('snippet','')}) – {item['link']}"
            for item in results
        ])
    except Exception as e:
        return f"⚠️ 검색 오류: {str(e)}"