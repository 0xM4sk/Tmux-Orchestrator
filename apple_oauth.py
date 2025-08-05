from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def get_apple_access_token(code):
"""Fetch Apple access token using the provided code."""
apple_auth_url = "https://appleid.apple.com/auth/token"
payload = {
"client_id": "your-client-id",
"client_secret": "your-client-secret",
"grant_type": "authorization_code",
"redirect_uri": "your-redirect-uri",
"code": code
}
headers = {
"Content-Type": "application/x-www-form-urlencoded"
}
response = requests.post(apple_auth_url, data=payload, headers=headers)
if response.status_code == 200:
return response.json()
else:
raise Exception("Failed to fetch Apple access token")

@app.route('/apple/oauth', methods=['POST'])
def apple_oauth():
"""Handle Apple OAuth callback."""
try:
code = request.form.get('code')
access_token_response = get_apple_access_token(code)
# Process the access token response
return jsonify(access_token_response), 200
except Exception as e:
return jsonify({"error": str(e)}), 500