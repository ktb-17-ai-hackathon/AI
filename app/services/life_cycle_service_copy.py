import json
from pydantic import ValidationError
from app.schemas.life_cycle_response import LifeCyclePlanResponse
from app.services.json_sanitizer import extract_json_object

class LifeCycleService:
    def __init__(self, gemini, repo):
        self.gemini = gemini
        self.repo = repo

    def _build_prompt(self, user_data: dict) -> str:
        user_info_text = json.dumps(user_data, ensure_ascii=False, indent=2)

        return f"""
Role
너는 백엔드로부터 전달받은 [사용자 JSON 데이터]를 정밀 분석하여, 주택 구매를 위한 자산 형성 과정과 최적의 청약 시나리오를 설계하는 'AI 자산 설계 에이전트'다.


Output Format
사용자 현황 진단
적합 트랙: [생애최초 / 신혼부부 / 다자녀 / 일반공급/ 한부모 가정 중 가장 유리한 유형]
강점과 약점: 현재 데이터 기준(무주택 기간, 현재 자산, 부채 등), 청약 가점 및 자금력의 객관적 위치.

자산 로드맵 및 미래 예측
목표 시점 자산: 사용자의 계획(결혼/출산/구매 등)이 맞물리는 시점의 예상 가용 자금.
자금 분석: "현재의 저축 페이스라면 targetResidence 진입을 위해 OO년의 시간이 소요되거나, 대출 OO원이 필요합니다. 총합 OO 원을 보유해야 합니다."

에이전트의 전략적 솔루션
최적의 타이밍: "아이를 낳고 청약을 넣으세요" vs "결혼 직후 신혼특공을 노리세요"에 대한 명확한 결론.
실행 지침: 목표하는 preferredArea 평형과 priorityCriteria(학군/역세권 등)를 충족하기 위해 지금 즉시 조정해야 할 저축/투자 행동.

청약 가이드
청약 과정 상세 설명: “아이를 낳은 후 출생신고서를 제출하세요. 세대원에 아이가 포함되는지 확인하세요.” “해택 기간 제시”

지역 추천
사용자의 직장, 거주지, 상권 선호를 바탕으로 가장 적합한 세 곳의 구를 추천(추천 시 자세한 설명 및 가격, 평수 비교)

대출 가이드
지역 규제로 인한 대출 가능 금액 계산.
현재 상황을 고려하여 대출 상품 추천.
주거하는 구, 직장이 있는 구에 있는 혜택 찾아보기
생애 최초 대출에 해당하는지 분석 및 설명.
추천하는 대출 상품으로 대출을 할 시 우리 서비스는 대출 상품은 수수료를 받습니다.”

가산점
청약 가산점 계산 및 분석.
가산점을 올리기 위한 개선 방향 제시.

Constraints
모든 분석은 백엔드에서 넘어온 JSON 필드 데이터에 근거해야 한다.
targetResidence는 텍스트 그대로 해석하여 해당 지역의 특성을 반영한다.
데이터가 부족하거나 비현실적인 목표일 경우, '현실적인 대안(지역 하향 또는 저축액 상향)'을 반드시 제시한다.

아래 사용자 데이터를 기반으로,
반드시 JSON 객체 하나만 출력하라.
설명 문장, 마크다운, 코드블록(
)은 절대 포함하지 말고
아래 스키마와 키 이름을 정확히 지켜라.

[사용자 데이터]
{user_info_text}

[출력 JSON 스키마]
{{
  "summary": {{
    "title": "string",
    "body": "string"
  }},
  "diagnosis": {{
    "canBuyWithCheongyak": boolean,
    "confidenceLevel": "HIGH | MEDIUM | LOW",
    "reasons": ["string"]
  }},
  "timeHorizonStrategy": {{
    "now": "string",
    "threeYears": "string",
    "fiveYears": "string"
  }},
  "chartData": {{
    "savingProjectionByYear": [
      {{ "year": number, "amount": number }}
    ]
  }},
  "planMeta": {{
    "recommendedHorizon": "SHORT_3 | MID_5 | LONG_10",
    "reason": "string"
  }}
}}

규칙:
- 출력은 **순수 JSON 텍스트만**
- 코드블록(
) 사용 금지
JSON 외 다른 텍스트 금지
투자 권유 표현 금지
""".strip()
    
    def generate_plan(self, user_data: dict) -> LifeCyclePlanResponse:
        prompt = self._build_prompt(user_data)
        raw_text = self.gemini.generate_text(prompt)

        # 이부분을 없애기
        cleaned_json = extract_json_object(raw_text)

        try:
            parsed = json.loads(cleaned_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM returned invalid JSON after cleaning: {str(e)} | cleaned={cleaned_json[:200]}")

        try:
            validated = LifeCyclePlanResponse(**parsed)
        except ValidationError as e:
            raise ValueError(f"LLM JSON schema mismatch: {e}")

        self.repo.save_record(task="plan", user_data=user_data, question=None, result=cleaned_json)
        return validated