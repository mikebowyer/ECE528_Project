from decimal import Decimal
import json
import boto3
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
        self.table = self.dynamodb.create_table(
            TableName=self.tableName,
            KeySchema=[
                {
                    'AttributeName': 'image_uid',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'time',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'image_uid',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'time',
                    'AttributeType': 'N'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )