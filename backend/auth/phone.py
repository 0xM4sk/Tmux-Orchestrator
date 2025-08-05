|
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/api/validate_phone', methods=['POST'])
def validate_phone():
phone_number = request.json.get('phone_number')
if not phone_number:
return jsonify({'error': 'Phone number is required'}), 400

# Validate the phone number format (e.g., E.164)
import re
if not re.match(r'^\+1?\d{9,15}$', phone_number):
return jsonify({'error': 'Invalid phone number format'}), 400

return jsonify({'message': 'Phone number is valid'}), 200

if __name__ == '__main__':
app.run(debug=True)