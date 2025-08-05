|
from flask import Flask, request, redirect
app = Flask(__name__)

@app.route('/login')
def login():
return '<button id="google">Google</button><button id="apple">Apple</button>'

@app.route('/auth/google', methods=['GET'])
def auth_google():
if request.method == 'GET':
return redirect('https://accounts.google.com/o/oauth2/auth')
else:
return 'Method Not Allowed', 405

@app.route('/auth/apple', methods=['GET'])
def auth_apple():
if request.method == 'GET':
return redirect('https://appleid.apple.com/auth/authorize')
else:
return 'Method Not Allowed', 405