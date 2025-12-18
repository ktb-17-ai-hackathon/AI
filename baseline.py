from fastapi import FastAPI, Body
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# =====================================================
# Gemini 2.5 Flash 설정
# =====================================================
# 실행 전에 반드시:
# export API_KEY=YOUR_GEMINI_API_KEY

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-2.5-flash:generateContent"
)


def call_gemini(prompt: str) -> str:
    response = requests.post(
        f"{GEMINI_URL}?key={GEMINI_API_KEY}",
        json={
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        },
        timeout=30
    )

    data = response.json()

    # Gemini 오류 방어
    if "candidates" not in data:
        return f"[Gemini Error] {json.dumps(data, ensure_ascii=False)}"

    return data["candidates"][0]["content"]["parts"][0]["text"]


# =====================================================
# 생애주기 설계 API (JSON 자유 입력)
# =====================================================
@app.post("/life-cycle-plan")
def generate_life_cycle_plan(user_data: dict = Body(...)):
    """
    - Spring에서 DB 조회 후 그대로 넘겨주는 JSON
    - 구조/필드 자유
    """

    user_info_text = json.dumps(
        user_data,
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
너는 대한민국 부동산·청약 환경을 이해하는
생애주기 자산 설계 AI다.

아래 JSON은 한 사용자의 현재 상태와 목표를
구조화한 데이터다.
필드 이름과 값의 의미를 스스로 해석해
생애주기 관점의 부동산 자산 플랜을 설계하라.

조건:
- 계산 과정이나 수식은 설명하지 말 것
- 단정적 표현, 투자 권유 표현은 피할 것
- 단계별(현재 / 준비기 / 목표 시점)로 설명할 것
- JSON에 없는 정보를 추측하지 말 것

[사용자 데이터(JSON)]
{user_info_text}

[출력 형식]
1. 현재 생애 단계 요약
2. 준비 단계 전략
3. 목표 시점 행동 가이드
"""

    plan_text = call_gemini(prompt)

    return {
        "input": user_data,
        "life_cycle_plan": plan_text
    }
