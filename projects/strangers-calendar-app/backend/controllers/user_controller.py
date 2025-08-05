|
# User controller implementation
from flask import request, jsonify
from backend.models.user import User

def get_user_profile(user_id):
user = User.query.get(user_id)
if user:
return jsonify({
'id': user.id,
'username': user.username,
'email': user.email
})
else:
return jsonify({'error': 'User not found'}), 404

def update_user_profile(user_id):
user = User.query.get(user_id)
if user:
data = request.get_json()
user.username = data.get('username', user.username)
user.email = data.get('email', user.email)
return jsonify({
'id': user.id,
'username': user.username,
'email': user.email
})
else:
return jsonify({'error': 'User not found'}), 404