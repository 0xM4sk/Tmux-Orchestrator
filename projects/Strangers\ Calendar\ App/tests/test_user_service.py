|
import unittest
from services.user_service import send_verification_email

class TestUserService(unittest.TestCase):
@patch('services.email_service.send_email')
def test_send_verification_email_with_invalid_email(self, mock_send_email):
# Arrange
user = {'email': 'invalid-email'}

# Act
with self.assertRaises(ValueError):
send_verification_email(user)

# Assert
mock_send_email.assert_not_called()

if __name__ == '__main__':
unittest.main()