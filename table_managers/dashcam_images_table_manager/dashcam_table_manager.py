from decimal import Decimal
import time, datetime, uuid, boto3
from botocore.exceptions import ClientError


class DashcamTableManager():
    def __init__(self, tableName, dynamoDB_local=False):
        self.tableName = tableName
        self.table = None

        # Establish DynamoDB Resource Connection locally or to AWS
        if dynamoDB_local:
            self.dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
        else:
            self.dynamodb = boto3.resource('dynamodb')

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

    def put_new_img(self, epochTime, lat, long, imgSrc, labeledImgSrc, detectedLabels,
                    humanReadableTime):
        print("Adding new entry with lat: {} \tlong:{} \tImage Source: {}".format(lat, long, imgSrc))

        # Preprocess & Generate new entry inputs
        uid = str(uuid.uuid4())
        latitude = Decimal(str(lat))
        longitude = Decimal(str(long))
        returnVal = False
        # try:
        response = self.table.put_item(
            Item={
                'time': epochTime,
                'image_uid': uid,
                'info': {
                    'human_readable_time': humanReadableTime,
                    'latitude': latitude,
                    'longitude': longitude,
                    'image_source': imgSrc,
                    'labeled_image_source': labeledImgSrc,
                    'detected_labels': detectedLabels
                }
            }
        )
        returnVal = True

        # print(response)
        # except:
        #     print("Error putting new item")
        #     returnVal = False

        return returnVal

    def get_img(self, time, uid):
        print("Getting image with time: {} and uid: {}".format(time, uid))
        returnItem = None
        try:
            response = self.table.get_item(Key={'time': Decimal(time), 'image_uid': uid})
            # print("Get item Response:")
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

    def scan_table(self):
        response = self.table.scan()
        for item in response['Items']:
            print(item)
        returnVal = None
        if 'Items' in response:
            returnVal = response['Items']
        return returnVal

    def update_img(self, time, uid, lat=None, long=None, imgSrc=None, detectedLabel=None):
        item = self.get_img(time, uid)
        returnVal = False
        if item is None:
            print("Unable to update specified item because it cannot be found in the table.")
        else:
            # Update the item in place for any attributes which we want to change
            if lat != None:
                item['info']['latitude'] = str(lat)
            if long != None:
                item['info']['longitude'] = str(long)
            if imgSrc != None:
                item['info']['image_source'] = str(imgSrc)
            if detectedLabel != None:
                item['info']['detected_labels'] = str(detectedLabel)

            # Update the item!
            response = self.table.update_item(
                Key={
                    'time': time,
                    'image_uid': uid
                },
                UpdateExpression="set info.latitude=:lt, info.longitude=:lg, info.image_source=:i, info.detected_label=:d",
                ExpressionAttributeValues={
                    ':lt': item['info']['latitude'],
                    ':lg': item['info']['longitude'],
                    ':i': item['info']['image_source'],
                    ':d': item['info']['detected_label']
                },
                ReturnValues="UPDATED_NEW"
            )
            print(response)
            returnVal = True
        return returnVal

    def delete_img(self, time, uid):
        try:
            response = self.table.delete_item(
                Key={
                    'time': time,
                    'image_uid': uid
                },
            )
            # TODO make sure this really deletes something
        except ClientError as e:
            if e.response['Error']['Code'] == "ConditionalCheckFailedException":
                print(e.response['Error']['Message'])
            else:
                raise
        else:
            return response

    def get_imgs_in_GPS_bounds(self, top_left_lat, top_left_long, bottom_right_lat, bottom_right_long, freshness_limit=0,
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
