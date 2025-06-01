
import os
import requests
from datetime import datetime

from langchain.tools import tool
from utils.utils import format_conversation_for_agent

@tool
def share_gist_tool(input: str) -> str:
    """
    GitHub Gist 생성. 입력 형식: 파일명;내용;설명
    """
    try:
        token = os.getenv("GITHUB_TOKEN", "")
        if not token:
            return "❌ GITHUB_TOKEN 환경 변수가 설정되지 않았습니다."

        if ';' in input and input.count(';') >= 2:
            parts = input.split(';', 2)
            filename = parts[0].strip()
            content = parts[1].strip()
            description = parts[2].strip()
        else:
            plan = format_conversation_for_agent()
            if not plan:
                return "❌ 저장할 여행 계획을 찾을 수 없습니다."
            filename = f"travel_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            content = plan
            description = "AI로 생성된 여행 계획"

        payload = {
            "description": description,
            "public": True,
            "files": {filename: {"content": content}}
        }

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

        res = requests.post("https://api.github.com/gists", json=payload, headers=headers, timeout=30)
        if res.status_code in (200, 201):
            gist_data = res.json()
            gist_url = gist_data.get("html_url", "")
            return f"✅ Gist 생성 완료!\n🔗 URL: {gist_url}\n📄 파일명: {filename}\n📊 크기: {len(content)}문자"
        else:
            return f"❌ Gist 생성 실패 (status {res.status_code}): {res.text[:200]}"

    except Exception as e:
        return f"❌ Gist 생성 중 오류 발생: {e}"

@tool
def share_travel_plan_gist(input: str = "") -> str:
    """
    현재 여행 계획을 자동으로 Gist에 저장합니다.
    """
    plan = format_conversation_for_agent()
    if not plan:
        return "❌ 저장할 여행 계획을 찾을 수 없습니다. 먼저 여행 계획을 생성해주세요."
    filename = f"travel_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    description = "AI 여행 플래너로 생성된 여행 계획"
    gist_input = f"{filename};{plan};{description}"
    return share_gist_tool(gist_input)

@tool
def debug_share_status(input: str = "") -> str:
    """
    공유 기능 디버깅용 정보 출력
    """
    debug_info = []
    token = os.getenv("GITHUB_TOKEN", "")
    debug_info.append(f"GitHub Token: {'설정됨' if token else '❌ 미설정'}")

    plan = format_conversation_for_agent()
    debug_info.append(f"여행 계획: {'발견됨' if plan else '❌ 없음'}")

    # 간단하게 '공유해줘' 인텐트 확인
    from intents.intent_detector import detect_intent
    intent = detect_intent("공유해줘")
    debug_info.append(f"'공유해줘' 인텐트: {intent}")

    env_vars = ["GITHUB_TOKEN", "GOOGLE_APPLICATION_CREDENTIALS", "CALENDAR_ID", "SERPER_API_KEY"]
    for var in env_vars:
        value = os.getenv(var, "")
        debug_info.append(f"{var}: {'설정됨' if value else '❌ 미설정'}")

    return "\n".join(debug_info)