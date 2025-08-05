|
from flask import Blueprint, request, jsonify, abort
from models.user_profile import UserProfile

user_profiles_bp = Blueprint('user_profiles', __name__)

@user_profiles_bp.route('/user_profiles', methods=['POST'])
def create_user_profile():
data = request.get_json()
if not data:
return jsonify({'error': 'No input provided'}), 400

new_profile = UserProfile(**data)
try:
new_profile.save()
return jsonify(new_profile.to_dict()), 201
except Exception as e:
return jsonify({'error': str(e)}), 500

@user_profiles_bp.route('/user_profiles/<int:id>', methods=['GET'])
def get_user_profile(id):
profile = UserProfile.query.get_or_404(id)
return jsonify(profile.to_dict())

@user_profiles_bp.route('/user_profiles/<int:id>', methods=['PUT'])
def update_user_profile(id):
data = request.get_json()
if not data:
return jsonify({'error': 'No input provided'}), 400

profile = UserProfile.query.get_or_404(id)
for key, value in data.items():
setattr(profile, key, value)

try:
profile.save()
return jsonify(profile.to_dict()), 200
except Exception as e:
return jsonify({'error': str(e)}), 500

@user_profiles_bp.route('/user_profiles/<int:id>', methods=['DELETE'])
def delete_user_profile(id):
profile = UserProfile.query.get_or_404(id)
try:
profile.delete()
return jsonify({'message': 'Profile deleted successfully'}), 200
except Exception as e:
return jsonify({'error': str(e)}), 500

user_profiles_bp.register_error_handler(404, lambda error: (jsonify({'error': 'Resource not found'}), 404))