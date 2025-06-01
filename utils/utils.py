import re
import json
from datetime import datetime, timedelta
import streamlit as st
from langchain.schema import AIMessage, HumanMessage

# ========================================
# 1) 메모리 관리 함수
# ========================================
def safe_add_message_to_memory(memory, message):
    """메모리에 안전하게 메시지 추가"""
    try:
        memory.chat_memory.add_message(message)
    except AttributeError:
        try:
            if isinstance(message, HumanMessage):
                memory.chat_memory.add_user_message(message.content)
            elif isinstance(message, AIMessage):
                memory.chat_memory.add_ai_message(message.content)
        except AttributeError:
            try:
                memory.chat_memory.messages.append(message)
            except Exception as e:
                st.warning(f"메모리 추가 실패: {e}")

# ========================================
# 2) 파싱 오류 처리 함수
# ========================================
def extract_actual_response(response_text: str) -> str:
    """파싱 오류 메시지에서 실제 응답 내용을 추출합니다."""
    if not isinstance(response_text, str):
        return str(response_text)

    # 파싱 오류 패턴들
    parsing_error_patterns = [
        "Could not parse LLM output:",
        "Invalid or incomplete response",
        "OutputParserException:",
        "For troubleshooting, visit:"
    ]

    for pattern in parsing_error_patterns:
        if pattern in response_text:
            if "Could not parse LLM output:" in response_text:
                parts = response_text.split("Could not parse LLM output:")
                if len(parts) > 1:
                    actual_content = parts[1]
                    if "For troubleshooting" in actual_content:
                        actual_content = actual_content.split("For troubleshooting")[0]
                    return actual_content.strip()
            break

    # JSON 형식 응답 처리
    if response_text.strip().startswith('{'):
        try:
            parsed = json.loads(response_text)
            if "action_input" in parsed:
                return parsed["action_input"]
            elif "output" in parsed:
                return parsed["output"]
        except:
            pass

    return response_text

# ========================================
# 3) 대화 컨텍스트 포맷팅 함수
# ========================================
def format_conversation_for_agent():
    """대화에서 여행 계획 추출"""
    if "messages" not in st.session_state:
        return None
    
    travel_content = []
        
    # 최근 메시지부터 역순으로 검색
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "assistant":
            content = msg["content"]
            
            # content가 문자열인지 확인
            if not isinstance(content, str):
                content = str(content)
            
            # 여행 계획 내용 확인 (수정된 부분)
            travel_keywords = ["day1", "day 1", "첫날", "첫째날", "1일차", "여행 계획", "일정", "스케줄"]
            exclude_keywords = ["캘린더", "예약"]
            
            has_travel_content = any(pattern in content.lower() for pattern in travel_keywords)
            has_exclude_content = any(keyword in content.lower() for keyword in exclude_keywords)
            
            if has_travel_content and not has_exclude_content:
                travel_content.append(f"📋 **여행 계획**\n{content}")
    
    if travel_content:
        return "\n\n".join(travel_content)
        
    return None

# ========================================
# 4) 날짜/시간 관련 유틸
# ========================================
def parse_korean_date(date_str: str) -> str:
    """한국어 날짜를 ISO 8601 형식으로 변환"""
    patterns = [
        r'(\d{2})년\s*(\d{1,2})월\s*(\d{1,2})일',
        r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일',
        r'(\d{4})-(\d{1,2})-(\d{1,2})',
        r'(\d{2})/(\d{1,2})/(\d{1,2})',
    ]

    for pattern in patterns:
        match = re.search(pattern, date_str)
        if match:
            year, month, day = match.groups()
            if len(year) == 2:
                year = f"20{year}"
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    return None

def extract_date_from_input(user_input: str) -> str:
    """사용자 입력에서 날짜 추출 (오늘, 내일, 모레 등 포함)"""
    # user_input이 문자열인지 확인
    if not isinstance(user_input, str):
        user_input = str(user_input)
        
    parsed_date = parse_korean_date(user_input)
    if parsed_date:
        return parsed_date

    today = datetime.now()
    if "오늘" in user_input:
        return today.strftime('%Y-%m-%d')
    elif "내일" in user_input:
        return (today + timedelta(days=1)).strftime('%Y-%m-%d')
    elif "모레" in user_input:
        return (today + timedelta(days=2)).strftime('%Y-%m-%d')
    return None

def validate_date_format(date_string: str) -> bool:
    """ISO 8601 날짜 형식 검증"""
    try:
        datetime.fromisoformat(date_string.replace('+09:00', ''))
        return True
    except ValueError:
        return False

def sanitize_input(text: str) -> str:
    """사용자 입력에서 위험 문자 제거 후 최대 1000자 반환"""
    # text가 문자열인지 확인
    if not isinstance(text, str):
        text = str(text)
    return re.sub(r'[;\"\'\n]', '', text)[:1000]