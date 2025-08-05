|
import pytest
from backend.auth.oauth import google_auth

@pytest.mark.parametrize("test_input,expected", [
("valid_token", True),
("invalid_token", False)
])
def test_google_auth(test_input, expected):
assert google_auth(test_input) == expected