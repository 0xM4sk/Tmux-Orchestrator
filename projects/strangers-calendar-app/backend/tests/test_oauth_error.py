|
# Unit tests for OAuth error handling
import pytest
from backend.auth.oauth import google_login, apple_callback

def test_google_login_user_not_found(mocker):
mocker.patch('backend.auth.oauth.find_user_by_id', return_value=None)
with pytest.raises(Exception) as e:
google_login()
assert str(e.value) == "User not found"

def test_apple_callback_exception_handled(mocker):
with pytest.raises(Exception) as e:
apple_callback()
assert str(e.value) == "Exception raised in apple_callback"