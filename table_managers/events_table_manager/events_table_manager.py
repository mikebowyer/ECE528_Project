from decimal import Decimal
import time, datetime, uuid, boto3
from botocore.exceptions import ClientError


class EventTableManager():
    def __init__(self, tableName, dynamoDB_local=False):
        self.tableName = tableName
        self.table = None

        # Establish DynamoDB Resource Connection locally or to AWS
        if dynamoDB_local:
            self.dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
        else:
            self.dynamodb = boto3.resource('dynamodb')

        if not self.check_if_table_exists():
            self.create_event_table()

    def check_if_table_exists(self):
        self.table = self.dynamodb.Table(self.tableName)

        returnVal = False
        try:
            creationTime = self.table.creation_date_time
            print("The table has been found, and was originally created on {}".format(creationTime))
            returnVal = True
        except:
            print("The table could not be found")
            returnVal = False
        return returnVal

    def delete_table(self, ):
        print("Deleting table")
        self.table.delete()
        print("Delete sucessful")

    def list_tables(self):
        tables = list(self.dynamodb.tables.all())
        print("Tables which are found in this DynamoDB instance: ")
        for table in tables:
            print("\t - {}".format(table))

    def create_event_table(self):
        print("Creating new table with title: {}".format(self.tableName))

        self.table = self.dynamodb.create_table(
            TableName=self.tableName,
            KeySchema=[
                {
                    'AttributeName': 'start_time',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'event_uid',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'start_time',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'event_uid',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )

    def scan_table(self):
        response = self.table.scan()
        for item in response['Items']:
            print(item)
        returnVal = None
        if 'Items' in response:
            returnVal = response['Items']
        return returnVal


    def put_new_event(self, eventType, first_image_of_event):
        # Preprocess & Generate new entry inputs
        uid = str(uuid.uuid4())
        latitude = first_image_of_event['info']['latitude']
        longitude = first_image_of_event['info']['longitude']
        print("Adding new event with lat: {} \tlong:{} \tEvent Type: {} \nAssociated Image: {}".format(latitude, longitude,
                                                                                                       eventType,
                                                                                                       first_image_of_event))
        associated_images = []
        associated_images.append(first_image_of_event)
        return_val = None
        try:
            response = self.table.put_item(
                Item={
                    'start_time': first_image_of_event['time'],
                    'event_uid': uid,
                    'info': {
                        'latitude': latitude,
                        'longitude': longitude,
                        'event_type': str(eventType),
                        'last_update_time': first_image_of_event['time'],
                        'associated_images': [associated_images]
                    }
                }
            )
            return_val = True
        except:
            print("Error putting new item")
            return_val = False

        return return_val


    def get_event(self, start_time, event_uid):
        print("Getting event with time: {} and uid: {}".format(start_time, event_uid))
        returnItem = None
        try:
            response = self.table.get_item(Key={'start_time': Decimal(start_time), 'event_uid': event_uid})
            print("Get item Response:")
            if "Item" in response:
                # print(response["Item"])
                returnItem = response["Item"]
            elif "Items" in response:
                for item in response["Items"]:
                    # print(item)
                    returnItem = []
                    returnItem.append(item)
            else:
                print("Get item request failed, no item with such data exists.")
        except ClientError as e:
            print(e.response['Error']['Message'])
            print("Get item request failed, no item with such data exists.")

        return returnItem


    def update_event_using_new_img(self, event_start_time, event_uid, new_image_to_associate):
        event = self.get_event(event_start_time, event_uid)
        returnVal = False
        if event is None:
            print("Unable to update specified item because it cannot be found in the table.")
        else:
            # Update Lat & Long:
            event['info']['latitude'] = (event['info']['latitude'] + new_image_to_associate['info']['latitude']) / 2
            event['info']['longitude'] = (event['info']['longitude'] + new_image_to_associate['info']['longitude']) / 2

            # Update latest update time of event
            event['info']['last_update_time'] = new_image_to_associate['time']

            # Update list of associated images
            associated_images = []
            for associated_image in event['info']['associated_images']:
                associated_images.append(associated_image[0])
            associated_images.append(new_image_to_associate)
            event['info']['associated_images'] = associated_images

            # Update the item!
            response = self.table.update_item(
                Key={
                    'start_time': event_start_time,
                    'event_uid': event_uid,
                },
                UpdateExpression="set info.latitude=:lt, info.longitude=:lg, info.last_update_time=:lu, info.associated_images=:ai",
                ExpressionAttributeValues={
                    ':lt': event['info']['latitude'],
                    ':lg': event['info']['longitude'],
                    ':lu': event['info']['last_update_time'],
                    ':ai': event['info']['associated_images']
                },
                ReturnValues="UPDATED_NEW"
            )
            print(response)
            returnVal = True
        return returnVal

