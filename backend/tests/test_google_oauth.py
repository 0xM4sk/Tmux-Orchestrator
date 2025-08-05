|
import pytest
from backend.auth.google_oauth import fetch_user_info_from_google

@pytest.fixture
def user_info():
return {
'id': '12345',
'email': 'test@example.com'
}

def test_fetch_user_info_from_google(user_info):
result = fetch_user_info_from_google(user_info)
assert result == user_info