|
# Phone number validation implementation
from flask import request, jsonify

def validate_phone_number(phone_number):
"""Validate phone number format."""
if not phone_number.isdigit():
return False
if len(phone_number) != 10:
return False
return True

@app.route('/validate-phone', methods=['POST'])
def validate_phone():
data = request.get_json()
phone_number = data.get('phone_number')

if validate_phone_number(phone_number):
return jsonify({'status': 'success'}), 200
else:
return jsonify({'status': 'error', 'message': 'Invalid phone number format'}), 400