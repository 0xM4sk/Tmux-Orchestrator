|
# OAuth configuration settings
import os

oauth_config = {
'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID'),
'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET'),
'APPLE_CLIENT_ID': os.getenv('APPLE_CLIENT_ID'),
'APPLE_CLIENT_SECRET': os.getenv('APPLE_CLIENT_SECRET'),
'REDIRECT_URI': 'http://localhost:5000/auth/callback'
}