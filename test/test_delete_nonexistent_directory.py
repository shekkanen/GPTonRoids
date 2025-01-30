
import requests
import os

BASE_URL = 'http://localhost:8000'
API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "x-api-key"

def test_delete_nonexistent_directory():
    response = requests.delete(f'{BASE_URL}/directories/nonexistent_dir', headers={"x-api-key": API_KEY})
    assert response.status_code == 404
    assert response.json()['detail'] == "Directory not found"
