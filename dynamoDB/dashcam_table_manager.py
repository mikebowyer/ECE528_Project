from decimal import Decimal
import json
import boto3
import time, datetime, uuid
import logging
from pprint import pprint
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

class DashcamTableManager():
    def __init__(self, tableName, dynamoDB=None):
        self.tableName = tableName
        self.table = None

        #Establish DynamoDB Resource Connection
        if not dynamoDB:
            self.dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

        if not self.check_if_table_exists():
            self.create_dashcam_img_table()

    def check_if_table_exists(self):
        self.table = self.dynamodb.Table(self.tableName)

        returnVal = False
        try:
            creationTime = self.table.creation_date_time
            # logger.info("The DashCam Images table has been found, and was originally created on {}".format(creationTime))
            print("The DashCam Images table has been found, and was originally created on {}".format(creationTime))
            returnVal = True
        except:
            # logger.info("The DashCam Images table could not be found")
            print("The DashCam Images table could not be found")
            returnVal =False
        return returnVal

    def delete_table(self,):
        print("Deleting table")
        self.table.delete()
        print("Delete sucessful")

    def list_tables(self):
        tables = list(self.dynamodb.tables.all())
        print("Tables which are found in this DynamoDB instance: ")
        for table in tables:
            print("\t - {}".format(table))

    def create_dashcam_img_table(self):
        print("Creating new table with title: {}".format(self.tableName))

        self.table = self.dynamodb.create_table(
            TableName=self.tableName,
            KeySchema=[
                {
                    'AttributeName': 'time',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'image_uid',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'time',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'image_uid',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )

    def put_new_img(self, lat, long, imgSrc, detectedLabel):
        print("Adding new entry with lat: {} \tlong:{} \tImage Source: {}".format(lat, long, imgSrc))

        #Preprocess & Generate new entry inputs
        epochTime = int(time.time())
        uid = str(uuid.uuid4())
        humanReadableTime = str(datetime.datetime.now())
        latitude = str(lat)
        longitude = str(long)
        returnVal = False
        try:
            response = self.table.put_item(
               Item={
                    'time': epochTime,
                    'image_uid': uid,
                    'info': {
                        'human_readable_time': humanReadableTime,
                        'latitude': latitude,
                        'longitude': longitude,
                        'image_source': imgSrc
                    }
                }
            )
            returnVal = True
        except:
            returnVal = False

        print("Putting new item into table response:")
        print(response)

        return returnVal

    def get_img(self, time, uid=None):
        print("Getting image with time: {} and uid: {}".format(time, uid))
        returnItem = None
        try:
            response = self.table.get_item(Key={'time': Decimal(time), 'image_uid': uid})
            print("Get item Response:")
            if "Item" in response:
                 print(response["Item"])
                 returnItem = response["Item"]
            elif "Items" in response:
                for item in response["Items"]:
                    print(item)
                    returnItem = []
                    returnItem.append(item)
            else:
                print("Get item request failed, no item with such data exists.")
        except ClientError as e:
            print(e.response['Error']['Message'])
            print("Get item request failed, no item with such data exists.")

        return returnItem

    def scan_table(self):
        response = self.table.scan()
        for item in response['Items']:
            print(item)
        # print(response)
        # scan_kwargs = {
        #     'FilterExpression': Key('year').between(*year_range),
        #     'ProjectionExpression': "#yr, title, info.rating",
        #     'ExpressionAttributeNames': {"#yr": "year"}
        # }
        #
        # done = False
        # start_key = None
        # while not done:
        #     if start_key:
        #         scan_kwargs['ExclusiveStartKey'] = start_key
        #     response = self.table.scan()
        #     display_movies(response.get('Items', []))
        #     start_key = response.get('LastEvaluatedKey', None)
        #     done = start_key is None