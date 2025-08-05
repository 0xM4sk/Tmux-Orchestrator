|
import pytest
from models import db, User

@pytest.fixture(scope='module')
def app():
test_app = Flask(__name__)
test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
test_app.config['TESTING'] = True

with test_app.app_context():
db.create_all()
yield test_app
db.session.remove()
db.drop_all()

def test_user_creation(app):
with app.test_client() as client:
response = client.post('/register', json={
'username': 'testuser',
'email': 'test@example.com',
'password': 'password'
})
assert response.status_code == 201

def test_duplicate_user(app):
with app.test_client() as client:
client.post('/register', json={
'username': 'testuser',
'email': 'test@example.com',
'password': 'password'
})
response = client.post('/register', json={
'username': 'testuser',
'email': 'another@example.com',
'password': 'password'
})
assert response.status_code == 400