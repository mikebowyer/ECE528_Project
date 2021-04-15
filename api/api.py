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
from table_manager.events_table_manager import EventTableManager
import feature.features as feat


# %% Lambda function used for share_image in AWS LAMBDA
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

    # Use default AWS model and custom model; combine results
    labels = feat.get_features(bucket_name=bucket_name,
                               image_name=original_image_name,
                               max_labels=2)
    custom_labels = feat.get_custom_features(bucket_name=bucket_name,
                                             image_name=original_image_name)
    labels = labels + custom_labels

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
                                        time.gmtime(epoch_time - 4 * 60 * 60))
    dynamo_meta = {'Latitude': lat,
                   'Longitude': lon,
                   'EpochTime': epoch_time,
                   'ImageURL': original_image_url,
                   'LabeledImageURL': labeled_image_url,
                   'humanReadableTime': human_readable_time,
                   'Labels': label_names}

    TableManager = DashcamTableManager("dashcam_images")
    new_img = TableManager.put_new_img(epochTime=dynamo_meta['EpochTime'],
                                     humanReadableTime=dynamo_meta['humanReadableTime'],
                                     lat=dynamo_meta['Latitude'],
                                     long=dynamo_meta['Longitude'],
                                     imgSrc=dynamo_meta['ImageURL'],
                                     labeledImgSrc=dynamo_meta['LabeledImageURL'],
                                     detectedLabels=dynamo_meta['Labels'])

    # Check events
    EventMan = EventTableManager('Events')
    
    detected_label_associations = EventMan.check_if_img_matches_any_events(new_img)
    print("Events this image should be associated with: \n {}".format(detected_label_associations))

    if not detected_label_associations:
        print("No events could be associated with this image, so creating new event.")
        supported_events = ['Construction', 'Deer']
        
        for event_type in supported_events:
            if event_type in new_img['info']['detected_labels']:
                put_success = EventMan.put_new_event(event_type, new_img)
    else:
        print("At least one event found associated to this image, making associations.")
        for detected_label_association in detected_label_associations:
            for event_to_associate in detected_label_association:
                event_time = event_to_associate['start_time']
                event_uid = event_to_associate['event_uid']
                result = EventMan.update_event_using_new_img(event_time,
                                                            event_uid,
                                                            new_image_to_associate=new_img)
                if not result:
                    raise Exception("Sorry, had problems associating image to event")

    # Response
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        statusCode = 500
        message = 'Unable to upload JSON to S3'

    # Send response back with a status code
    response = {'statusCode': statusCode,
                'message': message,
                'dynamoMeta': json.dumps(dynamo_meta)}
    return response

def getEvents(event):
    """
    Get images from database within a GPS bounding box

    Parameters
    ----------
    event : dictionary
        Contains the following:
            TL_Lat : decimal
                Top-left latitude (Degrees) of GPS bounding box
            TL_Long : decimal
                Top-left longitude (Degrees) of GPS bounding box
            BR_Lat : decimal
                Bottom-right latitude (Degrees) of GPS bounding box
            BR_Long : decimal
                Bottom-right longitude (Degrees) of GPS bounding box
            freshness_limit : string (optional)
                Specifies how fresh results from this query must be so old data isn't included
            event_type : string (optional)
                Filter to only include results which include this event_type in the image

    Returns
    -------
    response : dictionary
        Contains the following:
            statusCode : integer
                200 for good, other for bad
            message : str
                Received message
            body : list
                Contains dictionary items corresponding to each found result 
    """
    try:
        tl_lat = float(event['TL_Lat'])
        tl_long = float(event['TL_Long'])
        br_lat = float(event['BR_Lat'])
        br_long = float(event['BR_Long'])
        freshness_limit = int(0)
        event_type = ""

        if 'freshness_limit' in event:
            if event['freshness_limit'] != "":
                freshness_limit = int(event['freshness_limit'])
        if 'event_type' in event:
            event_type = event['event_type']
    except:
        print("ERROR")
        response = {'statusCode': 400, 'message': 'RecievedMessage: {}'.format(event), 'body': 'Base request'}
        return response

    table_manager = EventTableManager("Events")
    results = table_manager.get_events_in_GPS_bounds(tl_lat, tl_long, br_lat, br_long, freshness_limit, event_type)

    response = {'statusCode': 200,
                'message': 'RecievedMessage: {}'.format(event), 'body': results}

    return response


# %% Lambda function used for "getDashcamImages" AWS LAMBDA
def getDashcamImages(event):
    """
    Get images from database within a GPS bounding box

    Parameters
    ----------
    event : dictionary
        Contains the following:
            TL_Lat : decimal
                Top-left latitude (Degrees) of GPS bounding box
            TL_Long : decimal
                Top-left longitude (Degrees) of GPS bounding box
            BR_Lat : decimal
                Bottom-right latitude (Degrees) of GPS bounding box
            BR_Long : decimal
                Bottom-right longitude (Degrees) of GPS bounding box
            freshness_limit : string (optional)
                Specifies how fresh results from this query must be so old data isn't included
            detected_label : string (optional)
                Filter to only include results which include this detected label in the image

    Returns
    -------
    response : dictionary
        Contains the following:
            statusCode : integer
                200 for good, other for bad
            message : str
                Received message
            body : list
                Contains dictionary items corresponding to each found result 
    """
    try:
        tl_lat = float(event['TL_Lat'])
        tl_long = float(event['TL_Long'])
        br_lat = float(event['BR_Lat'])
        br_long = float(event['BR_Long'])
        freshness_limit = int(0)
        detected_label = ""

        if 'freshness_limit' in event:
            if event['freshness_limit'] != "":
                freshness_limit = int(event['freshness_limit'])
        if 'detected_label' in event:
            detected_label = event['detected_label']
    except:
        print("ERROR")
        response = {'statusCode': 400, 'message': 'RecievedMessage: {}'.format(event), 'body': 'Base request'}
        return response

    table_manager = DashcamTableManager("dashcam_images")
    results = table_manager.get_imgs_in_GPS_bounds(tl_lat, tl_long, br_lat, br_long, freshness_limit, detected_label)

    response = {'statusCode': 200,
                'message': 'RecievedMessage: {}'.format(event), 'body': results}

    return response


# %% Lambda function used for get_image_s3 in AWS LAMBDA
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
