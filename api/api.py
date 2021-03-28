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
import time

# Internal
import feature.features as feat

# %% REQUEST FUNCTIONS
# These are simple functions that make use of the boto3 SDK provided
# by AWS to interact with AWS's different services. These functions are
# directly copied into AWS Lambda, where they are invoked by AWS API Gateway
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
                'message': 'Requested {} images w/ a {} in it'.format(
                    n_max, req_label),
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
            'EpochTime': decimal
                Time since epoch from time.time()
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
        epoch_time = event['EpochTime']
        image_base64 = event['ImageBase64']
    except:
        statusCode = 400
        message = 'Missing at least one HTTP request parameter'

    # Files stored with name '<epoch_time>.<ext>'
    base_image_name = '{}.jpg'.format(epoch_time)

    # -- Upload original image
    original_image_name = 'original_' + base_image_name
    original_image_bytes = base64.b64decode(image_base64)
    s3_client = boto3.client('s3')
    response = s3_client.put_object(
            Body=original_image_bytes,
            Bucket=bucket_name,
            Key=original_image_name,
            ACL='public-read')  # enable public read access
    original_image_url = 'https://{}.s3.amazonaws.com/{}'.format(
        bucket_name,
        original_image_name)

    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        statusCode = 500
        message = 'Unable to upload original image to S3'

    # -- Get labels
    labels = feat.get_features(bucket_name=bucket_name,
                               image_name=original_image_name,
                               max_labels=2)

    # -- Label image and store
    labeled_image_name = 'labeled_' + base_image_name
    labeled_image_bytes = feat.label_image(
        image_bytes=original_image_bytes,
        labels=labels)

    s3_client = boto3.client('s3')
    response = s3_client.put_object(
            Body=labeled_image_bytes,
            Bucket=bucket_name,
            Key=labeled_image_name,
            ACL='public-read')  # enable public read access
    labeled_image_url = 'https://{}.s3.amazonaws.com/{}'.format(
        bucket_name,
        labeled_image_name)
    
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        statusCode = 500
        message = 'Unable to upload labeled image to S3'

    # -- Replace this with storage into DynamoDB
    dynamo_meta = {'Latitude': lat,
                   'Longitude': lon,
                   'EpochTime': epoch_time,
                   'ImageURL': original_image_url,
                   'LabeledImageURL': labeled_image_url,
                   'Labels': labels}
    # dynamo.add_item(dynamo_meta)
    json_str = json.dumps(dynamo_meta)
    json_name = str(epoch_time) + '.json'
    response = s3_client.put_object(
        Body=json_str,
        Bucket=bucket_name,
        Key=json_name)

    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        statusCode = 500
        message = 'Unable to upload JSON to S3'

    # Send response back with a status code
    response = {'statusCode': statusCode,
                'message': message,
                'dynamoMeta': json.dumps(dynamo_meta)}
    return response

def get_json_s3(event):
    """
    Retrieve a JSON formatted file from an S3 bucket

    Parameters
    ----------
    event : dict
        Contains body (and Query key&val pairs if mapped)
        for HTTP request. HTTP request requires the following
        key&value pairs:

            bucketName : str
                Bucket name in S3 where file exists
            fileName : str
                Name of JSON-formatted file

    Returns
    -------
    json_string : str
        JSON-formatted string
    """
    bucket_name = event['bucketName']
    file_name = event['fileName']

    s3 = boto3.resource('s3')
    content_object = s3.Object(bucket_name=bucket_name,
                               key=file_name)
    response = content_object.get()

    json_str = response['Body'].read()
    json_dict = json.loads(json_str)

    out_dict = {
        'statusCode': 200,
        'bucketName': bucket_name,
        'fileName': file_name,
        'body': json_dict
    }

    # Decode to JSON string with
    # response['Body'].read().decode('utf-8')
    return out_dict

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
            
