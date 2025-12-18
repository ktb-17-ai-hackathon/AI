import json
import requests
from app.core.config import settings
from app.core.http_client import post_json

class GeminiServiceError(Exception):
    pass

class GeminiServiceTimeout(GeminiServiceError):
    pass

class GeminiService:
    def __init__(self) -> None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set in environment variables.")

    def generate_text(self, prompt: str) -> str:
        url = f"{settings.GEMINI_URL}?key={settings.GEMINI_API_KEY}"

        try:
            resp = post_json(
                url=url,
                payload={"contents": [{"parts": [{"text": prompt}]}]},
                timeout_sec=settings.GEMINI_TIMEOUT_SEC,
            )
        except requests.Timeout:
            raise GeminiServiceTimeout("Gemini request timed out.")
        except requests.RequestException as e:
            raise GeminiServiceError(f"Gemini network error: {str(e)}")

        if resp.status_code >= 400:
            raise GeminiServiceError(f"Gemini HTTP {resp.status_code}: {resp.text}")

        data = resp.json()
        if "candidates" not in data or not data["candidates"]:
            raise GeminiServiceError(f"Gemini invalid response: {json.dumps(data, ensure_ascii=False)}")

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            raise GeminiServiceError(f"Gemini invalid shape: {json.dumps(data, ensure_ascii=False)}")