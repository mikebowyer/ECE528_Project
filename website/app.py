from flask import (Flask, render_template, request, url_for)
import os, os.path
import config
creds = config.map_key

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('home.html')

@app.route('/map')
def map():
    global creds
    images = os.listdir(os.path.join(app.static_folder, "images"))
    return render_template('map.html', credentials=creds, imgs=images)


if __name__ == '__main__':
    app.run()
