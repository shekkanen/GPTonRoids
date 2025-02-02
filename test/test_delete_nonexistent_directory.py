
import requests
import os

BASE_URL = 'http://localhost:8000'
GPTONROIDS_API_KEY = os.getenv("GPTONROIDS_API_KEY")
GPTONROIDS_API_KEY_NAME = "GPTONROIDS_API_KEY"

def test_delete_nonexistent_directory():
    response = requests.delete(f'{BASE_URL}/directories/nonexistent_dir', headers={"GPTONROIDS_API_KEY": GPTONROIDS_API_KEY})
    assert response.status_code == 404
    assert response.json()['detail'] == "Directory not found"
