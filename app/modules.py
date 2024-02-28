######################################
## Modules
## 
## General functions for use in 
## all lambdas
######################################

# Libraries needed
import json
from datetime import datetime, timedelta
import boto3
import os
import requests

## Insert event row on DB
def insert_db(table_name, event_parameters, ttl_days):
    # Calculate dates assuming
    # event date is just now
    date = datetime.now()
    date_delta = date + timedelta(days = ttl_days)
    date_string = date.strftime("%Y%m%d_%H%M%S")
    date_ttl = int(date_delta.timestamp())
    event_parameters['date'] = date_string
    event_parameters['date_ttl'] = date_ttl

    # Create DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    # Put the row in the table
    response = table.put_item(
        Item = event_parameters
        )
    status_code = response['ResponseMetadata']['HTTPStatusCode']

    # Return status value
    return status_code, response['ResponseMetadata']

# Get sunrise/sunset from https://sunrisesunset.io/api/
def get_sunrise(lat, long):
    url = "https://api.sunrisesunset.io/json?lat=" + \
        str(lat) + \
        "&lng=" + \
        str(long)

    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)

# Store config file
def put_config_file(data):
    bucket = os.environ['S3_BUCKET']
    s3 = boto3.resource('s3')
    s3object = s3.Object(bucket, 'config.json')
    response = s3object.put(
        Body=(bytes(json.dumps(data).encode('UTF-8')))
    )
    status_code = response['ResponseMetadata']['HTTPStatusCode']

    # Return status value
    return status_code, response['ResponseMetadata']

# Retrieve config file
def get_config_file():
    bucket = os.environ['S3_BUCKET']
    s3 = boto3.resource('s3')
    s3object = s3.Object(bucket, 'config.json')
    file_content = s3object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)
    return json_content

# Use a IFTTT app
def ifttt_app(key, app_name, body):
    url = "https://maker.ifttt.com/trigger/APPLET_NAME/json/with/key/".replace("APPLET_NAME", app_name) + key
    print(url)
    headers = {}

    response = requests.request('POST', url,
                headers=headers,
                data=json.dumps(body))

    return response.status_code

# # Get body event and parse it
# # using interpret for each
# # manufacturer
# def get_event_parameters(body):
#     device_manufacturer = ""
#     device_id = ""
#     channel = ""
#     device_event= ""

#     if 'trigger' in body:
#         # Ewelink event
#         # Set parameters
#         device_manufacturer = "ewelink"
#         device_id = body['trigger']['deviceid']
#         device_type_switches = body['trigger']['expression'].find("update.params.switches") != -1
#         device_type_switch = body['trigger']['expression'].find("update.params.switch=") != -1
#         device_type_defense = body['trigger']['expression'].find("update.params.defense") != -1
#         if device_type_switches == True:
#             # Multiswitch
#             channel = body['trigger']['expression'].split("'")[0].replace("]", "[").split("[")[1]
#             device_event = body['trigger']['expression'].split("'")[1]
#         if device_type_switch == True and device_type_defense == False:
#             # Switch
#             channel = 0
#             device_event = body['trigger']['expression'].split("'")[1]
#         if device_type_switch == True and device_type_defense == True:
#             # Sensor
#             channel = 0
#             device_event = body['trigger']['expression'].split("'")[1]
#             if device_event == 'on':
#                 device_event = 'open'
#             else:
#                 device_event = 'close'
#     else:
#         # Get device manufacturer 
#         if 'manufacturer' in body:
#             device_manufacturer = body['manufacturer']

#         # Get device info 
#         if 'deviceid' in body:
#             device_id = body['deviceid']

#         # Check if it's a dlink cam
#         if device_manufacturer == 'dlink' and device_id[0:3] == 'cam':
#             channel = body['event']
#             device_event = 'on'
#         else:        
#             # Calculate parameters
#             channel = 0
#             if 'event' in body:
#                 device_event = body['event']

    
#     event_parameters = {
#         "device_manufacturer" : device_manufacturer,
#         "device_id": device_id,
#         "channel": channel,
#         "device_event": device_event
#     }
#     if device_manufacturer == "" or device_id == "":
#         status_code = 400
#     else:
#         status_code = 200
    
#     return status_code, event_parameters

# # Insert event in Dynamo DB
# def insert_event_db(event_parameters, ttl_days):
#     # Calculate dates assuming
#     # event date is just now
#     date = datetime.now()
#     date_ttl = date + timedelta(days = ttl_days)
#     date_string = date.strftime("%Y%m%d_%H%M%S")
#     date_epoch = int(date_ttl.strftime("%s"))

#     # Create row for insert
#     row = {
#     "device_id": event_parameters['device_id'],
#     "date_epoch": date_epoch,
#     "date_string": date_string,
#     "device_manufacturer": event_parameters['device_manufacturer'],
#     "channel": event_parameters['channel'],
#     "event": event_parameters['device_event']
#     }

#     # Create DynamoDB client
#     dynamodb = boto3.resource('dynamodb')
#     table = dynamodb.Table('iot-v8-events')

#     # Put the row in the table
#     response = table.put_item(Item=row)
#     status_code = response['ResponseMetadata']['HTTPStatusCode']

