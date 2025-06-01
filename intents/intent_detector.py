import re
import streamlit as st

INTENT_KEYWORDS = {
    "PLAN_TRIP": {
        "primary": ["계획 짜", "일정 짜", "여행 추천", "코스 추천"],
        "secondary": ["여행지", "코스", "루트"]
    },
    "BOOK_CALENDAR": {
        "primary": ["캘린더 예약", "일정 등록", "캘린더에 추가", "스케줄 등록"],
        "secondary": ["캘린더", "예약", "등록해줘"]
    },
    "SHARE_PLAN": {
        "primary": ["공유해줘", "gist 만들어줘", "저장해줘", "링크 생성"],
        "secondary": ["공유", "gist", "저장", "링크"]
    },
    "SEARCH_PLACE": {
        "primary": ["검색해줘", "찾아줘", "알려줘"],
        "secondary": ["검색", "찾아", "맛집", "관광지"]
    },
    "MANAGE_EVENT": {
        "primary": ["일정 목록", "캘린더 확인", "일정 조회"],
        "secondary": ["수정", "삭제", "변경", "확인"]
    }
}

def detect_intent(user_input: str) -> str:
    """
    인텐트 감지 (가중치 및 우선순위 적용)
    """
    user_input_lower = user_input.lower()
    intent_scores = {}

    for intent, keyword_groups in INTENT_KEYWORDS.items():
        score = 0
        # Primary 키워드 (가중치 3)
        for keyword in keyword_groups["primary"]:
            if keyword in user_input_lower:
                score += 3
        # Secondary 키워드 (가중치 1)
        for keyword in keyword_groups["secondary"]:
            if keyword in user_input_lower:
                score += 1
        if score > 0:
            intent_scores[intent] = score

    # 특별 규칙: "공유"가 포함되면 SHARE_PLAN 우선
    if "공유" in user_input_lower:
        intent_scores["SHARE_PLAN"] = intent_scores.get("SHARE_PLAN", 0) + 5

    if not intent_scores:
        return "OTHER"

    best_intent = max(intent_scores, key=intent_scores.get)
    debug_info = f"인텐트 점수: {intent_scores} → 선택: {best_intent}"
    st.write(f"🔍 {debug_info}")
    return best_intent

def filter_tools_by_intent(intent: str, all_tools: list) -> list:
    """
    인텐트에 따라 사용 가능한 도구(툴) 필터링
    """
    tool_mapping = {
        "PLAN_TRIP": ["search_place", "plan_trip_tool"],
        "BOOK_CALENDAR": ["create_calendar_from_plan", "create_event_tool", "check_event_exists"],
        "SHARE_PLAN": ["share_travel_plan_gist", "share_gist_tool", "debug_share_status"],
        "SEARCH_PLACE": ["search_place"],
        "MANAGE_EVENT": ["list_events_tool", "update_event_tool", "delete_event_tool", "check_event_exists"],
        "OTHER": all_tools
    }

    allowed_tool_names = tool_mapping.get(intent, [])
    if intent == "OTHER":
        return all_tools

    filtered_tools = []
    for tool in all_tools:
        # Tool 객체인지, 함수인지에 따라 이름 비교
        name = getattr(tool, "name", None) or getattr(tool, "__name__", "")
        if name in allowed_tool_names:
            filtered_tools.append(tool)

    return filtered_tools