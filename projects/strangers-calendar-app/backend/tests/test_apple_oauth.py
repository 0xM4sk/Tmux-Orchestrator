|
import pytest
from backend.auth.apple_oauth import fetch_user_info_from_apple

@pytest.fixture
def id_token():
return 'test_id_token'

def test_fetch_user_info_from_apple(id_token):
user_info = fetch_user_info_from_apple(id_token)
assert 'sub' in user_info