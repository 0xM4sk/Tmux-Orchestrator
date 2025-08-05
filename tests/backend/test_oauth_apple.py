|
import pytest
from backend.auth.oauth import apple_auth

@pytest.mark.parametrize("test_input,expected", [
("valid_token", True),
("invalid_token", False)
])
def test_apple_auth(test_input, expected):
assert apple_auth(test_input) == expected