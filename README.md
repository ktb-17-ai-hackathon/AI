# 청약 플랜 에이전트
### AI -powered Housing Subscription Planning Agent
- 청약 플랜 에이전트는 개인의 생애주기, 자산, 가족, 계획 데이터를 기반으로, 주택 청약 가능성과 중장기 내 집 마련 전략을 제시하는 AI 분석 서비스입니다.

## Contributer
- 이지우: Baseline code implementation, Prompt Engineering
- 조유림: Baseline code Optimize, AI service implementation


## **기술 스택**
- AI: Gemini API, FastAPI, Python, uvicorn, gunicorn

## **기술 적용 전략 (이번 프로젝트에서 기술을 어떻게 적용할 것인가?)**

- 해당 기술을 선택한 이유:
    - pydantic 기반 요청/응답 스키마 검증 가능
    - 자연어와 구조화 JSON으로 결과 도출
    - 출력 형식 강제 및 규칙 제어
    - LLM 연동에 최적화 된 생태계
    - 서비스 개발 속도를 높일 수 있음
- 구현 방법:
    - 아키텍쳐 구성
        - Router: 엔드포인트 제공, 요청 검증 및 응답 반환
        - Service: 프롬픔트 생성, Gemini 호출, 응답 정제, JSON 파싱 및 Pydantic 검증
        - Schema: 데이터 타입 설정, 데이터 구조 정의, 데이터 검증
    - API 흐름
        - 백엔드에서 설문 JSON을 엔드포인트로 POST
        - FastAPI가 입력 검증
        - Service가 프롬프트 구성
        - Gemini API 호출
        - 응답에서 올바른 JSON 형태로 변환
        - 변환된 JSON을 다시 백엔드로 반환

## **예상 기술 리스크 & 해결 전략(리스크 관리)**

- 구체적인 실현 가능성:
    - 입력이 설문 JSON으로 고정되어 있어 **스키마 기반 검증(Pydantic)**이 가능하고,
    - 출력도 사전 합의된 JSON 스펙으로 강제하므로 **프론트 연동 난이도가 낮음**
    - FastAPI + Gemini API는 단순 HTTP 통신 구조라 구축/배포가 현실적으로 가능함(Docker/Cloud Run 등)
- 예상되는 기술적 문제:
    1. **Gemini API 지연/타임아웃**
        - 응답 시간이 길어 100초로 설정, 네트워크 불안정
    2. **레이트 리밋/비용 증가**
        - 동시 요청 증가 시 호출 제한 또는 과금 부담
    3. **품질 이슈**
        - LLM이 주는 분석이 신뢰도가 없을 수 있고 정확하지 않을 수 있다
- 해결 전략:
    - **타임아웃/에러 처리 표준화**
        - Gemini 호출 타임아웃 시 504 Gateway Timeout 반환
        - 네트워크/HTTP 오류는 502 Bad Gateway로 반환
        - (옵션) 1회 재시도(backoff) 적용
        - “분석 실패 fallback JSON” 제공(프론트가 깨지지 않도록 최소 구조 반환)
    - **호출량 제어(비용/레이트리밋 대응)**
        - 동일 surveyId 요청은 캐싱(예: Redis/메모리 캐시, TTL)
        - 사용자별/분당 요청 제한(rate limit) 적용
        - 로그 기반으로 호출량 모니터링(추후 Prometheus/Grafana 연동)
