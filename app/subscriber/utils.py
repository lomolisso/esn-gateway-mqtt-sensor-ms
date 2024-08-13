import httpx
from app.core.config import GATEWAY_API_URL

def post_to_gateway_api(endpoint: str, json_data: dict):
    httpx.post(f"{GATEWAY_API_URL}{endpoint}", json=json_data)