|
from flask import Flask, request, jsonify
from .models.user import User, db

app = Flask(__name__)

# Initialize the database
def init_db():
db.create_all()

@app.route('/register', methods=['POST'])
def register():
data = request.get_json()
username = data['username']
password = data['password']
email = data['email']

user = User(username=username, password_hash=password, email=email)
db.session.add(user)
db.session.commit()

return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
data = request.get_json()
username = data['username']
password = data['password']

user = User.query.filter_by(username=username, password_hash=password).first()
if user:
return jsonify({'message': 'Login successful'}), 200
else:
return jsonify({'message': 'Invalid credentials'}), 401

if __name__ == '__main__':
init_db()
app.run(debug=True)