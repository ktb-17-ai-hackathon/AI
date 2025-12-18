# json 추출 유틸 함수
import re

def extract_json_object(text: str) -> str:
    """
    LLM이 반환한 텍스트에서 JSON 객체만 뽑아냄.
    - ```json ... ``` 코드펜스 제거
    - 텍스트 중 첫 '{' ~ 마지막 '}' 구간만 추출
    """
    if not text:
        raise ValueError("Empty LLM response.")

    # 1) ```json ... ``` 또는 ``` ... ``` 제거
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1).strip()

    # 2) 첫 { 부터 마지막 } 까지 추출
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"Could not locate JSON object in LLM output: {text[:200]}")

    return text[start:end + 1].strip()