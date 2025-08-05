|
from flask import Flask, request, jsonify
from .models import UserProfile

app = Flask(__name__)

@app.route('/user_profiles', methods=['POST'])
def create_user_profile():
data = request.get_json()
new_user_profile = UserProfile(username=data['username'], email=data['email'], passwordHash=data['passwordHash'])
new_user_profile.save()
return jsonify(new_user_profile.to_dict()), 201

@app.route('/user_profiles/<int:id>', methods=['GET'])
def get_user_profile(id):
user_profile = UserProfile.query.get_or_404(id)
return jsonify(user_profile.to_dict())

@app.route('/user_profiles/<int:id>', methods=['PUT'])
def update_user_profile(id):
data = request.get_json()
user_profile = UserProfile.query.get_or_404(id)
user_profile.username = data['username']
user_profile.email = data['email']
user_profile.passwordHash = data['passwordHash']
user_profile.save()
return jsonify(user_profile.to_dict())

@app.route('/user_profiles/<int:id>', methods=['DELETE'])
def delete_user_profile(id):
user_profile = UserProfile.query.get_or_404(id)
user_profile.delete()
return '', 204