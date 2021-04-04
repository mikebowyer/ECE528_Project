import boto3
import json
import requests

if __name__ == '__main__':
    # %% SETUP
    BUCKET_NAME = 'ktopolovbucket'
    stage_url = 'https://dy0duracgd.execute-api.us-east-1.amazonaws.com/deploymentStage'

    # Local files
    local_image_file = 'data/dashcams-2048px-20.jpg'
    test_method = 'local'  # 'local', 'api'

    # %% ShareImage Test
    print('\n===== Get Images in GPS Box TEST =====')

    # Setup PUT request HTTP body contents
    params = { #These coordiantes have dynamoDB entries in them
        "TL_Lat": 42.396622,
        "TL_Long": -83.402775,
        "BR_Lat": 42.383067,
        "BR_Long": -83.372909
    }

    # params = { #These coordiantes DO NOT have dynamoDB entries in them
    #     "TL_Lat": 42.410831,
    #     "TL_Long": -83.413774,
    #     "BR_Lat": 42.396622,
    #     "BR_Long": -83.402775
    # }


    # Send request
    request_url = stage_url + '/get-imgs-in-gps-box'
    print(request_url)
    # http_body_str = json.dumps(http_body)  # Must make string for put request
    get_imgs_in_gps_box_response = requests.get(url=request_url, params=params).json()
    print(get_imgs_in_gps_box_response)
