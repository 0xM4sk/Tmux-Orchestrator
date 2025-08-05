|
from flask import Flask, request, jsonify
from .oauth2 import require_auth
from .integrations.whatsapp import app as whatsapp_app
from .calendars import app as calendars_app
from .availability import app as availability_app
from .intersection import app as intersection_app
from .cleanup import app as cleanup_app

app = Flask(__name__)

app.register_blueprint(whatsapp_app, url_prefix='/api/whatsapp')
app.register_blueprint(calendars_app, url_prefix='/api/calendars')
app.register_blueprint(availability_app, url_prefix='/api/availability')
app.register_blueprint(intersection_app, url_prefix='/api/intersection')
app.register_blueprint(cleanup_app, url_prefix='/api/cleanup')

@app.route('/api/test', methods=['GET'])
def test():
return jsonify({'status': 'success', 'message': 'API is working'})