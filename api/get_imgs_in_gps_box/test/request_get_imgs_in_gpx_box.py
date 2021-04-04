import boto3
import json
import requests

if __name__ == '__main__':
    # %% SETUP
    BUCKET_NAME = 'ktopolovbucket'
    stage_url = 'https://dy0duracgd.execute-api.us-east-1.amazonaws.com/deploymentStage'

    # %% ShareImage Test
    print('\n===== Get Images in GPS Box TEST =====')

    # Setup PUT request HTTP body contents
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
    print(request_url)
    # http_body_str = json.dumps(http_body)  # Must make string for put request
    get_imgs_in_gps_box_response = requests.get(url=request_url, params=params).json()
    print(get_imgs_in_gps_box_response)
