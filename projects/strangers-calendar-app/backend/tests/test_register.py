|
import unittest
from flask import Flask, json
from ..app import app

class TestRegister(unittest.TestCase):
def setUp(self):
self.app = app.test_client()
with app.app_context():
db.create_all()

def tearDown(self):
with app.app_context():
db.session.remove()
db.drop_all()

def test_register_success(self):
response = self.app.post('/register', data=json.dumps({'username': 'testuser', 'password': 'testpass'}), content_type='application/json')
self.assertEqual(response.status_code, 201)
self.assertIn('User registered successfully', str(response.data))

def test_register_existing_user(self):
response = self.app.post('/register', data=json.dumps({'username': 'testuser', 'password': 'testpass'}), content_type='application/json')
response = self.app.post('/register', data=json.dumps({'username': 'testuser', 'password': 'testpass'}), content_type='application/json')
self.assertEqual(response.status_code, 409)
self.assertIn('Username already exists', str(response.data))

def test_register_missing_username(self):
response = self.app.post('/register', data=json.dumps({'password': 'testpass'}), content_type='application/json')
self.assertEqual(response.status_code, 400)
self.assertIn('Username and password are required', str(response.data))

def test_register_missing_password(self):
response = self.app.post('/register', data=json.dumps({'username': 'testuser'}), content_type='application/json')
self.assertEqual(response.status_code, 400)
self.assertIn('Username and password are required', str(response.data))

if __name__ == '__main__':
unittest.main()