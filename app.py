from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from langchain.schema import AIMessage, HumanMessage
from langchain.memory import ConversationBufferMemory

from config import (
    SERVICE_ACCOUNT_FILE,
    SCOPES,
    CALENDAR_ID,
    credentials,
    service,
    llm
)
from intents.intent_detector import detect_intent, filter_tools_by_intent
from utils.utils import (
    safe_add_message_to_memory,
    sanitize_input,
    extract_actual_response,
    format_conversation_for_agent
)
from tools.search_tools import search_place
from tools.calendar_tools import (
    check_event_exists,
    create_event_tool,
    list_events_tool,
    update_event_tool,
    delete_event_tool
)
from tools.travel_tools import plan_trip_tool, create_calendar_from_plan
from tools.share_tools import share_gist_tool, share_travel_plan_gist, debug_share_status
from agents.agent_factory import create_intent_based_agent

# ========================================
# Streamlit UI 설정
# ========================================
st.set_page_config(
    page_title="AI 여행 플래너 (파싱 오류 해결)",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ AI 여행 플래너")

# 사이드바
with st.sidebar:
    st.header("💡 사용법")
    st.markdown("""
    **여행 계획 생성** (PLAN_TRIP)
    ```
    부산 2박 3일 여행 계획 짜줘
    ```
    
    **캘린더 예약** (BOOK_CALENDAR)
    ```
    25년 6월 20일 시작으로 캘린더 예약해줘
    ```
    
    **공유하기** (SHARE_PLAN)
    ```
    여행 계획 공유해줘
    ```
    """)

# ========================================
# 1) 초기 메시지 및 메모리 설정
# ========================================
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome_text = "안녕하세요! AI 여행 플래너입니다."
    st.session_state.messages.append({"role": "assistant", "content": welcome_text})
    safe_add_message_to_memory(memory, AIMessage(content=welcome_text))

# ========================================
# 2) 채팅 기록 표시
# ========================================
col1, col2 = st.columns([3, 1])
with col1:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ========================================
# 3) 사용자 입력 처리
# ========================================
user_input = st.chat_input("메시지를 입력하고 Enter를 눌러주세요...")
if user_input:
    sanitized = sanitize_input(user_input)

    # 3-1) 인텐트 감지
    detected_intent = detect_intent(user_input)
    st.info(f"🎯 감지된 인텐트: {detected_intent}")

    # 3-2) 메시지 저장
    st.session_state.messages.append({"role": "user", "content": user_input})
    safe_add_message_to_memory(memory, HumanMessage(content=user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # 3-3) 인텐트 기반 에이전트 실행
    with st.chat_message("assistant"):
        with st.spinner(f"인텐트({detected_intent}) 처리 중..."):
            try:
                agent = create_intent_based_agent(detected_intent, user_input)
                conversation_context = format_conversation_for_agent()
                enhanced_prompt = f"{conversation_context}\n\n현재 요청: {sanitized}"

                raw_response = agent.run(enhanced_prompt)
                cleaned_response = extract_actual_response(raw_response)
                response = cleaned_response

            except Exception as e:
                error_message = str(e)
                if "Could not parse LLM output:" in error_message:
                    response = extract_actual_response(error_message)
                else:
                    response = f"⚠️ 시스템 오류: {error_message}"
                    st.error("문제가 발생했어요. 다시 시도해주세요.")

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            safe_add_message_to_memory(memory, AIMessage(content=response))