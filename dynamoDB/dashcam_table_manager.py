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

        self.check_if_table_exists()

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