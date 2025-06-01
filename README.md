# AI 여행 플래너

이 프로젝트는 Streamlit 기반의 AI 여행 플래너 웹앱입니다.  
LangChain + Amazon Bedrock(Anthropic Claude) LLM을 사용하여 여행 일정을 생성하고,  
Google Calendar API를 통해 자동으로 캘린더에 일정을 등록할 수 있습니다.  
또한 GitHub Gist를 이용해 여행 계획을 공유할 수 있는 기능이 포함되어 있습니다.

## 폴더 구조

```
travel_planner/
│
├── app.py                 # Streamlit 엔트리 포인트
├── config.py              # 환경 변수 및 Google Calendar / LLM 객체 초기화
├── requirements.txt       # 필요한 라이브러리 목록
├── README.md              # 프로젝트 설명 및 실행 방법
│
├── intents/               # 인텐트 감지 모듈
│   └── intent_detector.py
│
├── utils/                 # 공통 유틸리티 함수
│   └── utils.py
│
├── tools/                 # 실제 실행되는 “툴(tool)” 함수들
│   ├── search_tools.py
│   ├── calendar_tools.py
│   ├── travel_tools.py
│   └── share_tools.py
│
└── agents/                # 인텐트 기반 에이전트 생성 모듈
    └── agent_factory.py
```

## 실행 전 준비 사항

1. Python 3.8 이상 설치
2. `.env` 파일 생성 후 아래 환경 변수 설정  
   ```
   GOOGLE_APPLICATION_CREDENTIALS=<service-account-json 경로>
   CALENDAR_ID=<Google Calendar ID>
   SERPER_API_KEY=<Google Serper API 키>
   GITHUB_TOKEN=<GitHub Personal Access Token>
   ```

3. 필요한 패키지 설치  
   ```bash
   pip install -r requirements.txt
   ```

4. Streamlit 앱 실행  
   ```bash
   streamlit run app.py
   ```

## 주요 기능
``` 키워드로 구분 하는 것이 아니라 인텐트를 활용한 매핑으로 인해 키워드 방식 보다 좀 더 자연스럽고 다양하게 매핑이 가능할 것으로 예상합니다 ```
- **여행 계획 생성 (PLAN_TRIP)**  
  사용자가 “부산 2박 3일 여행 계획 짜줘” 와 같은 요청을 하면,  
  LLM을 통해 날짜/시간, 장소/활동이 포함된 상세한 일정표를 만들어줍니다.

- **캘린더 예약 (BOOK_CALENDAR)**  
  사용자가 “25년 6월 20일 시작으로 캘린더 예약해줘” 와 같이 요청하면,  
  이전에 생성된 여행 계획을 분석하여 자동으로 Google Calendar에 일정들을 등록합니다.

- **공유하기 (SHARE_PLAN)**  
  “여행 계획 공유해줘” 요청 시, 현재 대화 내에 저장된 여행 계획을 GitHub Gist로 업로드하고,  
  생성된 Gist URL을 반환합니다.

- **장소 검색 (SEARCH_PLACE)**  
  “여행지 검색해줘” 요청 시, Google Serper API를 통해 장소 정보(맛집·관광지 등)를 찾아서 알려줍니다.

- **일정 관리 (MANAGE_EVENT)**  
  “일정 목록 보여줘” / “일정 수정해줘” / “일정 삭제해줘” 등의 요청을 처리합니다.

---

## 스크린샷 및 설명
1. 여행 계획 생성 인텐트 발화 시 화면
![alt text](/screenshots/image.png)

2. 캘린더 예약 인텐트 발화 시 화면
![alt text](/screenshots/image-1.png)

3. 공유하기 인텐트 발화 시 화면
![alt text](/screenshots/image-2.png)

4. GitHub gist으로 마크다운 문서 링크 공유
![alt text](/screenshots/image-3.png)

5. 구글캘린더 등록 된 화면
![alt text](/screenshots/image-4.png)

url : https://gist.github.com/haesungcho-git/57b42638fd6f4086f3b3e6880bbc17a6