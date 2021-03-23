from flask import Flask
from flask import render_template
from flask import request
import config
creds = config.map_key

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('home.html')

@app.route('/map')
def map():
    global creds
    return render_template('map.html', credentials=creds)


if __name__ == '__main__':
    app.run()
