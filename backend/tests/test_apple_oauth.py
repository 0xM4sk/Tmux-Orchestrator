|
import pytest
from backend.auth.apple_oauth import fetch_user_info_from_apple

@pytest.fixture
def user_info():
return {
'id': '12345',
'email': 'test@example.com'
}

def test_fetch_user_info_from_apple(user_info):
result = fetch_user_info_from_apple(user_info)
assert result == user_info