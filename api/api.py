# -*- coding: utf-8 -*-
"""
API to interface with data storage
"""
# %% IMPORTS
# External
import boto3
import json
import base64
import io
import requests
from PIL import Image
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

# Internal
from feature import features

# %% SETUP
BUCKET_NAME = 'ktopolovbucket'
stage_url = 'https://dy0duracgd.execute-api.us-east-1.amazonaws.com/dev'

# Local files
local_image_file = 'data/dashcams-2048px-20.jpg'

is_test_api = True
is_test_local = False

# %% LOCAL FUNCTIONS
def query_database(req_label, n_max):
    """
    Placeholder function
    """
    return ['URL1', 'URL2']

def grab_images(event):
    """
    Get image URLs from database

    Parameters
    ----------
    event : dict
        HTTP GET request with key-valu pairs:
            'ReqLabel': str
                Required label in image; must be supported by Rekognition
            'MaxNumImages': str
                Maximum number of images to return

    Returns
    -------
    response : dict
        Response dictionary containing:
            'statusCode': integer
                200 - success
                400 - something not provided properly
            'message': str
                Message describing status code
            'imageURLs': list of str
                List of image URLs found
    """
    n_max = event['MaxNumImages']
    req_label = event['ReqLabel']

    # Search DynamoDB for these images & return the URLs
    imageURLs = query_database(req_label=req_label, n_max=n_max)

    # IN PROGRESS
    response = {'statusCode': 200,
                'message': 'Requested {} images w/ a {} in it'.format(n_max,
                                                                      req_label),
                'imageURLs': json.dumps(imageURLs)}
    return response
    

def share_image(event):
    """
    Put an image into S3, and stickmetadata into DynamoDB

    Parameters
    ----------
    event : dict
        HTTP PUT request body, containing:
            'Latitude': decimal
                Latitude in degrees
            'Longitude': decimal
                Longitude in degrees
            'DateTimeStr': str
                data time string in format:
                    yyyy-mm-dd hh:mm:ss.mmmmmm
            'ImageBase64': str
                Image encoded as a base64 string

    Returns
    -------
    response : dict
        Response dictionary containing:
            'statusCode': integer
                200 - success
                400 - something not provided properly
            'message': str
                Message describing status code
            'imageURL': str
                URL of image in s3 bucket
            'imageName': str
                Name of image within bucket
            'jsonName': str
                Name of JSON within bucket
    """
    statusCode = 200  # default to success
    message = 'Success'

    bucket_name = 'ktopolovbucket'
    try:
        lat = event['Latitude']
        lon = event['Longitude']
        date_time_string = event['DateTimeStr']
        image_base64 = event['ImageBase64']
    except:
        statusCode = 400
        message = 'Missing at least one HTTP request parameter'

    # d for data, t for time
    ext = '.jpg'
    name = date_time_string # current date and time
    image_name = name + ext

    # -- Upload image
    image_bytes = base64.b64decode(image_base64)
    s3_client = boto3.client('s3')
    response = s3_client.put_object(
            Body=image_bytes,
            Bucket=bucket_name,
            Key=image_name,
            ACL='public-read')  # enable public read access
    del event['ImageBase64']  # delete bytes from metadata

    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        statusCode = 500
        message = 'Unable to upload image to S3'

    # -- Get URL
    image_url = 'https://{}.s3.amazonaws.com/{}'.format(bucket_name,
                                                        image_name)
    event['ImageURL'] = image_url

    # -- Get labels
    labels = features.get_features(bucket_name=bucket_name,
                                   image_name=image_name,
                                   max_labels=5)
    
    for label in labels:  # don't need this key
        del label['Parents']

    # Bounding boxes should be under labels['Instances']
    event['Labels'] = labels

    # -- Replace this with storage into DynamoDB
    json_str = json.dumps(event)
    ext = '.json'
    json_name = name + ext
    response = s3_client.put_object(
        Body=json_str,
        Bucket=bucket_name,
        Key=json_name)

    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        statusCode = 500
        message = 'Unable to upload JSON to S3'

    response = {'statusCode': statusCode,
                'message': message,
                'imageURL': image_url,
                'imageName': image_name,
                'jsonName': json_name}
    return response

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

