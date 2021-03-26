# -*- coding: utf-8 -*-
"""
Provides functionality fr feature extraction from image data stored in S3
"""
# %% Imports
import boto3

# %% Functions
def get_features(bucket_name, image_name, max_labels=5):
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
    S3_Object = {'Bucket': bucket_name,
                 'Name': image_name}
    response = rekog_client.detect_labels(Image={'S3Object': S3_Object},
                                          MaxLabels=max_labels)
    labels = response['Labels']
    return labels

# %% Main script
if __name__ == '__main__':
    # Create a metadata dictionary for each image. This all should
    # come from our DynamoDB database
    bucket_name = 'ktopolovbucket'
    image_name = 'd25-12-2021-t-14-45-22.jpg'
    max_labels = 5

    # Extract features for each, overwriting the image_metas
    print('Begin extracting features')
    labels = get_features(bucket_name=bucket_name,
                               image_name=image_name,
                               max_labels=max_labels)
    print('Done extracting features')
    print(labels)
    