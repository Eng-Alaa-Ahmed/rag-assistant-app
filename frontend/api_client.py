import os
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def ask_question(question, image_bytes=None, image_name=None):
    if image_bytes:
        response = requests.post(
            API_BASE_URL + "/query-image",
            data={"question": question},
            files={"image": (image_name or "image.jpg", image_bytes)},
            timeout=300,
        )
    else:
        response = requests.post(
            API_BASE_URL + "/query",
            json={"question": question},
            timeout=120,
        )
    response.raise_for_status()
    return response.json()


def check_health():
    try:
        response = requests.get(API_BASE_URL + "/health", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False