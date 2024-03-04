# Libraries needed
import json
from datetime import datetime, timedelta
import boto3
import os
from botocore.parsers import ResponseParser

session = boto3.session.Session(profile_name='personal', region_name='eu-central-1')

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

# get_sunrise(41.61899359318845, 2.289165292862088)

def ifttt_app(key, app_name, body):
    url = "https://maker.ifttt.com/trigger/APPLET_NAME/json/with/key/".replace("APPLET_NAME", app_name) + key
    print(url)
    headers = {
        'Content-Type': 'application/json'
    }
    print(json.dumps(body))

    response = requests.request('POST', url,
                headers=headers,
                data=json.dumps(body))

    return response.status_code

# print(ifttt_app('gcs4wieOf6v8rnA-CD8QbK3XP39vs_FIfnjvM-2Y6LA', 'iot_v7_blinds_off', {}))
# print(ifttt_app('gcs4wieOf6v8rnA-CD8QbK3XP39vs_FIfnjvM-2Y6LA', 'iot_v8_calendar_create', {
#     "start_time": "26-02-2024 22:54",
#     "end_time": "26-02-2024 22:59",
#     "title": "prueba",
#     "description": "prueba"
# }))

# days_of_week = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY','SUNDAY']
# today_datetime = datetime.now()
# today_weekday = days_of_week[today_datetime.weekday()]
# today_date = today_datetime.strftime("%Y-%m-%d")
# print(today_date)
# print(today_weekday)

# time_string = '08:00'
# time = datetime.strptime(time_string, '%H:%M')
# print(time+timedelta(minutes=2))

scheduler = session.client('scheduler')

flex_window = { "Mode": "OFF" }

event = {
    "type": "hola",
    "example": "bye"
}

sqs_templated = {
    "RoleArn": "arn:aws:iam::428652792036:role/service-role/Eventbridge_Test",
    "Arn": "arn:aws:lambda:eu-central-1:428652792036:function:iot-v8-calendar-event",
    "Input": json.dumps(event),
    'RetryPolicy': {
            'MaximumEventAgeInSeconds': 3600,
            'MaximumRetryAttempts': 0
        },
}

scheduler.create_schedule(
    Name="sqs-python-templated",
    ActionAfterCompletion='DELETE',
    ScheduleExpression = 'at(2024-03-14T00:00:00)',
    State='ENABLED',
    Target=sqs_templated,
    FlexibleTimeWindow=flex_window)