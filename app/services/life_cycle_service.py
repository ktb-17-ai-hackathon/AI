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
너는 대한민국 부동산·청약 환경을 이해하는 자산 분석 AI다.

아래 사용자 데이터를 기반으로,
반드시 **JSON 객체 하나만** 출력하라.
설명 문장, 마크다운, 코드블록(```)은 절대 포함하지 말고
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
- 코드블록(```) 사용 금지
- JSON 외 다른 텍스트 금지
- 투자 권유 표현 금지
""".strip()
    
    def generate_plan(self, user_data: dict) -> LifeCyclePlanResponse:
        prompt = self._build_prompt(user_data)
        raw_text = self.gemini.generate_text(prompt)

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