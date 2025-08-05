|
# OAuth authentication implementation
from flask import Flask, request, redirect
from datetime import datetime, timedelta
import jwt

SECRET_KEY = os.getenv('SECRET_KEY')

def create_ephemeral_token(user_id):
payload = {
'user_id': user_id,
'exp': datetime.utcnow() + timedelta(hours=1)
}
return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_ephemeral_token(token):
try:
payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
return payload
except jwt.ExpiredSignatureError:
return None

@app.route('/login', methods=['POST'])
def login():
user_id = request.form['user_id']
token = create_ephemeral_token(user_id)
return redirect(f'https://example.com/redirect?token={token}')