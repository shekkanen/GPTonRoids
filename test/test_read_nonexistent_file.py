
import requests
import os

BASE_URL = 'http://localhost:8000'
GPTONROIDS_API_KEY = os.getenv("GPTONROIDS_API_KEY")
GPTONROIDS_API_KEY_NAME = "GPTONROIDS_API_KEY"

def test_read_nonexistent_file():
    response = requests.get(f'{BASE_URL}/files/nonexistent.txt', headers={"GPTONROIDS_API_KEY": GPTONROIDS_API_KEY})
    assert response.status_code == 404
    assert "File not found" in response.json()['detail']
