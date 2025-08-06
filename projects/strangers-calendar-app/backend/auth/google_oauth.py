|
# Google OAuth authentication implementation
from flask import Flask, request, redirect, url_for, session
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = 'your_secret_key'

oauth = OAuth(app)
google = oauth.register(
name='google',
client_id='your_google_client_id',
client_secret='your_google_client_secret',
access_token_url='https://accounts.google.com/o/oauth2/token',
access_token_params=None,
authorize_url='https://accounts.google.com/o/oauth2/auth',
authorize_params=None,
api_base_url='https://www.googleapis.com/oauth2/v1/',
client_kwargs={'scope': 'openid email profile'},
)

@app.route('/login')
def login():
redirect_uri = url_for('authorize', _external=True)
return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
token = google.authorize_access_token()
resp = google.get('userinfo')
user_info = resp.json()

# Save the user information in the session or database
session['user'] = user_info

return 'Logged in as: ' + user_info.get('email')

if __name__ == '__main__':
app.run(debug=True)