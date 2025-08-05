|
# Security settings for Flask application
from flask import Flask, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.before_request
def before_request():
if not request.is_secure:
url = request.url.replace('http://', 'https://', 1)
code = 301
return redirect(url, code=code)

@app.after_request
def after_request(response):
response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
response.headers['X-Content-Type-Options'] = 'nosniff'
response.headers['X-Frame-Options'] = 'SAMEORIGIN'
response.headers['X-XSS-Protection'] = '1; mode=block'
return response