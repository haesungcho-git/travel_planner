import os
from datetime import datetime, timezone, timedelta

from googleapiclient.discovery import build
from google.oauth2 import service_account

from langchain_community.chat_models import BedrockChat

# ========================================
# 1) 환경 변수 로드
# ========================================
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "calendar_key.json")
SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_ID = os.getenv("CALENDAR_ID", "")

if not CALENDAR_ID:
    raise RuntimeError("환경 변수 CALENDAR_ID가 설정되지 않았습니다.")

# ========================================
# 2) Google Calendar API 서비스 객체 생성
# ========================================
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("calendar", "v3", credentials=credentials)

# ========================================
# 3) BedrockChat LLM 객체 생성
# ========================================
# (Anthropic Claude 3.5 Sonnet 예시, 필요 시 모델 ID 변경)
llm = BedrockChat(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    streaming=True,
    region_name="us-west-2"
)