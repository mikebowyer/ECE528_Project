# -*- coding: utf-8 -*-
"""
Provides functionality fr feature extraction from image data stored in S3
"""
# %% Imports
import boto3

# %% Functions
def get_features(image_metas, max_labels=10):
    """
    Extract important features from images located in the provided S3 paths

    Parameters
    ----------
    image_metas : [n,] dict
        List of dictionaries; each containing image metadata:
            {
                'bucket': 'myBucket/subBucket',
                'filename': 'image.jpg',
                'time': ...,
                'date': ...,
                'latitude': 40.1,
                'longitude': 22.7,
                'altitude': 1523.2
            }
            containing the full file path and location to each
        image within the S3 database. Ex: 'myBucket/subBucket/image.png'

    Returns
    -------
    image_metas : [n,] dict
        Image metadata with 'labels' key added
    """
    # Begin Rekognition client
    rekog_client = boto3.client('rekognition')

    for meta in image_metas:
        S3_Object = {'Bucket': meta['bucket'],
                     'Name': meta['filename']}
        response = rekog_client.detect_labels(Image={'S3Object': S3_Object},
                                              MaxLabels=max_labels)
        meta['labels'] = response['Labels']

    return image_metas

# %% Main script
if __name__ == '__main__':
    # Create a metadata dictionary for each image. This all should
    # come from our DynamoDB database
    bucket = 'ktopolovbucket'

    meta1 = {'bucket': bucket,
             'filename': 'logo.png',
             'time': '13/45/02',  # hour/minute/second
             'date': '01/09/2021',  # MM/DD/YYYY
             'latitude': 40.1,
             'longitude': 22.7,
             'altitude': 1523.2}

    # Store in single list
    image_metas = [meta1]

    # Extract features for each, overwriting the image_metas
    print('Begin extracting features')
    image_metas = get_features(image_metas)
    print('Done extracting features')
    