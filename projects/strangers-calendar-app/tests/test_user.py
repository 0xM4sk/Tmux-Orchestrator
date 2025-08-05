|
import pytest
from flask_sqlalchemy import SQLAlchemy
from backend.api.v1.user import app, db

@pytest.fixture(scope='module')
def test_client():
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

with app.app_context():
db.create_all()

yield app.test_client()

with app.app_context():
db.session.remove()
db.drop_all()

def test_create_user(test_client):
response = test_client.post('/user', json={'username': 'testuser', 'email': 'test@example.com', 'password_hash': 'testpassword'})
assert response.status_code == 201

def test_get_user(test_client):
token = generate_token()  # Assume we have a function to generate a token
response = test_client.get('/user?token=' + token)
assert response.status_code == 200

def test_update_user(test_client):
token = generate_token()  # Assume we have a function to generate a token
response = test_client.put('/user?token=' + token, json={'username': 'newtestuser', 'email': 'newtest@example.com'})
assert response.status_code == 200

def test_delete_user(test_client):
token = generate_token()  # Assume we have a function to generate a token
response = test_client.delete('/user?token=' + token)
assert response.status_code == 200