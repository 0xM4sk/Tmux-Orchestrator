|
# Google OAuth implementation
from flask import Flask, request, redirect
import requests

def fetch_user_info_from_google(access_token):
response = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers={'Authorization': f'Bearer {access_token}'})
return response.json()