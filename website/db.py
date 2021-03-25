import boto3

dynamo_client = boto3.client('dynamodb')

def get_items():
    resp = dynamo_client.scan(
        TableName='TestLocationMarkers'
    )
    arr = []
    for el in resp["Items"]:
        arr.append([float(el["latitude"]['S']), float(el["longitude"]['S'])])
    return arr
