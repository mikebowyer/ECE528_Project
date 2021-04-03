from flask import (Flask, render_template, jsonify, request, url_for, send_from_directory)
import os
import os.path
import db
try:
    import config
except ImportError:
    config = ''
    pass

creds = config.map_key if hasattr(config, 'map_key') else ""

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('home.html')

@app.route('/map')
def map():
    global creds
    images = os.listdir(os.path.join(app.static_folder, "images"))
    try:
        markers = db.get_items()
    except:
        markers = ''
        pass

    return render_template('map.html', credentials=creds, imgs=images, markers=markers)

@app.route('/api_ref')
def api_ref():
    return render_template('api.html')

@app.route('/upload')
def api():
    return render_template('upload.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run()
