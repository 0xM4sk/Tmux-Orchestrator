|
# Error handlers for OAuth authentication
from flask import jsonify

def handle_auth_error(e):
response = jsonify({"error": str(e)})
response.status_code = 401
return response