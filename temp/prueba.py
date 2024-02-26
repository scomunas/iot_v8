# Libraries needed
import json
from datetime import datetime, timedelta
import boto3
import os

# # Insert event in Dynamo DB
# def insert_event_db(event_parameters, ttl_days):
#     # Calculate dates assuming
#     # event date is just now
#     date = datetime.now()
#     date_delta = date + timedelta(days = ttl_days)
#     date_string = date.strftime("%Y%m%d_%H%M%S")
#     date_ttl = int(date_delta.timestamp())

#     # Create row for insert
#     row = {
#     "date": date_string,
#     "type": "door",
#     "id": "entrada",
#     "state": "open",
#     "data": "-",
#     "date_ttl": date_ttl
#     }

#     # Create DynamoDB client
#     session = boto3.session.Session(profile_name='personal', region_name='eu-central-1')
#     dynamodb = session.resource('dynamodb')
#     table = dynamodb.Table('iot-v8-events')

#     # Put the row in the table
#     response = table.put_item(Item=row)
#     status_code = response['ResponseMetadata']['HTTPStatusCode']

#     # Return status value
#     return status_code, response['ResponseMetadata']


# insert_event_db(
#     event_parameters={},
#     ttl_days=1
# )

import requests
import urllib3

# Get sunrise/sunset from https://sunrisesunset.io/api/
def get_sunrise(lat, long):
    url = "https://api.sunrisesunset.io/json?lat=" + \
        str(lat) + \
        "&lng=" + \
        str(long)

    payload={}
    headers = {}

    print(url)
    response = urllib3.request('GET', url,
                headers=headers,
                body=payload)
    

    # response = requests.request("GET", url, headers=headers, data=payload)

    print(response)

get_sunrise(41.61899359318845, 2.289165292862088)