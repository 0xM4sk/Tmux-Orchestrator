|
from flask import Flask, request, jsonify

app = Flask(__name__)

# Endpoint to create a calendar
@app.route('/create_calendar', methods=['POST'])
def create_calendar():
name = request.json.get('name')

if not name:
return jsonify({'error': 'Calendar name is required'}), 400

# Simulate creating a calendar
return jsonify({'status': 'success', 'message': f'Calendar {name} created'})

# Endpoint to share a calendar
@app.route('/share_calendar', methods=['POST'])
def share_calendar():
calendar_id = request.json.get('calendar_id')
email = request.json.get('email')

if not calendar_id or not email:
return jsonify({'error': 'Calendar ID and email are required'}), 400

# Simulate sharing a calendar
return jsonify({'status': 'success', 'message': f'Calendar {calendar_id} shared with {email}'})