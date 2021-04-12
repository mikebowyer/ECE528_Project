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

    def get_imgs_in_GPS_bounds(self, top_left_lat, top_left_long, bottom_right_lat, bottom_right_long,
                               freshness_limit=0,
                               detected_label=""):

        upper_lat = max(top_left_lat, bottom_right_lat)
        lower_lat = min(top_left_lat, bottom_right_lat)
        upper_long = max(top_left_long, bottom_right_long)
        lower_long = min(top_left_long, bottom_right_long)

        items = self.scan_table()

        # Get items in GPS bounding Boxes
        itemsInBounds = []
        for item in items:
            if upper_lat > item['info']['latitude'] and item['info']['latitude'] > lower_lat:
                if upper_long > item['info']['longitude'] and item['info']['longitude'] > lower_long:
                    itemsInBounds.append(item)

        # Filter out items not uploaded within recent time window
        itemInBoundsAndFresh = []
        current_time = int(time.time())
        if freshness_limit != 0:
            for item in itemsInBounds:
                itemCreationTime = int(item['time'])
                itemAgeinMins = (current_time - itemCreationTime) / 60

                if itemAgeinMins < freshness_limit:
                    itemInBoundsAndFresh.append(item)
        else:
            itemInBoundsAndFresh = itemsInBounds

        # Filter out items without the correct label
        itemInBoundsAndFreshAndCorrectLabel = []
        if detected_label != "":
            for item in itemInBoundsAndFresh:
                for label in item['info']['detected_labels']:
                    if detected_label in label:
                        itemInBoundsAndFreshAndCorrectLabel.append(item)
        else:
            itemInBoundsAndFreshAndCorrectLabel = itemInBoundsAndFresh

        return itemInBoundsAndFreshAndCorrectLabel

    def put_new_event(self, epochTime, lat, long, eventType, associateImg):
        print("Adding new event with lat: {} \tlong:{} \tEvent Type: {} \nAssociated Image: {}".format(lat, long, eventType, associateImg))

        # Preprocess & Generate new entry inputs
        uid = str(uuid.uuid4())
        latitude = Decimal(str(lat))
        longitude = Decimal(str(long))
        return_val = None
        try:
            response = self.table.put_item(
                Item={
                    'start_time': epochTime,
                    'event_uid': uid,
                    'info': {
                        'latitude': latitude,
                        'longitude': longitude,
                        'event_type': str(eventType),
                        'last_update_time': epochTime,
                        'associated_images': [{"image_uid": associateImg['image_uid'], "time": associateImg['time']}]
                    }
                }
            )
            return_val = True
        except:
            print("Error putting new item")
            return_val = False

        return return_val


    def update_events_from_new_image(self, img_info):
        # 1) Get events within last X minutes
        # 2) Check if img is near any existing events
        # 3) Check if img labels match any event labels
        # 3a) if matching, update event
        print("Yalla Habibe")