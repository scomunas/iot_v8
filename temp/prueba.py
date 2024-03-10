# Libraries needed
import json
from datetime import datetime, timedelta
import boto3
import os
from botocore.parsers import EventStreamJSONParser, ResponseParser
from requests.models import DEFAULT_REDIRECT_LIMIT

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
    response = requests.request("GET", url, headers=headers, data=payload)
    

    # response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code >= 200 and response.status_code < 300:
        response_json = json.loads(response.text)
        sunrise = datetime.strptime(response_json['results']['sunrise'], "%I:%M:%S %p")
        sunset = datetime.strptime(response_json['results']['sunset'], "%I:%M:%S %p")
        data = {
            "status": 200,
            "results": {
                "sunrise": sunrise,
                "sunset": sunset    
            }
        }
    else:
        data = {
            "status": 400,
            "results": {
            }
        }
    
    return data


sunrise_data = get_sunrise(41.61899359318845, 2.289165292862088)

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

    if response.status_code >= 200 and response.status_code < 300:
        response_json = json.loads(response.text)
        sunrise = datetime.strptime(response_json['results']['sunrise'], "%H:%M %p")
        data = {
            "sunrise": sunrise
        }
    else:
        data = {}


    return data

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

# scheduler = session.client('scheduler')

# flex_window = { "Mode": "OFF" }

# event = {
#     "type": "hola",
#     "example": "bye"
# }

# sqs_templated = {
#     "RoleArn": "arn:aws:iam::428652792036:role/iot-v8-eventbridge-role",
#     "Arn": "arn:aws:lambda:eu-central-1:428652792036:function:iot-v8-config-retrieve",
#     "Input": json.dumps(event),
#     'RetryPolicy': {
#             'MaximumEventAgeInSeconds': 3600,
#             'MaximumRetryAttempts': 0
#         },
# }

# scheduler.create_schedule(
#     Name="sqs-python-templated",
#     ActionAfterCompletion='DELETE',
#     ScheduleExpression = 'at(2024-03-14T00:00:00)',
#     ScheduleExpressionTimezone = 'CET',
#     State='ENABLED',
#     GroupName='iot-v8-actions',
#     Target=sqs_templated,
#     FlexibleTimeWindow=flex_window)

# prueba = "05:00-19:00"
# up = datetime.strptime(prueba.split('-')[0], "%H:%M")

# if up > sunrise_data['results']['sunrise']:
#     print("MAYOR")
# else:
#     print("MeNOR")

# # Get holiday list from https://date.nager.at/api
# def get_holidays(country, county):
#     year = datetime.now().year
#     url = "https://date.nager.at/api/v3/publicholidays/" + \
#         str(year) + \
#         "/" + \
#         str(country)

#     payload={}
#     headers = {}

#     response = requests.request("GET", url, headers=headers, data=payload)

#     if response.status_code >= 200 and response.status_code < 300:
#         response_json = json.loads(response.text)
#         holiday_list = []
#         for holiday in response_json:
#             if (holiday['global'] == True or
#                 county in holiday['counties']):
#                 holiday_list.append(holiday['date'])
#         data = {
#             "status": 200,
#             "results": holiday_list  
#         }
#     else:
#         data = {
#             "status": 400,
#             "results": {
#             }
#         }
    
#     return data

# print(get_holidays("ES", "ES-CT"))
# client = session.client('scheduler')

# response = client.list_schedules(
#     GroupName='iot-v8-events',
#     NamePrefix='iot-v8-irrigation',
#     MaxResults=50
# )
# print(len(response['Schedules']))


def check_db(table_name, type, date, id, state):
    dynamodb = session.client('dynamodb')

    response = dynamodb.query(
        TableName=table_name,
        KeyConditionExpression='event_type = :event_type AND event_date >= :event_date',
        ExpressionAttributeValues={
            ':event_type': {'S': type},
            ':event_date': {'S': date}
        }
    )
    
    event_number = 0
    
    for item in response['Items']:
        event_id = item['event_id']['S']
        event_state = item['event_state']['S']
        if ((event_id == id or id == 'any') and
            (event_state == state or state == 'any')):
            event_number += 1

    return event_number

print(check_db('iot-v8-events', 'door', '20240310_123556', 'entrada', 'open'))