import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    GEMINI_URL: str = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-2.5-flash:generateContent"
    )
    GEMINI_TIMEOUT_SEC: int = 300

settings = Settings()