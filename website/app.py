from flask import (Flask, render_template, jsonify, request, url_for)
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
    markers = db.get_items()

    return render_template('map.html', credentials=creds, imgs=images, markers=markers)

@app.route('/get-items')
def get_items():
    return str(db.get_items())


if __name__ == '__main__':
    app.run()
