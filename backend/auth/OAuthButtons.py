|
from flask import request, jsonify
from functools import wraps

def handle_oauth_response(func):
@wraps(func)
def wrapper(*args, **kwargs):
token = request.json.get('token')
if not token:
return jsonify({"message": "Token is missing"}), 401

# Validate the token
if validate_token(token):
return func(*args, **kwargs)
else:
return jsonify({"message": "Invalid token"}), 401

return wrapper

def validate_token(token):
# Placeholder for token validation logic
return True

# Example usage in an OAuth endpoint
@app.route('/auth/google', methods=['POST'])
@handle_oauth_response