|
import jwt
from datetime import datetime, timedelta

SECRET_KEY = 'your_secret_key'

def generate_token(email):
payload = {
'user_email': email,
'exp': datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
}
token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
return token

def verify_token(token):
try:
payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
return True
except jwt.ExpiredSignatureError:
return False
except jwt.InvalidTokenError:
return False