# -*- coding: utf-8 -*-
"""
API to interface with data storage
"""
# %% IMPORTS
import boto3
import json
import base64
import io
import requests
from PIL import Image
import matplotlib.pyplot as plt

# %% SETUP
BUCKET_NAME = 'ktopolovbucket'
stage_url = 'https://dy0duracgd.execute-api.us-east-1.amazonaws.com/dev'

# %% LOCAL FUNCTIONS
def get_json_s3(filename, bucket_name):
    """
    Retrieve a JSON formatted file from an S3 bucket

    Parameters
    ----------
    bucket_path : str
        Path to the file

    filename : str
        Name of JSON-formatted file

    Returns
    -------
    json_string : str
        JSON-formatted string
    """
    s3 = boto3.resource('s3')
    content_object = s3.Object(bucket_name, filename)
    response = content_object.get()

    # Decode to JSON string with
    # response['Body'].read().decode('utf-8')
    return response

def get_image_s3(http_request):
    """
    Retrieve an image from an S3 bucket

    Parameters
    ----------
    http_request : dict
        HTTP Request; should have fields:
            'bucketName': str
                Name of S3 bucket

            'imageName': str
                Name of image within bucket

    Returns
    -------
    response : dict
        HTTP response. Contains:
            'statusCode': integer
                200 for okay, 400 for bad
            'bucketName': str
                Name of bucket
            'imageName': str
                Name of image
            'content': bytes
                Image as bytes
    """
    s3 = boto3.resource('s3')
    bucketname = http_request['bucketName']
    imagename = http_request['imageName']

    obj = s3.Object(bucketname, imagename)  # response
    # body = obj.get()['Body'].read()  # image as base64 encoded string

    file_stream = io.BytesIO()
    obj.download_fileobj(file_stream)
    image_bytes = file_stream.getvalue()
    image_base64 = base64.b64encode(image_bytes)
    
    response = {'bucketName': bucketname,
                'imageName': imagename,
                'imageBase64': image_base64,
                'statusCode': 200}
    # For base64 string, use:
    #   img_b64_str = base64.b64encode(response['bytes']).decode()

    return response

def put_json_s3(event):
    """
    Put a JSON formatted file into an S3 bucket

    Parameters
    ----------
    event : dict
        HTTP request body with parameters:
            bucketName : str
                Name of S3 bucket to store in
            itemName : str
                Name of file when stored in s3
            content : str
                JSON file contents

    Returns
    -------
    json_string : str
        JSON-formatted string
    """
    item_name = event['itemName']
    bucket_name = event['bucketName']
    json_str = json.dumps(event['content'])

    s3_client = boto3.client('s3')
    response = s3_client.put_object(
        Body=json_str,
        Bucket=bucket_name,
        Key=item_name)

# %% LOCAL FUNCTION TESTS
# FIXME-KT: Add try/catch to return more useful responses if item does not exist, etc.

# -- Get JSON
filename = 'sample_meta.json'  # MAKE SURE THIS FILE IS IN S3 BUCKET
jsons3 = get_json_s3(filename=filename, bucket_name=BUCKET_NAME)
json_str = jsons3['Body'].read().decode('utf-8')
json_dict = json.loads(json_str)
print(json_dict)

# -- Get Image
params = {'bucketName': BUCKET_NAME,
          'imageName': 'logo.png'}
resp_dict = get_image_s3(http_request=params)
image_b64 = (resp_dict['imageBase64'])
im = Image.open(io.BytesIO(base64.b64decode(image_b64)))
plt.figure(0, clear=True)
plt.imshow(im)

# -- Put JSON
local_filename = 'api/sample_meta.json'
with open(local_filename, 'r') as file:
    content = json.dumps(json.load(file))

body = {'bucketName': BUCKET_NAME,
        'itemName': 'hamsandwich.json',
        'content': content}
put_json_s3(event=body)

# %% API TESTS
# NOTE: Parameters like '?name=Kenny&age=22' can be given in 'params'

# -- TEST Function
command = '/test'
request_url = stage_url + command
r = requests.get(url=request_url, params={'name': 'Kenny', 'age': 22})
print(r.text)

# -- Get JSON
params = {'fileName': 'sample_meta.json',
          'bucketName': 'ktopolovbucket'}
command = '/get-json-s3'
request_url = stage_url + command
r = requests.get(url=request_url, params=params)
resp_dict = json.loads(r.text)
print(resp_dict)

# -- Get Image, decode and show
params = {'bucketName': BUCKET_NAME,
          'imageName': 'logo.png'}
command = '/get-image-s3'
request_url = stage_url + command
r = requests.get(url=request_url, params=params)
resp_dict = json.loads(r.text)
image_b64 = (resp_dict['imageBase64'])
im = Image.open(io.BytesIO(base64.b64decode(image_b64)))
plt.figure(1, clear=True)
plt.imshow(im)
plt.title('Retrieved and decoded from s3 bucket')

# -- Put JSON Function
filename = 'api/sample_meta.json'
with open(filename, 'r') as file:
    content = json.dumps(json.load(file))

body = {'bucketName': BUCKET_NAME,
        'itemName': 'bacon.json',
        'content': content}
body = json.dumps(body)

command = '/put-json-s3'
request_url = stage_url + command
r = requests.put(request_url, data=body)
# CHECK s3 for file!