#     # Return status value
#     return status_code, response['ResponseMetadata']

# # Insert event in sqs Queue
# # events available are: status_update, action
# def insert_event_sqs(event, body, delay):
#     sqs_url = os.environ['sqs_url']

#     #Set up the SQS client
#     sqs = boto3.client('sqs')

#     # Set up the message to send
#     message = {
#         'event': event,
#         'body': body
#     }
#     messageBody = json.dumps(message)

#     # Set up the delay time
#     delay_seconds = delay

#     # Send the message to the SQS queue with the specified delay
#     response = sqs.send_message(
#         QueueUrl=sqs_url,
#         MessageBody=messageBody,
#         DelaySeconds=delay_seconds
#     )
#     status_code = response['ResponseMetadata']['HTTPStatusCode']

#     # Return status value
#     return status_code, response['ResponseMetadata']

# # Insert event in status table
# def insert_status_db(event_parameters):
#     # Calculate dates assuming
#     # event date is just now
#     date = datetime.now()
#     date_string = date.strftime("%Y%m%d_%H%M%S")

#     # Prepare row for insert
#     row = {
#         "device_id": event_parameters['device_id'],
#         "channel": str(event_parameters['channel']),
#         "date_string": date_string,
#         "status": event_parameters['device_event']    
#     }
    
#     # Create DynamoDB client
#     dynamodb = boto3.resource('dynamodb')
#     table = dynamodb.Table('iot-v8-status')

#     # Put the row in the table
#     response = table.put_item(Item=row)
#     status_code = response['ResponseMetadata']['HTTPStatusCode']

#     # Return status value
#     return status_code, response['ResponseMetadata']

# # Get current scene
# def get_scene():
#     # Create DynamoDB client
#     dynamodb = boto3.resource('dynamodb')
#     table = dynamodb.Table('iot-v8-status')

#     response = table.get_item(
#         Key={"device_id": "scene", "channel": "scene"}
#     )
#     status_code = response['ResponseMetadata']['HTTPStatusCode']

#     # Error if status code 4xx o 5xx
#     if status_code >= 400 and status_code < 600:
#         scene = "error"
#     else:
#         if 'Item' in response:
#             scene = response['Item']['status']
#         else:
#             scene = "error"
        
#     # Return status value
#     return status_code, scene

# # Search trigger for device_id, scene and channel
# def get_triggers(device_id, scene, channel):
#     # Create DynamoDB client
#     dynamodb = boto3.resource('dynamodb')
#     table = dynamodb.Table('iot-v8-triggers')

#     response = table.get_item(
#         Key={"device_id": device_id, "id": scene + "|" + str(channel)}
#     )
#     status_code = response['ResponseMetadata']['HTTPStatusCode']

#     # Error if status code 4xx o 5xx
#     if status_code >= 400 and status_code < 600:
#         trigger = {
#             "event_num": -1
#         }
#     else:
#         if 'Item' in response:
#             trigger = {
#                 "event_num": response['Item']['event_num'],
#                 "event_seconds": response['Item']['event_seconds'],
#                 "log": response['Item']['log'],
#                 "telegram": response['Item']['telegram'],
#                 "call": response['Item']['call']
#             }
            
#         else:
#             trigger = {
#                 "event_num": 0
#             }
        
#     # Return status value
#     return status_code, trigger

# # Check trigger conditions
# def check_triggers(event_num, event_seconds, event_parameters):
#     # Calculate dates 
#     date_end = datetime.now()
#     date_start = date_end - timedelta(seconds = int(event_seconds))
#     date_current = date_end
#     date_list = []
#     while date_current > date_start:
#         date_list.append(date_current.strftime("%Y%m%d_%H%M"))
#         date_current = date_current - timedelta(minutes = 1)
#     # print(date_list)

#     # Create DynamoDB client
#     dynamodb = boto3.resource('dynamodb')
#     table = dynamodb.Table('iot-v8-events')

#     # Get event list
#     events = []
#     event_count = 0
#     for date in date_list:
#         response = table.query(
#             KeyConditionExpression="device_id = :device_id AND begins_with(date_string, :date_string)",
#             ExpressionAttributeValues={
#                 ':device_id': event_parameters['device_id'],
#                 ':date_string': date
#             }
#         )
#         status_code = response['ResponseMetadata']['HTTPStatusCode']

#         # Error if status code 4xx o 5xx
#         if status_code >= 400 and status_code < 600:
#             events = []
#             print("Error obtaining event registers")
#         else:
#             # Query obtains results
#             if response['Count'] >= 1:
#                 for item in response['Items']:
#                     # Check conditions for each event
#                     # current: channel and date_string
#                     date_event = datetime.strptime(item['date_string'], "%Y%m%d_%H%M%S")
#                     if item['channel'] == event_parameters['channel'] and date_event >= date_start:
#                         events.append(item)
    
#     # Return trigger only if we have more events
#     # than configured in trigger
#     event_count = len(events)
#     if event_count >= int(event_num):
#         trigger_status = True
#     else:
#         trigger_status = False

#     # Return status value
#     return status_code, trigger_status