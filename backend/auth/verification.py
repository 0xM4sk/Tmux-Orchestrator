|
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/verify_phone', methods=['POST'])
def verify_phone():
data = request.get_json()
phone_number = data.get('phone_number')

if not phone_number:
return jsonify({'error': 'Phone number is required'}), 400

# Perform validation on the phone number
if not phone_number.startswith('+'):
return jsonify({'error': 'Phone number must start with "+"'}), 400

# Simulate sending a verification code (in practice, this would involve sending an SMS)
verification_code = "123456"

# Store the verification code and its expiration time in the database
# For simplicity, we'll use a dictionary for demonstration purposes
verification_codes[phone_number] = {
'code': verification_code,
'expiration_time': datetime.datetime.now() + datetime.timedelta(minutes=10)
}

return jsonify({'message': f'Verification code sent to {phone_number}', 'verification_code': verification_code}), 200

if __name__ == '__main__':
app.run(debug=True)