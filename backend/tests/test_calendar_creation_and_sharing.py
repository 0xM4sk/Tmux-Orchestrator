|
import unittest
from app import create_app, db
from models import User

class CalendarTestCase(unittest.TestCase):
def setUp(self):
self.app = create_app('testing')
self.app_context = self.app.app_context()
self.app_context.push()
db.create_all()

def tearDown(self):
db.session.remove()
db.drop_all()
self.app_context.pop()

def test_calendar_creation_and_sharing(self):
# Add calendar creation and sharing tests here
pass

if __name__ == '__main__':
unittest.main()