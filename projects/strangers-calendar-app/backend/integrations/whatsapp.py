|
from flask import Flask, request, jsonify

app = Flask(__name__)

# Endpoint to send a WhatsApp message
@app.route('/send_whatsapp_message', methods=['POST'])
def send_whatsapp_message():
phone_number = request.json.get('phone_number')
message = request.json.get('message')

if not phone_number or not message:
return jsonify({'error': 'Phone number and message are required'}), 400

# Simulate sending a WhatsApp message
return jsonify({'status': 'success', 'message': f'Message sent to {phone_number}: {message}'})

if __name__ == '__main__':
app.run(debug=True)