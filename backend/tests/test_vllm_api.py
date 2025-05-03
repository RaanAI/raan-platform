import requests

def test_vllm_api():
    url = "http://localhost:8000/v1/models"
    response = requests.get(url)
    assert response.status_code == 200, "vLLM API not reachable"
    data = response.json()
    assert "data" in data and isinstance(data["data"], list), "Unexpected response format"
