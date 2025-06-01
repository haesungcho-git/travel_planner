from datetime import datetime
from langchain.tools import tool
from config import llm
from utils.utils import (
    parse_korean_date,
    extract_date_from_input,
    format_conversation_for_agent
)
from tools.calendar_tools import create_event_tool, check_event_exists

@tool
def plan_trip_tool(input: str) -> str:
    """
    여행 계획표를 생성합니다.
    """
    user_specified_date = extract_date_from_input(input)
    today_str = datetime.now().strftime('%Y-%m-%d')
    prompt_plan = f"""
여행 계획 요청: {input}

**중요: 날짜 설정 규칙**
- 사용자가 "25년 6월 20일"이라고 했다면 반드시 "2025-06-20"으로 해석
- 현재 날짜: {today_str}
- 사용자 지정 시작 날짜: {user_specified_date or "명시되지 않음"}

아래 형식에 따라 한국어로 상세한 여행 일정표를 만들어 주세요:
- 날짜별로 일정 구분 (Day1, Day2, ...)
- 각 일정마다 정확한 시간, 장소, 활동 포함
- 각 이벤트 별로 한 줄씩 표현해주세요
- ISO 8601 형식의 날짜/시간 사용 (예: 2025-06-20T11:00:00+09:00)

출력 예시:
Day1 (2025-06-20):
 - 09:00~10:00 : 서울역 도착 및 호텔 체크인
 - 11:00~12:30 : 경복궁 방문
 - 13:00~14:00 : 점심 (인사동 전통 음식)
 - 15:00~17:00 : 북촌 한옥마을 산책

Day2 (2025-06-21):
 - 09:00~10:00 : 남산타워 관람
 - 11:00~12:00 : 명동 쇼핑
 - 13:00~14:00 : 점심 (명동 떡볶이)
 - 15:00~17:00 : 이태원 구경

**응답은 반드시 일반 텍스트로만 제공하세요. JSON이나 특수 구조는 사용하지 마세요.**
"""
    try:
        response = llm.invoke(prompt_plan)
        content = response.content if hasattr(response, 'content') else str(response)
        if user_specified_date:
            content = f"📅 시작 날짜: {user_specified_date}\n\n{content}"
        return content
    except Exception as e:
        return f"❌ 여행 계획 생성 실패: {e}"

@tool
def create_calendar_from_plan(input: str = "") -> str:
    """
    이전 여행 계획을 기반으로 캘린더에 자동 예약합니다.
    """
    user_specified_date = extract_date_from_input(input)
    plan = format_conversation_for_agent()
    if not plan:
        return "❌ 먼저 여행 계획을 생성해주세요. 예: '서울 2박 3일 여행 계획 짜줘'"

    today_str = datetime.now().strftime('%Y-%m-%d')
    prompt_parse = f"""
다음 여행 계획을 분석하여 각 일정을 캘린더 이벤트로 변환해주세요:

{plan}

**중요: 날짜 변환 규칙**
- 현재 날짜: {today_str}
- 사용자가 지정한 시작 날짜: {user_specified_date or "계획에서 추출"}
- "25년" = "2025년"으로 해석
- 사용자가 "{input}"라고 했다면, 명시된 날짜를 정확히 사용
- 모든 날짜는 정확히 YYYY-MM-DD 형식으로 변환
- 시간대는 반드시 +09:00 (한국 시간) 사용

각 일정마다 다음 형식으로 출력하세요:
제목;시작시간;종료시간

예시:
경복궁 방문;2025-06-20T11:00:00+09:00;2025-06-20T12:30:00+09:00
인사동 점심;2025-06-20T13:00:00+09:00;2025-06-20T14:00:00+09:00

각 줄마다 하나의 이벤트만 작성하고, 다른 설명은 포함하지 마세요.
날짜가 불명확한 경우 {user_specified_date or "2025-06-20"}부터 시작하세요.

**응답은 반드시 일반 텍스트로만 제공하세요. JSON이나 특수 구조는 사용하지 마세요.**
"""
    try:
        response = llm.invoke(prompt_parse)
        content = response.content if hasattr(response, 'content') else str(response)

        if user_specified_date and user_specified_date not in content:
            # Streamlit UI에서는 경고로 처리하지만, 여기서는 문자열로만 반환
            content = f"⚠️ 사용자 지정 날짜({user_specified_date})가 반영되지 않았습니다.\n\n{content}"

        events_created = []
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if ';' in line and line.count(';') >= 2:
                try:
                    result = create_event_tool(line)
                    events_created.append(result)
                except Exception as e:
                    events_created.append(f"❌ 이벤트 생성 실패: {line} - {e}")

        if events_created:
            success_msg = f"🗓️ 캘린더 예약 완료 (시작일: {user_specified_date or '계획 기준'}):\n"
            return success_msg + "\n".join(events_created)
        else:
            return f"❌ 캘린더 이벤트 생성에 실패했습니다.\n파싱 결과: {content}"
    except Exception as e:
        return f"❌ 일정 파싱 실패: {e}"