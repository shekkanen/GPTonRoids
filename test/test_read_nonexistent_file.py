
import requests
import os

BASE_URL = 'http://localhost:8001'
API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "x-api-key"

def test_read_nonexistent_file():
    response = requests.get(f'{BASE_URL}/files/nonexistent.txt', headers={"x-api-key": API_KEY})
    assert response.status_code == 404
    assert "File not found" in response.json()['detail']
