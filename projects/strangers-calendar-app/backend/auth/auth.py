|
from flask import Flask, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models import db, User

app = Flask(__name__)

@app.route('/register', methods=['GET', 'POST'])
def register():
if request.method == 'POST':
username = request.form['username']
email = request.form['email']
password = request.form['password']

user_exists = User.query.filter_by(username=username).first()
if user_exists:
flash('Username already exists.')
return redirect(url_for('register'))

hashed_password = generate_password_hash(password)
new_user = User(username=username, email=email, password=hashed_password)
db.session.add(new_user)
db.session.commit()
flash('User registered successfully!')
return redirect(url_for('login'))
return '''
<form method="post">
Username: <input type="text" name="username"><br>
Email: <input type="email" name="email"><br>
Password: <input type="password" name="password"><br>
<input type="submit" value="Register">
</form>
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
if request.method == 'POST':
username = request.form['username']
password = request.form['password']

user = User.query.filter_by(username=username).first()
if user and check_password_hash(user.password, password):
session['user_id'] = user.id
flash('Logged in successfully!')
return redirect(url_for('home'))
else:
flash('Invalid username or password.')
return '''
<form method="post">
Username: <input type="text" name="username"><br>
Password: <input type="password" name="password"><br>
<input type="submit" value="Login">
</form>
'''

@app.route('/logout')
def logout():
session.pop('user_id', None)
flash('Logged out successfully!')
return redirect(url_for('login'))

@app.route('/')
def home():
if 'user_id' in session:
return f'Welcome, {session["username"]}!'
else:
return redirect(url_for('login'))