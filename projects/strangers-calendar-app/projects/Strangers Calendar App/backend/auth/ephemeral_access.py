|
import time

def generate_ephemeral_token(user_id, expiration_time):
token = f"{user_id}_{time.time() + expiration_time}"
return token

def validate_ephemeral_token(token, user_id):
parts = token.split('_')
if len(parts) != 2:
return False
user_id_from_token, timestamp = parts
try:
timestamp = float(timestamp)
except ValueError:
return False
current_time = time.time()
if user_id == user_id_from_token and current_time < timestamp:
return True
return False

def get_user_data(token):
if validate_ephemeral_token(token, '123'):
return {'user_id': '123', 'data': 'protected data'}
return None