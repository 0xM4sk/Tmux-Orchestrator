|
from flask import Flask, request, redirect

app = Flask(__name__)

@app.route('/')
def index():
return "Hello, Strangers Calendar App!"

if __name__ == '__main__':
app.run(debug=True)