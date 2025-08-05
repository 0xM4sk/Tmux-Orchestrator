|
# Availability windows input and storage
from flask import Flask, request, redirect
app = Flask(__name__)

@app.route('/add_availability')
def add_availability():
return 'Add availability page'

@app.route('/get_availability')
def get_availability():
return 'Get availability page'