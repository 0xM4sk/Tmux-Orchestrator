|
import pytest
from backend.app import app

@pytest.fixture
def client():
with app.test_client() as client:
yield client

def test_get_calendars(client):
response = client.get('/api/calendars')
assert response.status_code == 200
data = response.json()
assert len(data) > 0