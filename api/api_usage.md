# Roadway Event Estimation Based On Dashcam Image APIs
This page describes how to use the different APIs related to the Roadway Event Estimation Based On Dashcam Image project. There are two application programming interfaces:
* Image Upload API - API for users to upload images taken from their dashcams
* Uploaded Image Fetching API - API for users to fetch images uploaded from dashcams meeting GPS, timing, and label criteria

These API allows interaction with the Crowdsourced Data project. The base URL for this project is https://dy0duracgd.execute-api.us-east-1.amazonaws.com/dev. All methods are defined relative to this base URL.

# Image Upload API
### Purpose of API
The purpose of this API is so users can upload an image to a Crowdsourced database. There is some required added metadata which must be included in the API call. 
### API Parameters
| Parameter Name |                 Parameter Description                  | Parameter Type | Required Parameter |
| :------------- | :----------------------------------------------------: | :------------: | -----------------: |
| Latitude       | Latitude (decimal degrees) where the image was taken.  |    float64     |                Yes |
| Longitude      | Longitude (decimal degrees) where the image was taken. |    float64     |                Yes |
| ImageBase64    |        Image bytes encoded as a base64 string.         |     string     |                Yes |
### Example API Call URL
https://dy0duracgd.execute-api.us-east-1.amazonaws.com/dev/share-image?Latitude=48.3&Longitude=-83.3&ImageBase64=<ImageBase64>
### Response Format and description
Here is an example response in json format which a sucessful API call will result in: 
```json
{
    "statusCode": 200,
    "message": "Success",
    "dynamoMeta":
    {
        "Latitude": 20.2,
        "Longitude": 30.3,
        "EpochTime": 1617556321,
        "ImageURL": "https://ktopolovbucket.s3.amazonaws.com/original_1617556321.jpg",
        "LabeledImageURL": "https://ktopolovbucket.s3.amazonaws.com/labeled_1617556321.jpg",
        "humanReadableTime": "2021-04-04 17:12:01",
        "Labels": ["Road", "Traffic Jam"]
    }
}
```
Here is a description of all of the items provided in the result: 
| Response Item     |                                                                                    Item Description |
| :---------------- | --------------------------------------------------------------------------------------------------: |
| statusCode        |                                              Response code for if API call was sucessful or failed. |
| message           |                                            Response string for if API call was sucessful or failed. |
| Latitude          |                                              Latitude (decimal degrees) which was used in API call. |
| Longitude         |                                              Longitude (decimal degrees) which was used in API call |
| EpochTime         |                                 The time at which the server recieved the image in Unix Epoch time. |
| ImageURL          |                                   The URL of where the original image was stored and can be viewed. |
| LabeledImageURL   | The URL of where the image with added detected feature bounding boxes was stored and can be viewed. |
| humanReadableTime |                         The time at which the server recieved the image in a human readable format. |
| Labels            |                                                 A list of all identified features within the image. |

# Uploaded Image Fetching API
## Purpose of API
The purpose of this API is so users can obtain a list of uploaded images from the dashcam database with a provided criteria. The criteria which can be provided is a GPS bounding box, a freshness limit, and a detected label category. This allows users to get images within a certain geographic area, which were taken in a given recent amount of time, and have a particular detected label in them. 
## URL and path of API
https://dy0duracgd.execute-api.us-east-1.amazonaws.com/dev/get-imgs-in-gps-box?TL_Lat=48.3&TL_Long=-83.3&BR_Lat=41.3&BR_Long=-83.2&freshness_limit=60&detected_label=Car
## API Parameters
| Parameter Name  |                                         Parameter Description                                         | Parameter Type | Required Parameter |
| :-------------- | :---------------------------------------------------------------------------------------------------: | :------------: | -----------------: |
| TL_Lat          |                     Top left corner of bounding boxes Latitude (decimal degrees).                     |    float64     |                Yes |
| TL_Long         |                    Top left corner of bounding boxes Longitude (decimal degrees).                     |    float64     |                Yes |
| BR_Lat          |                   Bottom right corner of bounding boxes Latitude (decimal degrees).                   |    float64     |                Yes |
| BR_Long         |                  Bottom right corner of bounding boxes Longitude (decimal degrees).                   |    float64     |                Yes |
| freshness_limit |              In minutes, how recently an image was uploaded to be returned in the query.              |     int32      |                 No |
| detected_label  | Filter query results of query to only include images which contain this detected feature within them. |     string     |                 No |
## Response Format
Below is an example response in json format which a sucessful API call will result in. It is possible for the response body to have multiple items within the body indicating that multiple images match the query criteria: 
```json
"statusCode": 200,
"message": "RecievedMessage: {"TL_Lat": "0.0", "TL_Long": "0.0", "BR_Lat": "180.0", "BR_Long": "180.0"}",
"body": [
   {
       "info": {
           "latitude": 20.2,
           "longitude": 30.3,
           "image_source": "https://ktopolovbucket.s3.amazonaws.com/original_1617556321.jpg"
           "labeled_image_source":"https://ktopolovbucket.s3.amazonaws.com/labeled_1617556321.jpg",
           "human_readable_time": "2021-04-04 17:12:01",
           "detected_labels": ["Road", "Traffic Jam"],

       }
   }
]
```
Here is a description of all of the items provided in the result: 
| Response Item        |                                                                                    Item Description |
| :------------------- | --------------------------------------------------------------------------------------------------: |
| statusCode           |                                              Response code for if API call was sucessful or failed. |
| message              |                                         Contains all values of parameters used in API request call. |
| Latitude             |                                     Latitude (decimal degrees) associated with this uploaded image. |
| Longitude            |                                     Longitude (decimal degrees) associated with this uploaded image |
| image_source         |                                   The URL of where the original image was stored and can be viewed. |
| labeled_image_source | The URL of where the image with added detected feature bounding boxes was stored and can be viewed. |
| human_readable_time  |                         The time at which the server recieved the image in a human readable format. |
| detected_labels      |                                                 A list of all identified features within the image. |