# %% LOCAL FUNCTION TESTS
if is_test_local:
    # -- Upload with ShareImage
    print('===== ShareImage Local TEST =====')
    with open(local_image_file, 'rb') as file:
        image_bytes = file.read()
        image_base64 = base64.b64encode(image_bytes).decode()

    http_body = {
        'Latitude': 40.0,
        'Longitude': 41.0,
        # 'DateTimeStr': str(datetime.now()),
        'DateTimeStr': '2021-03-26 14:00:47.935047',
        'ImageBase64': image_base64}
    
    response = share_image(event=http_body)
    print('\tMessage: {}'.format(response['message']))
    
    # -- Get JSON that was just uploaded and read
    print('===== GetJson Local TEST =====')
    jsons3 = get_json_s3(filename=response['jsonName'],
                         bucket_name=BUCKET_NAME)
    json_str = jsons3['Body'].read().decode('utf-8')
    json_dict = json.loads(json_str)
    print(json_dict['ImageURL'])
    
    # -- Get Image and show
    print('===== GetImage Local TEST =====')
    params = {'bucketName': BUCKET_NAME,
              'imageName': response['imageName']}
    resp_dict = get_image_s3(http_request=params)
    image_b64 = (resp_dict['imageBase64'])
    im = Image.open(io.BytesIO(base64.b64decode(image_b64)))
    plt.figure(0, clear=True)
    plt.imshow(im)
    plt.title(resp_dict['imageName'])
    
    # -- Get Image URLs
    http_body = {'ReqLabel': 'Dog',
                 'MaxNumImages': 5}
    response = grab_images(event=http_body)
    print(response)

# %% API TESTS
if is_test_api:
    # -- Share Image
    print('===== ShareImage API TEST =====')
    with open(local_image_file, 'rb') as file:
        image_bytes = file.read()
        image_base64 = base64.b64encode(image_bytes).decode()

    http_body = {
        'Latitude': 40.0,
        'Longitude': 41.0,
        
        # Should get current data/time, but for now
        # just give same name every time
        # 'DateTimeStr': str(datetime.now()),
        'DateTimeStr': '2021-03-26 14:00:47.935047',
        'ImageBase64': image_base64}

    command = '/share-image'
    request_url = stage_url + command
    response = requests.put(url=request_url,
                            data=json.dumps(http_body))  # Must dump to string for put request
    resp_dict = response.json()
    
    # -- Get JSON
    print('===== GetJson API TEST =====')
    params = {'fileName': resp_dict['jsonName'],
              'bucketName': 'ktopolovbucket'}  # key-value params in URL ?key=value&key1=...
    command = '/get-json-s3'
    request_url = stage_url + command
    json_response = requests.get(url=request_url, params=params)
    json_data = json_response.json()
    print('\tStatus Code: {}'.format(json_data['statusCode']))
    
    # -- Get Image, decode and show
    print('===== GetImage API TEST =====')
    params = {'bucketName': BUCKET_NAME,
              'imageName': resp_dict['imageName']}
    command = '/get-image-s3'
    request_url = stage_url + command
    image_response = requests.get(url=request_url, params=params)
    image_dict = image_response.json()
    image_b64 = (image_dict['imageBase64'])
    im = Image.open(io.BytesIO(base64.b64decode(image_b64)))
    plt.figure(1, clear=True)
    plt.imshow(im)
    plt.title('Retrieved and decoded from s3 bucket')

    # -- Query images
    params = {'MaxNumImages': 3,
              'ReqLabel': 'Cat'}
    command = '/grab-images'
    request_url = stage_url + command
    image_query_response = requests.get(url=request_url, params=params)
    
    print(image_query_response.json())

# %% Plot Bounding Box
plt.figure(2, clear=True)
img_array = np.array(im)
plt.imshow(img_array)
plt.title('Retrieved Image w/ Bounding Boxes')

json_data = json_response.json()
labels = json_data['body']['Labels']
n_row, n_col, _ = img_array.shape
colors = [np.random.rand(3,) for _ in labels]

for ii, label in enumerate(labels):
    print('Label found: {}'.format(label['Name']))
    instances = label['Instances']
    for instance in instances:
        bounding_box = instance['BoundingBox']
        width = bounding_box['Width']
        height = bounding_box['Height']
        left = bounding_box['Left']
        top = bounding_box['Top']

        row = n_col * (left + np.array([0, 0, width, width, 0]))
        col = n_row * (top + np.array([0, height, height, 0, 0]))

        plt.plot(row, col, color=colors[ii])
        