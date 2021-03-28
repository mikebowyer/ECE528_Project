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
    filename = filedialog.askopenfilename()
    file_str.set(filename)

def upload():
    """
    
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

    time.sleep(1.0)
    status_str.set(share_image_response['message'])
    window.update()


# %%
window = tk.Tk()
window.geometry("1400x500")

# -- Latitude
tk.Label(text='Latitude').grid(row=0, column=0)
lat_entry = tk.Entry()
lat_entry.grid(row=0, column=1)
lat_entry.insert(0, '41.53')

# -- Longitude
tk.Label(text='Longitude').grid(row=1, column=0)
long_entry = tk.Entry()
long_entry.grid(row=1, column=1)
long_entry.insert(0, '40.12')

# -- File Entry
browse_button = tk.Button(
    text="Browse",
    bd=3,
    height=3,
    width=10,
    bg='yellow',
    fg='black',
    command=get_filename).grid(row=2, column=0)

file_str = tk.StringVar()
file_str.set('')
file_entry = tk.Entry(textvariable=file_str)
file_entry.grid(row=2, column=1)

# -- Upload
upload_button = tk.Button(
    text="Upload",
    bd=3,
    height=3,
    width=10,
    bg='green',
    fg='white',
    command=upload).grid(row=3, column=0)
status_str = tk.StringVar()
status_str.set('')
status_label = tk.Label(textvariable=status_str)
status_label.grid(row=3, column=1)

tk.mainloop()
