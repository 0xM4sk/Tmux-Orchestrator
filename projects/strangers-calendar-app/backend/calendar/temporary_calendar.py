|
# Temporary calendar implementation
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

def create_temporary_calendar():
data = request.get_json()
user_id = data.get('user_id')
start_time = datetime.strptime(data.get('start_time'), '%Y-%m-%d %H:%M:%S')
end_time = datetime.strptime(data.get('end_time'), '%Y-%m-%d %H:%M:%S')

# Simulate calendar creation
temp_calendar = {
'user_id': user_id,
'start_time': start_time,
'end_time': end_time
}

return jsonify(temp_calendar), 201

@app.route('/calendar/temporary', methods=['POST'])
def handle_temporary_calendar():
return create_temporary_calendar()

if __name__ == '__main__':
app.run(debug=True)