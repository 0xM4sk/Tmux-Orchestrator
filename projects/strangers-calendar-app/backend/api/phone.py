|
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash

app = Flask(__name__)

@app.route('/api/phone', methods=['POST'])
def add_phone_number():
data = request.get_json()
phone_number = data.get('phoneNumber')

if not phone_number:
return jsonify({'error': 'Phone number is required'}), 400

# Hash the phone number for security
hashed_phone = generate_password_hash(phone_number)

# Store the hashed phone number in a database (simulated here)
db = {
'hashed_phone': hashed_phone
}

return jsonify({'message': 'Phone number added successfully', 'data': db}), 201

if __name__ == '__main__':
app.run(debug=True)