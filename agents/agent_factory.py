from langchain.agents import initialize_agent, AgentType
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from intents.intent_detector import filter_tools_by_intent
from config import llm
from utils.utils import format_conversation_for_agent

# 모든 툴을 import 해서 리스트로 만들어둡니다.
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

all_tools = [
    search_place,
    plan_trip_tool,
    create_calendar_from_plan,
    create_event_tool,
    check_event_exists,
    list_events_tool,
    update_event_tool,
    delete_event_tool,
    share_gist_tool,
    share_travel_plan_gist,
    debug_share_status,
]

def create_intent_based_agent(intent: str, user_input: str):
    """
    인텐트에 따라 특정 도구만 사용하는 에이전트 생성 (파싱 오류 방지)
    """
    filtered_tools = filter_tools_by_intent(intent, all_tools)

    intent_prompts = {
        "PLAN_TRIP": """너는 여행 계획 전문가입니다.
**오직 여행 계획 생성만** 수행하세요. 캘린더 예약이나 공유는 하지 마세요.
사용자가 요청하면 상세한 여행 일정을 만들어주세요.""",

        "BOOK_CALENDAR": """너는 캘린더 예약 전문가입니다.
**오직 캘린더 예약 기능만** 수행하세요. 새로운 여행 계획을 생성하지 마세요.
이전에 생성된 여행 계획을 캘린더에 등록해주세요.""",

        "SHARE_PLAN": """너는 공유 전문가입니다.
**오직 Gist 공유 기능만** 수행하세요. 여행 계획 생성이나 캘린더 예약은 하지 마세요.
기존 여행 계획을 GitHub Gist로 저장해주세요.""",

        "SEARCH_PLACE": """너는 장소 검색 전문가입니다.
**오직 장소 검색 기능만** 수행하세요. 전체 여행 계획을 생성하지 마세요.
사용자가 요청한 장소나 정보를 찾아서 알려주세요.""",

        "MANAGE_EVENT": """너는 일정 관리 전문가입니다.
**오직 기존 일정의 조회/수정/삭제만** 수행하세요. 새로운 계획은 생성하지 마세요.
캘린더의 기존 일정을 관리해주세요."""
    }

    system_prompt = f"""{intent_prompts.get(intent, "너는 도움이 되는 AI 어시스턴트입니다.")}

**중요: 출력 형식 규칙**
- 반드시 일반 한국어 텍스트로만 응답하세요
- JSON, XML, YAML 등의 구조화된 형식은 절대 사용하지 마세요
- action, action_input, output 같은 키워드는 사용하지 마세요
- 단순하고 명확한 문장으로 자연스럽게 답변하세요
- 마크다운 구조는 최소화하고 일반 텍스트 위주로 작성하세요

**인텐트: {intent}**
허용된 도구만 사용하고, 사용자가 명시적으로 요청하지 않은 추가 작업은 금지합니다.

현재 대화 컨텍스트: {{conversation_context}}
사용 가능한 도구: {[tool.name if hasattr(tool, 'name') else tool.__name__ for tool in filtered_tools]}"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = initialize_agent(
        tools=filtered_tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        memory=None,  # 메모리는 app.py에서 관리하므로 여기서는 None 또는 필요 시 전달
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3,
        max_execution_time=30,
        early_stopping_method="generate",
        agent_kwargs={
            'prompt': prompt,
            'handle_parsing_errors': "응답을 파싱할 수 없습니다. 일반 텍스트로 다시 답변해주세요."
        }
    )

    return agent