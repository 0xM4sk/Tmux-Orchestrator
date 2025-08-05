|
# Phone number validation implementation

from flask import request, jsonify

def validate_phone_number(phone_number):
# Simple regex pattern to check if phone number is in E.164 format
import re
pattern = r"^\+?1?\d{9,15}$"
return re.match(pattern, phone_number) is not None

@app.route('/validate_phone', methods=['POST'])
def validate_phone():
data = request.get_json()
phone_number = data.get('phone_number')

if validate_phone_number(phone_number):
return jsonify({'message': 'Phone number is valid'}), 200
else:
return jsonify({'message': 'Phone number is invalid'}), 400