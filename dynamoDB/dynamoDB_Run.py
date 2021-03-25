from decimal import Decimal
import json
import boto3
import logging
from pprint import pprint
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import time
from dashcam_table_manager import DashcamTableManager

# def list_tables(dynamodb=None):
#     if not dynamodb:
#         dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
# 
#     print(list(dynamodb.tables.all()))
# 
# def check_if_table_exists(dynamodb=None):
#     if not dynamodb:
#         dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
# 
#     table = dynamodb.Table(databasename)
#     returnVal = False
#     try:
#         creationTime = table.creation_date_time
#         logger.info("The DashCam Images table has been found, and was originally created on {}".format(creationTime))
#         returnVal = True
#     except:
#         logger.info("The DashCam Images table could not be found")
#         returnVal =False
#     return returnVal
# 
# def delete_table(tableName, dynamodb=None):
#     if not dynamodb:
#         dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
# 
#     table = dynamodb.Table(tableName)
#     table.delete()
# 
# def create_dashcam_img_table(dynamodb=None):
#     if not dynamodb:
#         dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
# 
#     table = dynamodb.create_table(
#         TableName=databasename,
#         KeySchema=[
#             {
#                 'AttributeName': 'image_uid',
#                 'KeyType': 'HASH'  # Partition key
#             },
#             {
#                 'AttributeName': 'time',
#                 'KeyType': 'RANGE'  # Sort key
#             }
#         ],
#         AttributeDefinitions=[
#             {
#                 'AttributeName': 'image_uid',
#                 'AttributeType': 'N'
#             },
#             {
#                 'AttributeName': 'time',
#                 'AttributeType': 'N'
#             }
#         ],
#         ProvisionedThroughput={
#             'ReadCapacityUnits': 10,
#             'WriteCapacityUnits': 10
#         }
#     )
#     return table
# 
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

    except KeyboardInterrupt:
        print('interrupted!')
    # list_tables()


    # if not check_if_table_exists():
    #     table = create_dashcam_img_table()

    # #Put new Item
    # put_response = put_new_img(0,int(time.time()), 42.390949, -83.393720,"www.google.com")
    # logger.info("Put image response: ")
    # pprint(put_response, sort_dicts=False)
