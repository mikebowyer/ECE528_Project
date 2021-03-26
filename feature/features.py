# -*- coding: utf-8 -*-
"""
Provides functionality fr feature extraction from image data stored in S3
"""
# %% Imports
import boto3
import numpy as np
import matplotlib.pyplot as plt

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

def plot_image_and_box(image_array, labels):
    """
    Plot an image and corresponding bounding
    boxes of detected labels

    Parameters
    ----------
    img_array : [n_row, n_col, 3] np.array()
        Image array; can also be PIL Image

    labels : [n_label,] dict
        Returned from api.get_json() function or from
        Rekognition.detect_labels(). Each label has:
            'Name': str
                Name of the label detected
            'Instances': [n,] list of dict
                List of all instances found for this label. Each instance has:
                    'BoundingBox': dict
                        'Width': 0 <= decimal =< 1
                        'Height': 0 <= decimal =< 1
                        'Left': 0 <= decimal =< 1
                        'Top': 0 <= decimal =< 1

    Returns
    -------
    """
    n_row, n_col, _ = image_array.shape
    colors = [np.random.rand(3,) for _ in labels]

    plt.imshow(image_array)

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
    