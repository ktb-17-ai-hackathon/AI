import json
import hashlib
import time
from pydantic import ValidationError
from typing import Any, Dict, Optional
from app.schemas.life_cycle_response import LifeCyclePlanResponse
from app.services.json_sanitizer import extract_json_object
from app.services.gemini_service import (
    GeminiService,
    GeminiServiceUnavailable,
    GeminiServiceTimeout,
)

class LifeCycleService:
    def __init__(self, gemini: GeminiService, repo):
        self.gemini = gemini
        self.repo = repo
        self._cache: Dict[str, LifeCyclePlanResponse] = {}
        self._failure_count = 0
        self._breaker_open_until = 0.0

    def _build_prompt(self, user_data: dict) -> str:
        user_info_text = json.dumps(user_data, ensure_ascii=False, indent=2)

        return f"""
Role
너는 '청약 자산 설계 에이전트'다. 입력 JSON만을 근거로 한국어로 분석하고, 사전 정의된 JSON 스키마로만 답한다.

Task
- 사용자의 현황을 진단하고 청약 적합도, 자산 로드맵, 실행 지침, 지역/대출/가산점 포인트를 제시한다.
- 숫자/지역/직업 등은 입력 JSON 그대로 사용한다. 추측은 금지하며, 부족한 정보는 텍스트에서 보수적으로 언급한다.

Strict JSON Rules
1) 반드시 단 하나의 JSON 객체만 출력한다. 코드블록/머리말/주석/설명 문장 금지.
2) 스키마의 키와 값 타입을 정확히 지킨다. 불리언은 true/false, 숫자는 정수, 문자열은 따옴표로 감싼다.
3) 추가 키, trailing comma, null 사용 금지. 배열은 최소 1개 이상의 문자열을 넣는다.
4) 모든 문자열은 한국어 간결 문장으로 작성한다. 투자 권유·확정적 수익 표현 금지.
5) 출력 문자열에는 JSON 필드명(예: confidenceLevel, recommendedHorizon 등)을 그대로 노출하지 말고, 한국어 설명으로 풀어쓴다.

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
""".strip()
    
    def _build_fallback_plan(self, user_data: Dict[str, Any], reason: str) -> LifeCyclePlanResponse:
        monthly_saving = int(user_data.get("monthlySavingAmount") or 0)
        base_assets = int(user_data.get("currentFinancialAssets") or 0) + int(user_data.get("additionalAssets") or 0)
        district = user_data.get("currentDistrict") or "거주 지역"

        projection = []
        running_total = base_assets
        for year in range(1, 4):
            running_total += monthly_saving * 12
            projection.append({"year": year, "amount": running_total})

        payload = {
            "summary": {
                "title": "임시 청약 플랜 (LLM 지연)",
                "body": "현재 AI 응답이 지연되어 기본 가이드를 제공합니다.",
            },
            "diagnosis": {
                "canBuyWithCheongyak": False,
                "confidenceLevel": "LOW",
                "reasons": [
                    "AI 분석 지연으로 보수적인 가이드를 제공합니다.",
                    f"{district} 기준 자금 계획과 청약 자격을 우선 점검하세요.",
                ],
            },
            "timeHorizonStrategy": {
                "now": "지금은 자금·부채 현황을 정리하고 청약 자격 요건을 재확인하세요.",
                "threeYears": "3년 내 월 저축액을 유지·증액하며 청약 가점을 높이는 행동을 이어가세요.",
                "fiveYears": "5년 시점에 목표 지역의 분양 캘린더와 대출 한도를 점검해 최종 청약을 준비하세요.",
            },
            "chartData": {"savingProjectionByYear": projection},
            "planMeta": {"recommendedHorizon": "MID_5", "reason": "LLM 분석 실패 시 기본 5년 중기 플랜을 제시합니다."},
        }

        return LifeCyclePlanResponse(**payload)

    def _build_report(self, plan: LifeCyclePlanResponse, user_data: Dict[str, Any]) -> str:
        def _clean_phrase(text: str, drop_prefix: str = "") -> str:
            cleaned = (text or "").strip()
            if drop_prefix and cleaned.startswith(drop_prefix):
                cleaned = cleaned[len(drop_prefix):].lstrip()
            if cleaned.endswith((".", "!", "?")):
                cleaned = cleaned[:-1].rstrip()
            return cleaned

        monthly_saving = int(user_data.get("monthlySavingAmount") or 0)
        current_assets = int(user_data.get("currentFinancialAssets") or 0)
        extra_assets = int(user_data.get("additionalAssets") or 0)
        annual_income = int(user_data.get("annualIncome") or 0)
        district = user_data.get("currentDistrict") or "거주 지역"
        preferred_region = user_data.get("preferredRegion") or "희망 지역"

        reasons_text = "; ".join(plan.diagnosis.reasons) if plan.diagnosis.reasons else "특이 사유 없음"
        projection_text = ", ".join(
            [f"{p.year}년차 예상 {p.amount:,}원" for p in plan.chartData.savingProjectionByYear]
        ) if plan.chartData.savingProjectionByYear else "저축 추정치 없음"

        now_text = _clean_phrase(plan.timeHorizonStrategy.now, "지금은")
        three_text = _clean_phrase(plan.timeHorizonStrategy.threeYears, "3년 내에는")
        five_text = _clean_phrase(plan.timeHorizonStrategy.fiveYears, "5년 시점에는")

        sections = [
            f"1) 진단 개요: {plan.summary.title}. {plan.summary.body} 청약 적합도는 {plan.diagnosis.confidenceLevel}이며, 현재 판단으로는 "
            f"{'청약으로도 진입 가능' if plan.diagnosis.canBuyWithCheongyak else '청약만으로는 진입이 어려워 보수적 접근이 필요'}합니다. "
            f"선택된 전략 호라이즌은 {plan.planMeta.recommendedHorizon}이며 사유는 '{plan.planMeta.reason}'입니다.",
            f"2) 재무 현황: 연소득 {annual_income:,}원, 월 저축 {monthly_saving:,}원 수준, 가용 자산은 {current_assets + extra_assets:,}원으로 추정됩니다. "
            f"저축 추정: {projection_text}. {reasons_text}",
            f"3) 단계별 실행: 지금은 {now_text}. 3년 내에는 {three_text}. 5년 시점에는 {five_text}.",
            f"4) 지역·대출 포인트: 현재 거주지 {district}와 희망 지역 {preferred_region}을 기준으로 통근·생활 편의를 유지하며 청약 가점을 관리하세요. "
            "대출 가능 한도와 규제는 주기적으로 확인하고, 청약 가산점을 높일 수 있는 가족 구성·무주택 기간 관리에 집중하세요.",
            "5) 당부: 계획은 시장 상황에 따라 조정이 필요합니다. 분기마다 자산·부채를 점검하고, 청약 일정과 제도 변화를 모니터링하세요. "
            "과도한 레버리지는 피하고 생활비 쿠션을 남겨 재무 스트레스를 낮추는 것이 핵심입니다.",
        ]

        return "\n".join(sections)

    def _get_cache_key(self, user_data: dict) -> Optional[str]:
        survey = user_data.get("surveyId")
        payload = json.dumps(user_data, ensure_ascii=False, sort_keys=True)
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return f"{survey}:{digest}" if survey is not None else digest

    def _get_cached_plan(self, cache_key: Optional[str]) -> Optional[LifeCyclePlanResponse]:
        if not cache_key:
            return None
        cached = self._cache.get(cache_key)
        return cached.model_copy(deep=True) if cached else None

    def _save_cache(self, cache_key: Optional[str], plan: LifeCyclePlanResponse) -> None:
        if not cache_key:
            return
        self._cache[cache_key] = plan.model_copy(deep=True)

    def _ensure_report(self, plan: LifeCyclePlanResponse, user_data: Dict[str, Any]) -> LifeCyclePlanResponse:
        if plan.report and plan.report.strip():
            return plan
        report = self._build_report(plan, user_data)
        return plan.model_copy(update={"report": report})

    def generate_plan(self, user_data: dict) -> LifeCyclePlanResponse:
        cache_key = self._get_cache_key(user_data)
        now_ts = time.time()

        if now_ts < self._breaker_open_until:
            cached = self._get_cached_plan(cache_key)
            if cached:
                cached = self._ensure_report(cached, user_data)
                self.repo.save_record(task="plan", user_data=user_data, question=None, result=cached.model_dump_json())
                return cached
            fallback = self._build_fallback_plan(user_data, "Gemini 회로가 일시적으로 닫혀 있습니다.")
            fallback = self._ensure_report(fallback, user_data)
            self.repo.save_record(task="plan", user_data=user_data, question=None, result=fallback.model_dump_json())
            return fallback

        prompt = self._build_prompt(user_data)
        try:
            raw_text = self.gemini.generate_text(prompt)
        except (GeminiServiceUnavailable, GeminiServiceTimeout) as e:
            self._failure_count += 1
            if self._failure_count >= 3:
                self._breaker_open_until = time.time() + 60

            cached = self._get_cached_plan(cache_key)
            if cached:
                cached = self._ensure_report(cached, user_data)
                self.repo.save_record(
                    task="plan",
                    user_data=user_data,
                    question=None,
                    result=cached.model_dump_json(),
                )
                return cached

            fallback = self._build_fallback_plan(user_data, str(e))
            fallback = self._ensure_report(fallback, user_data)
            self.repo.save_record(task="plan", user_data=user_data, question=None, result=fallback.model_dump_json())
            return fallback

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

        self._failure_count = 0
        self._breaker_open_until = 0.0
        validated = self._ensure_report(validated, user_data)

        self._save_cache(cache_key, validated)
        self.repo.save_record(task="plan", user_data=user_data, question=None, result=validated.model_dump_json())
        return validated
