|
# Availability intersection algorithm
from flask import Flask, request, redirect
app = Flask(__name__)

@app.route('/intersect_availability')
def intersect_availability():
return 'Intersect availability page'