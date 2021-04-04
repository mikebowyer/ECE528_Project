# -*- coding: utf-8 -*-
"""
Provides functionality fr feature extraction from image data stored in S3
"""
# %% Imports
import boto3
import random
from PIL import ImageDraw, Image, ImageFont
import io

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

    # trim out parts we don't want (confidence and parents)
    for label in labels:
        del label['Confidence']
        del label['Parents']

        for instance in label['Instances']:
            del instance['Confidence']        

    return labels

def label_image(image_bytes, labels):
    """
    Plot an image and corresponding bounding
    boxes of detected labels

    Parameters
    ----------
    image_bytes : bytes
        Image as bytes

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
    labeled_image_bytes : bytes
        Labeled image as bytes
    """
    labeled_image = Image.open(io.BytesIO(image_bytes))

    # Weird it gives size in this format
    n_col, n_row = labeled_image.size
    colors = [(int(random.uniform(0, 255)),
               int(random.uniform(0, 255)),
               int(random.uniform(0, 255))) for label in labels]

    # Draw original image
    d = ImageDraw.Draw(labeled_image)
    font = ImageFont.truetype("arial.ttf", 25)

    for color, label in zip(colors, labels):
        instances = label['Instances']
        for jj, instance in enumerate(instances):
            bounding_box = instance['BoundingBox']
            width = int(n_col * bounding_box['Width'])
            height = int(n_row * bounding_box['Height'])
            left = int(n_col * bounding_box['Left'])
            top = int(n_row * bounding_box['Top'])

            points = [(left, top),
                      (left, top + height),
                      (left + width, top + height),
                      (left + width, top),
                      (left, top)]

            color = tuple(color)
            d.line(points, fill=color, width=5)

            # Write label name
            d.text((left + 3, top + 3),
                   label['Name'],
                   fill=(255, 255, 255, 255),
                   font=font)

    labeled_image_bytes = io.BytesIO()
    labeled_image.save(labeled_image_bytes, format="JPEG")
    labeled_image_bytes = labeled_image_bytes.getvalue()
    return labeled_image_bytes

# %% Main script
if __name__ == '__main__':
    # Create a metadata dictionary for each image. This all should
    # come from our DynamoDB database
    bucket_name = 'ktopolovbucket'
    image_name = 'original_1616897414.6725974.jpg'
    max_labels = 5

    # Extract features for each, overwriting the image_metas
    print('Begin extracting features')
    labels = get_features(bucket_name=bucket_name,
                          image_name=image_name,
                          max_labels=max_labels)
    print('Done extracting features')
    print(labels)
