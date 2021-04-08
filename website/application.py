import base64
import json

import requests
from flask import (Flask, render_template, flash, request, redirect, send_from_directory)

import os
import os.path

try:
    import config
except ImportError:
    config = ''
    pass

creds = config.map_key if hasattr(config, 'map_key') else ""
BUCKET_NAME = 'ktopolovbucket'
stage_url = 'https://dy0duracgd.execute-api.us-east-1.amazonaws.com/dev'

application = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


@application.route('/')
def hello_world():
    return render_template('home.html')

@application.route('/map')
def map():
    global creds
    images = os.listdir(os.path.join(application.static_folder, "images"))
    test = 0
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

@application.route('/api_ref')
def api_ref():
    return render_template('api.html')

@application.route('/upload', methods=['GET', 'POST'])
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

@application.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(application.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    application.run('localhost', port=8000)
