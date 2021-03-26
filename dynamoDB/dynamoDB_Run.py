from decimal import Decimal
import json
import boto3
import logging
from pprint import pprint
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import time
from dashcam_table_manager import DashcamTableManager


# def put_new_img(uid, time, lat, long, imgSrc,dynamodb=None):
#     if not dynamodb:
#         dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
# 
#     table = dynamodb.Table(databasename)
#     latitude = str(lat)
#     longitude = str(long)
#     response = table.put_item(
#        Item={
#             'image_uid': uid,
#             'time': time,
#             'info': {
#                 'latitude': latitude,
#                 'longitude': longitude,
#                 'image_source': imgSrc
#             }
#         }
#     )
#     return response

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s')
# logger = logging.getLogger(__name__)


if __name__ == '__main__':

    tableManager = DashcamTableManager("dashcam_images")

    try:
        while True:
            val = input("Enter your value: ")
            if int(val) == 0:
                tableManager.check_if_table_exists()
            elif int(val)==1:
                tableManager.delete_table()
            elif int(val)==2:
                tableManager.list_tables()
            elif int(val)==3:
                put_sucess = tableManager.put_new_img(42.389459,-83.386596,"http://imgSource.com", "caterpillar")


    except KeyboardInterrupt:
        print('interrupted!')
    # list_tables()


    # if not check_if_table_exists():
    #     table = create_dashcam_img_table()

    # #Put new Item
    # put_response = put_new_img(0,int(time.time()), 42.390949, -83.393720,"www.google.com")
    # logger.info("Put image response: ")
    # pprint(put_response, sort_dicts=False)
