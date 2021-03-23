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

# Internal
from feature import features

# %% SETUP
BUCKET_NAME = 'ktopolovbucket'
stage_url = 'https://dy0duracgd.execute-api.us-east-1.amazonaws.com/dev'

# %% LOCAL FUNCTIONS
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
            'Day': integer
                Day of the month
            'Month': integer
                Month of the year
            'Year': integer
                Year
            'Hour': integer
                Hour of the day, 0 <= 23
            'Minute': integer
                Minute value 0 <= 59
            'Second': integer
                Second value 0 <= 59
            'ImageBase64': str
                Image encoded as a base64 string

    Returns
    -------
    response : dict
        Response dictionary containing:
            'statusCode': integer
                200 - success
                400 - something not provided properly
            'imageURL': str
                URL of image in s3 bucket
    """
    statusCode = 200  # default to success
    message = 'Success'

    bucket_name = 'ktopolovbucket'
    try:
        day = event['Day']
        month = event['Month']
        year = event['Year']
        hour = event['Hour']
        minute = event['Minute']
        second = event['Second']
        image_base64 = event['ImageBase64']
    except:
        statusCode = 400
        message = 'Missing at least one HTTP request parameter'

    # d for data, t for time
    ext = '.jpg'
    name = 'd{}-{}-{}-t-{}-{}-{}'.format(day, month, year, hour, minute, second)
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

# %%
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
# -- Upload with ShareImage
local_image_file = 'data/logo.png'
with open(local_image_file, 'rb') as file:
    image_bytes = file.read()
    image_base64 = base64.b64encode(image_bytes).decode()

http_body = {
    'Latitude': 40.0,
    'Longitude': 41.0,
    'Day': 25,
    'Month': 12,
    'Year': 2021,
    'Hour': 14,
    'Minute': 45,
    'Second': 22,
    'ImageBase64': image_base64}

response = share_image(event=http_body)

# -- Get JSON and read
jsons3 = get_json_s3(filename=response['jsonName'],
                     bucket_name=BUCKET_NAME)
json_str = jsons3['Body'].read().decode('utf-8')
json_dict = json.loads(json_str)
print(json_dict)

# -- Get Image and show
params = {'bucketName': BUCKET_NAME,
          'imageName': response['imageName']}
resp_dict = get_image_s3(http_request=params)
image_b64 = (resp_dict['imageBase64'])
im = Image.open(io.BytesIO(base64.b64decode(image_b64)))
plt.figure(0, clear=True)
plt.imshow(im)

# %% API TESTS
# -- Share Image
local_image_file = 'data/fries.jpg'
with open(local_image_file, 'rb') as file:
    image_bytes = file.read()
    image_base64 = base64.b64encode(image_bytes).decode()

http_body = {
    'Latitude': 40.0,
    'Longitude': 41.0,
    'Day': 24,
    'Month': 7,
    'Year': 2021,
    'Hour': 3,
    'Minute': 25,
    'Second': 2,
    'ImageBase64': image_base64}

command = '/share-image'
request_url = stage_url + command
response = requests.put(url=request_url,
                        data=json.dumps(http_body))  # Must dump to string for put request
resp_dict = response.json()

# -- Get JSON
params = {'fileName': resp_dict['jsonName'],
          'bucketName': 'ktopolovbucket'}  # key-value params in URL ?key=value&key1=...
command = '/get-json-s3'
request_url = stage_url + command
json_response = requests.get(url=request_url, params=params)
print(json_response.json())

# -- Get Image, decode and show
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


# %% Dictionaries for Testing
# Use for share_image HTTP body test
event = {
    "Latitude": 40,
    "Longitude": 41,
    "Day": 25,
    "Month": 12,
    "Year": 2021,
    "Hour": 14,
    "Minute": 45,
    "Second": 22,
    "ImageBase64": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAACAAIDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDyBYo5VEkkaO7jczMoJJPUk0UUVw15P2ster/Nn2NGlT9nH3Vsui7LyP/Z"
}

