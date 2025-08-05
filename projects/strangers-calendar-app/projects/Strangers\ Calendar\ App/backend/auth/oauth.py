|
import time
from datetime import timedelta

class OAuthAuthenticator:
def __init__(self):
self.access_tokens = {}

def generate_access_token(self, user_id):
token = f"{user_id}_{time.time()}"
expiration_time = time.time() + timedelta(hours=1)  # Token expires in 1 hour
self.access_tokens[token] = expiration_time
return token

def validate_access_token(self, token):
if token in self.access_tokens and self.access_tokens[token] > time.time():
del self.access_tokens[token]
return True
return False