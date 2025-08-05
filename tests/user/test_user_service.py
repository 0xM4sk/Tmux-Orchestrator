|
import unittest
from app import create_app, db

class UserRegistrationTestCase(unittest.TestCase):
def setUp(self):
self.app = create_app('testing')
self.app_context = self.app.app_context()
self.app_context.push()
db.create_all()

def tearDown(self):
db.session.remove()
db.drop_all()
self.app_context.pop()

def test_registration_with_email_verification(self):
# Simulate a user registration request
response = self.client.post('/register', json={"email": "test@example.com", "password": "testpassword"})

# Assert that the response status code is 201 (Created)
self.assertEqual(response.status_code, 201)

# Assert that an email verification link was sent
mock_mail.send.assert_called_once_with("test@example.com")