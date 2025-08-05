|
import pytest
from backend.auth.google_oauth import fetch_user_info_from_google

@pytest.fixture
def access_token():
return 'test_access_token'

def test_fetch_user_info_from_google(access_token):
user_info = fetch_user_info_from_google(access_token)
assert 'sub' in user_info