# %% TESTS
if __name__ == '__main__':
    # %% SETUP
    BUCKET_NAME = 'ktopolovbucket'
    stage_url = 'https://dy0duracgd.execute-api.us-east-1.amazonaws.com/dev'
    
    # Local files
    local_image_file = 'data/dashcams-2048px-20.jpg'
    
    test_method = 'api'  # 'local', 'api'

    # %% ShareImage Test
    print('\n===== ShareImage {} TEST ====='.format(test_method))
    
    # Read local image file
    with open(local_image_file, 'rb') as file:
        image_bytes = file.read()
        image_base64 = base64.b64encode(image_bytes).decode()

    # Setup PUT request HTTP body contents
    http_body = {'Latitude': 40.0,
                 'Longitude': 41.0,
                 # 'EpochTime': time.time(),
                 'EpochTime': 1616938736.101607,  # use this so i dont make 50 files
                 'ImageBase64': image_base64}
    
    # Send request
    if test_method == 'local':
        share_image_response = share_image(event=http_body)
    elif test_method == 'api':
        request_url = stage_url + '/share-image'
        http_body_str = json.dumps(http_body)  # Must make string for put request
        share_image_response = requests.put(url=request_url, data=http_body_str).json()
    else:
        raise ValueError('Unknown test_method {}'.format(test_method))

    dynamo_dict = json.loads(share_image_response['dynamoMeta'])
    print(dynamo_dict['ImageURL'])

    # %% GetJson Test
    print('\n===== GetJson {} TEST ====='.format(test_method))
    
    # JSON named with epoch_time.json()
    image_url = dynamo_dict['ImageURL']
    image_name = image_url.split('/')[-1]
    epoch_time = image_name.replace('original_', '').replace('.jpg', '')
    json_name = epoch_time + '.json'
    
    # Setup Query ?key&value pairs for HTTP request
    params = {'fileName': json_name,
              'bucketName': BUCKET_NAME}

    # Send request
    if test_method == 'local':
        json_response = get_json_s3(event=params)
    elif test_method == 'api':
        request_url = stage_url + '/get-json-s3'
        json_response = requests.get(url=request_url, params=params).json()
    else:
        raise ValueError('Unknown test_method {}'.format(test_method))
    
    print('\tstatusCode: {}'.format(json_response['statusCode']))
    
    json_body = json_response['body']
    labels = json_body['Labels']
    print('\t{} Labels Found'.format(len(labels)))
    
    # %% GetImage Test
    print('\n===== GetImage Local TEST =====')
    orig_image_url = dynamo_dict['ImageURL'].split('/')[-1]
    labeled_image_url = dynamo_dict['LabeledImageURL'].split('/')[-1]

    orig_params = {'bucketName': BUCKET_NAME,
                   'imageName': orig_image_url}

    # Send request
    if test_method == 'local':
        orig_image_response = get_image_s3(http_request=orig_params)
    
        labeled_params = {'bucketName': BUCKET_NAME,
                          'imageName': labeled_image_url}
        labeled_image_response = get_image_s3(http_request=labeled_params)
        
    elif test_method == 'api':
        request_url = stage_url + '/get-image-s3'
        orig_image_response = requests.get(
            url=request_url,
            params=orig_params).json()
        # labeled_image_response = requests.get(
        #     url=request_url,
        #     params=labeled_params).json()
    else:
        raise ValueError('Unknown test_method {}'.format(test_method))

    # Plot image and bounding boxes
    orig_image_b64 = orig_image_response['imageBase64']
    orig_image_bytes = base64.b64decode(orig_image_b64)
    pil_orig_image = Image.open(io.BytesIO(orig_image_bytes))
    plt.figure(1, clear=True)
    plt.subplot(1, 2, 1)
    plt.imshow(pil_orig_image)
    plt.title('Original Image')

    # Labeled image
    if test_method == 'api':
        labeled_image_b64 = labeled_image_response['imageBase64']
        labeled_image_bytes = base64.b64decode(labeled_image_b64)
        pil_label_image = Image.open(io.BytesIO(labeled_image_bytes))
        plt.subplot(1, 2, 2)
        plt.imshow(pil_label_image)
        plt.title('Labeled Image')

    # plt.subplot(1, 2, 2)
    # plt.imshow(labeled_image)
    # plt.title('Labeled Image')

    # %% GrabImages Test
    print('\n===== GrabImages API TEST =====')
    params = {'ReqLabel': 'Dog',
              'MaxNumImages': 5}

    # Send request
    if test_method == 'local':
        query_response = grab_images(event=params)
    elif test_method == 'api':
        request_url = stage_url + '/grab-images'
        query_response = requests.get(url=request_url,
                                      params=params).json()
    else:
        raise ValueError('Unknown test_method {}'.format(test_method))

    print(query_response)
