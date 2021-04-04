# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 11:12:34 2021

@author: ktopo
"""
import tkinter as tk
import json
import requests
from tkinter import filedialog
import time
import base64

# GLOBALS
stage_url = 'https://dy0duracgd.execute-api.us-east-1.amazonaws.com/dev'

# %% FUNCTIONS
def get_filename():
    """
    Get name of file using filedialog browser

    Paremters
    ---------

    Returns
    -------
    """
    filename = filedialog.askopenfilename()
    file_str.set(filename)

def upload():
    """
    Upload a local image with metadata using API

    Parameters
    ----------

    Returns
    -------
    """
    status_str.set('UPLOADING')
    window.update()

    # Open image and encode
    with open(file_entry.get(), 'rb') as file:
        image_bytes = file.read()
        image_base64 = base64.b64encode(image_bytes).decode()

    # Setup PUT request HTTP body contents
    http_body = {'Latitude': float(lat_entry.get()),
                 'Longitude': float(long_entry.get()),
                 'ImageBase64': image_base64}

    request_url = stage_url + '/share-image'
    http_body_str = json.dumps(http_body)  # Must make string for put request
    share_image_response = requests.put(url=request_url, data=http_body_str).json()
    dynamo_meta = json.loads(share_image_response['dynamoMeta'])

    time.sleep(1.0)
    status_str.set('Uploaded to {} and \n{}'.format(
        dynamo_meta['ImageURL'], dynamo_meta['LabeledImageURL']))
    window.update()


# %% CREATE UI
window = tk.Tk()
window.geometry("1400x500")

# -- Title
tk.Label(text='Data Collection Uploader', font=("Arial", 25)).grid(
    row=0, column=0, rowspan=1, columnspan=2)

# -- Latitude
tk.Label(text='Latitude', font=("Arial", 16)).grid(row=1, column=0)
lat_entry = tk.Entry(font=("Arial", 16))
lat_entry.grid(row=1, column=1)

# -- Longitude
tk.Label(text='Longitude', font=("Arial", 16)).grid(row=2, column=0)
long_entry = tk.Entry(font=("Arial", 16))
long_entry.grid(row=2, column=1)

# -- File Entry
browse_button = tk.Button(
    text="Browse",
    bd=3,
    height=2,
    width=10,
    bg='yellow',
    fg='black',
    font=("Arial", 16),
    command=get_filename).grid(row=3, column=0)

file_str = tk.StringVar()
file_str.set('')
file_entry = tk.Entry(textvariable=file_str,
                      font=("Arial", 16),
                      width=20)
file_entry.grid(row=3, column=1)

# -- Upload
upload_button = tk.Button(
    text="Upload",
    bd=3,
    height=2,
    width=10,
    bg='green',
    fg='white',
    font=("Arial", 16),
    command=upload).grid(row=4, column=0)
status_str = tk.StringVar()
status_str.set('')
status_label = tk.Label(textvariable=status_str,
                        font=("Arial", 16))
status_label.grid(row=4, column=1)

tk.mainloop()
