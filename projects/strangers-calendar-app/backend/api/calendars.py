|
from flask import Blueprint, jsonify

calendars_bp = Blueprint('calendars', __name__)

@calendars_bp.route('/api/calendars', methods=['GET'])
def get_calendars():
# Example data
calendars = [
{'id': 1, 'title': 'Meeting', 'start': '2023-04-01T10:00:00Z', 'end': '2023-04-01T11:00:00Z'},
{'id': 2, 'title': 'Lunch', 'start': '2023-04-01T12:00:00Z', 'end': '2023-04-01T13:00:00Z'}
]
return jsonify(calendars)