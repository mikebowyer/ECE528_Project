import boto3
import json
import requests

if __name__ == '__main__':
    # %% SETUP
    BUCKET_NAME = 'ktopolovbucket'
    stage_url = 'https://gt3l006seh.execute-api.us-east-1.amazonaws.com/deploymentStage'

    # Local files
    local_image_file = 'data/dashcams-2048px-20.jpg'
    test_method = 'local'  # 'local', 'api'

    # %% ShareImage Test
    print('\n===== Get Images in GPS Box TEST =====')

    # Setup PUT request HTTP body contents
    params = {
        "TL_Lat": 48.3,
        "TL_Long": -83.3,
        "BR_Lat": 41.3,
        "BR_Long": -83.2
    }
    # Send request
    request_url = stage_url + '/get-imgs-in-gps-box'
    print(request_url)
    # http_body_str = json.dumps(http_body)  # Must make string for put request
    get_imgs_in_gps_box_response = requests.get(url=request_url, params=params).json()
    print(get_imgs_in_gps_box_response)
