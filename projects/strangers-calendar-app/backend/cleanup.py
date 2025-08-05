|
# Calendar expiration and cleanup
from flask import Flask, request, redirect
app = Flask(__name__)

@app.route('/cleanup_calendar')
def cleanup_calendar():
return 'Cleanup calendar page'