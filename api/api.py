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
import time

# Internal
from table_manager.dashcam_table_manager import DashcamTableManager
import feature.features as feat

# %% REQUEST FUNCTIONS
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
        image_base64 = event['ImageBase64']
    except:
        statusCode = 400
        message = 'Missing at least one HTTP request parameter'

    # Files stored with name '<epoch_time>.<ext>'
    epoch_time = int(time.time())
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
    label_names = []
    for label in labels:
        label_names.append(label['Name'])

    human_readable_time = time.strftime("%Y-%m-%d %H:%M:%S",
                                        time.gmtime(epoch_time))
    dynamo_meta = {'Latitude': lat,
                   'Longitude': lon,
                   'EpochTime': epoch_time,
                   'ImageURL': original_image_url,
                   'LabeledImageURL': labeled_image_url,
                   'humanReadableTime': human_readable_time,
                   'Labels': label_names}

    TableManager = DashcamTableManager("dashcam_images")
    TableManager.put_new_img(epochTime=dynamo_meta['EpochTime'],
                             humanReadableTime=dynamo_meta['humanReadableTime'],
                             lat=dynamo_meta['Latitude'],
                             long=dynamo_meta['Longitude'],
                             imgSrc=dynamo_meta['ImageURL'],
                             labeledImgSrc=dynamo_meta['LabeledImageURL'],
                             detectedLabels=dynamo_meta['Labels'])

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
