import requests

def post_json(url: str, payload: dict, timeout_sec: int) -> requests.Response:
    return requests.post(
        url,
        json=payload,
        timeout=timeout_sec,
        headers={"Content-Type": "application/json"},
    )