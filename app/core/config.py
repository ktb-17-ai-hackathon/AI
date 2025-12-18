import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

        # 기본값을 Pro로
        self.GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")

        # 모델에 따라 URL 동적으로 생성
        self.GEMINI_URL: str = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{self.GEMINI_MODEL}:generateContent"
        )

        self.GEMINI_TIMEOUT_SEC: int = int(os.getenv("GEMINI_TIMEOUT_SEC", "300"))

settings = Settings()
