|
from flask import Flask, redirect, url_for
from backend.auth.oauth import app as oauth_app
from backend.auth.apple import app as apple_app
from backend.auth.whatsapp import send_whatsapp_message

app = Flask(__name__)

app.register_blueprint(oauth_app, url_prefix='/login')
app.register_blueprint(apple_app, url_prefix='/apple')

@app.route('/register', methods=['POST'])
def register():
phone_number = request.form.get('phone_number')
if not validate_phone_number(phone_number):
return "Invalid phone number", 400
user_id = create_user(phone_number)
send_whatsapp_message(phone_number, f"Welcome to our service! Your ID is {user_id}")
return redirect(url_for('login'))

@app.route('/login', methods=['GET'])
def login():
# Implement login logic here
pass

if __name__ == '__main__':
app.run(debug=True)