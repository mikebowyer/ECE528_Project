# -*- coding: utf-8 -*-
"""
Created on Sun Apr  4 18:48:31 2021

@author: ktopo
"""
import requests
from PIL import Image
import matplotlib.pyplot as plt
import base64
import json
import io

# %% SETUP
BUCKET_NAME = 'ktopolovbucket'
stage_url = 'https://dy0duracgd.execute-api.us-east-1.amazonaws.com/dev'

# Local files
# local_image_file = 'data/dashcams-2048px-20.jpg'
local_image_file = 'C:/Users/ktopo/Desktop/School/Courses/Masters/ECE 528 - Cloud Computing/project/data/construction/BQ44GBLRMVHJNFO5UICX3O5SBI.jpg'
# local_image_file = 'C:/Users/ktopo/Desktop/School/Courses/Masters/ECE 528 - Cloud Computing/project/data/deer_crossing/hqdefault.jpg'

# %% 1) ShareImage Test
# Test name
print('\n===== ShareImage TEST =====')

# Setup inputs
with open(local_image_file, 'rb') as file:
    image_bytes = file.read()
    image_base64 = base64.b64encode(image_bytes).decode()

http_body = {'Latitude': 40.0,
             'Longitude': 41.0,
             'ImageBase64': image_base64}

# Make Request
request_url = stage_url + '/share-image'
http_body_str = json.dumps(http_body)  # Must make string for put request
share_image_response = requests.put(url=request_url, data=http_body_str).json()

# Print results
dynamo_dict = json.loads(share_image_response['dynamoMeta'])
print(dynamo_dict['ImageURL'])

# %% 2) GetImage Test
# Test name
print('\n===== GetImage Local TEST =====')

# Setup inputs
orig_image_url = dynamo_dict['ImageURL'].split('/')[-1]
labeled_image_url = dynamo_dict['LabeledImageURL'].split('/')[-1]
orig_params = {'bucketName': BUCKET_NAME,
               'imageName': orig_image_url}
labeled_params = {'bucketName': BUCKET_NAME,
                  'imageName': labeled_image_url}

# Make Request
request_url = stage_url + '/get-image-s3'
orig_image_response = requests.get(
    url=request_url,
    params=orig_params).json()
labeled_image_response = requests.get(
    url=request_url,
    params=labeled_params).json()

# Show output images
orig_image_b64 = orig_image_response['imageBase64']
orig_image_bytes = base64.b64decode(orig_image_b64)
pil_orig_image = Image.open(io.BytesIO(orig_image_bytes))
plt.figure(1, clear=True)
plt.subplot(1, 2, 1)
plt.imshow(pil_orig_image)
plt.title('Original Image')

labeled_image_b64 = labeled_image_response['imageBase64']
labeled_image_bytes = base64.b64decode(labeled_image_b64)
pil_label_image = Image.open(io.BytesIO(labeled_image_bytes))
plt.subplot(1, 2, 2)
plt.imshow(pil_label_image)
plt.title('Labeled Image')

# %% 3) Get Images in GPS Box
# Test name
print('\n===== get-imgs-in-gps-box Local TEST =====')

# Setup inputs
params = { #These coordinates have dynamoDB entries in them
    "TL_Lat": 0.0,
    "TL_Long": 0.0,
    "BR_Lat": 180.0,
    "BR_Long": 180.0
}

# params = { #These coordiantes DO NOT have dynamoDB entries in them
#     "TL_Lat": 42.410831,
#     "TL_Long": -83.413774,
#     "BR_Lat": 42.396622,
#     "BR_Long": -83.402775
# }

# Send request
request_url = stage_url + '/get-imgs-in-gps-box'
get_imgs_in_gps_box_response = requests.get(url=request_url, params=params).json()

# Print results
print('Found {} repsonses: '.format(len(get_imgs_in_gps_box_response['body'])))
for item in get_imgs_in_gps_box_response['body']:
    print('\t{}'.format(item['info']['labeled_image_source']))
