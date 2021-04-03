import json


def lambda_handler(event, context):
    try:
        tl_lat = event['TL_Lat']
        tl_long = event['TL_Long']
        br_lat = event['BR_Lat']
        br_long = event['BR_Long']
    except:
        response = {'statusCode': 400,
                    'message': 'RecievedMessage: {}'.format(event), 'body': 'Base request'}

    print(event['BR_Lat'])
    response = {'statusCode': 200,
                'message': 'RecievedMessage: {}'.format(event), 'body': json.dumps(event)}

    return response
