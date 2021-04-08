import base64
import json

import requests
from PIL import Image
from flask import (Flask, render_template, jsonify, flash, request, redirect, url_for, send_from_directory)
from werkzeug.utils import secure_filename
import os
import os.path
from request_get_imgs_in_gpx_box import request_image_in_gps_box

try:
    import config
except ImportError:
    config = ''
    pass

creds = config.map_key if hasattr(config, 'map_key') else ""
BUCKET_NAME = 'ktopolovbucket'
stage_url = 'https://dy0duracgd.execute-api.us-east-1.amazonaws.com/dev'

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


@app.route('/')
def hello_world():
    return render_template('home.html')

@app.route('/map')
def map():
    global creds
    images = os.listdir(os.path.join(app.static_folder, "images"))
    test = 1
    try:
        if test == 1:
            markers = [{'info': {'labeled_image_source': 'https://ktopolovbucket.s3.amazonaws.com/labeled_1617555090.jpg',
                       'detected_labels': ['Car', 'Transportation'], 'human_readable_time': '2021-04-04 16:51:30',
                       'latitude': 30.03, 'longitude': 40.25,
                       'image_source': 'https://ktopolovbucket.s3.amazonaws.com/original_1617555090.jpg'},
              'image_uid': 'e7379859-b71a-4d0c-9f11-b07092d677aa', 'time': 1617555090}]
        else:
            markers = []
    except Exception as e:
        print(e)
        markers = ''
        pass

    return render_template('map.html', credentials=creds, imgs=images, markers=markers)

@app.route('/api_ref')
def api_ref():
    return render_template('api.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':

        lat = request.form['lat_in']
        long = request.form['long_in']
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        if file.filename != '' and '.' in file.filename and file.filename.split('.', 1)[1] in ALLOWED_EXTENSIONS:
            image_bytes = file.read()
            image_base64 = base64.b64encode(image_bytes).decode()

            http_body = {'Latitude': lat,
                         'Longitude': long,
                         'ImageBase64': image_base64}

            # Make Request
            request_url = stage_url + '/share-image'
            http_body_str = json.dumps(http_body)  # Must make string for put request
            share_image_response = requests.put(url=request_url, data=http_body_str).json()
            print(share_image_response)

    return render_template('upload.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run()
