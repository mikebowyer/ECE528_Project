import json
from table_manager.dashcam_table_manager import DashcamTableManager

def lambda_handler(event, context):
    try:
        tl_lat = float(event['TL_Lat'])
        tl_long = float(event['TL_Long'])
        br_lat = float(event['BR_Lat'])
        br_long = float(event['BR_Long'])
    except:
        response = {'statusCode': 400, 
        'message': 'RecievedMessage: {}'.format(event),'body': 'Base request'}
        
    table_manager = DashcamTableManager("dashcam_images")
    results = table_manager.get_imgs_in_GPS_bounds(tl_lat, tl_long, br_lat,
                                                              br_long)

    response = {'statusCode': 200, 
        'message': 'RecievedMessage: {}'.format(event),'body': results}
                
    return response
     