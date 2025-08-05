|
import unittest
from backend.auth.oauth import app as oauth_app
from backend.auth.phone import app as phone_app
from backend.calendar import app as calendar_app
from backend.availability import app as availability_app
from backend.intersection import app as intersection_app
from backend.cleanup import app as cleanup_app

class TestIntegration(unittest.TestCase):
def test_oauth_login(self):
with oauth_app.test_client() as client:
response = client.get('/login')
self.assertEqual(response.status_code, 200)

def test_phone_register(self):
with phone_app.test_client() as client:
response = client.get('/register_phone')
self.assertEqual(response.status_code, 200)

def test_calendar_create(self):
with calendar_app.test_client() as client:
response = client.get('/create_calendar')
self.assertEqual(response.status_code, 200)

def test_availability_add(self):
with availability_app.test_client() as client:
response = client.get('/add_availability')
self.assertEqual(response.status_code, 200)

def test_intersection_intersect(self):
with intersection_app.test_client() as client:
response = client.get('/intersect_availability')
self.assertEqual(response.status_code, 200)

def test_cleanup_calendar(self):
with cleanup_app.test_client() as client:
response = client.get('/cleanup_calendar')
self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
unittest.main()