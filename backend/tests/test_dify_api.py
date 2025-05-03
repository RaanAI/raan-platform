import requests

def test_dify_api():
    url = "http://localhost:5001/api/status"
    try:
        response = requests.get(url)
        assert response.status_code == 200, "Dify API is not reachable"
    except Exception as e:
        assert False, f"Request failed: {e}"
