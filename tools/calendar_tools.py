from datetime import datetime, timezone, timedelta
import streamlit as st

from langchain.tools import tool
from config import service, CALENDAR_ID
from utils.utils import validate_date_format

@tool
def check_event_exists(input: str) -> str:
    """
    특정 제목과 날짜의 이벤트가 존재하는지 확인합니다.
    입력 형식: 제목;날짜(YYYY-MM-DD)
    """
    try:
        summary, date = [x.strip() for x in input.split(";")]
        start_date = f"{date}T00:00:00+09:00"
        end_date = f"{date}T23:59:59+09:00"
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_date,
            timeMax=end_date,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        for event in events:
            if event.get('summary', '').strip() == summary.strip():
                return f"EXISTS:{event.get('id')}:{event.get('summary')}"
        return "NOT_EXISTS"
    except Exception as e:
        return f"ERROR: {e}"

@tool
def create_event_tool(input: str) -> str:
    """
    일정을 생성합니다. 입력 형식: 제목; 시작시간; 종료시간
    """
    try:
        summary, start, end = [x.strip() for x in input.split(";")]

        if not validate_date_format(start) or not validate_date_format(end):
            return f"❌ 잘못된 날짜 형식입니다: {start}, {end}"

        date_part = start.split('T')[0]
        check_result = check_event_exists(f"{summary};{date_part}")
        if check_result.startswith("EXISTS:"):
            event_id = check_result.split(":")[1]
            try:
                service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
                st.write(f"🔄 기존 '{summary}' 일정을 삭제했습니다.")
            except Exception as delete_error:
                st.write(f"⚠️ 기존 일정 삭제 실패: {delete_error}")

        event = {
            'summary': summary,
            'start': {'dateTime': start, 'timeZone': 'Asia/Seoul'},
            'end': {'dateTime': end, 'timeZone': 'Asia/Seoul'}
        }
        created = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

        start_time = datetime.fromisoformat(start.replace('+09:00', '')).strftime('%m월 %d일 %H:%M')
        end_time = datetime.fromisoformat(end.replace('+09:00', '')).strftime('%H:%M')
        return f"✅ '{summary}' 일정이 {start_time}~{end_time}에 성공적으로 등록되었습니다!"
    except Exception as e:
        return f"❌ 일정 등록에 실패했습니다: {str(e)}"

@tool
def list_events_tool(input: str = "") -> str:
    """
    오늘 이후의 일정을 최대 10개까지 조회합니다.
    """
    try:
        now = datetime.now(timezone(timedelta(hours=9))).isoformat()
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        if not events:
            return "예정된 일정이 없습니다."
        event_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', '제목 없음')
            event_id = event.get('id', '')
            event_list.append(f"{start} - {summary} (ID: {event_id})")
        return "\n".join(event_list)
    except Exception as e:
        return f"일정 조회 실패: {e}"

@tool
def update_event_tool(input: str) -> str:
    """
    일정을 수정합니다. 입력 형식: 이벤트ID; 새 제목; 새 시작시간; 새 종료시간
    """
    try:
        event_id, new_summary, new_start, new_end = [x.strip() for x in input.split(";")]
        event = service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()
        event['summary'] = new_summary
        event['start'] = {'dateTime': new_start, 'timeZone': 'Asia/Seoul'}
        event['end'] = {'dateTime': new_end, 'timeZone': 'Asia/Seoul'}
        updated = service.events().update(calendarId=CALENDAR_ID, eventId=event_id, body=event).execute()
        return f"✅ '{new_summary}' 일정이 성공적으로 수정되었습니다!"
    except Exception as e:
        return f"❌ 일정 수정에 실패했습니다: {str(e)}"

@tool
def delete_event_tool(input: str) -> str:
    """
    일정을 삭제합니다. 입력 형식: 이벤트ID
    """
    try:
        event_id = input.strip()
        service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
        return "✅ 일정이 성공적으로 삭제되었습니다!"
    except Exception as e:
        return f"❌ 일정 삭제에 실패했습니다: {str(e)}"