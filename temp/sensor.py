######################################
## Input Event Fumction
## 
## IoT devices will send events to
## this function
######################################

import json
import os
from modules import insert_db

def sensor_event(event, context):
    ## Get Event parameters
    print("Input Event received-------------------------------------------")
    # print(event)
    body = json.loads(event["body"])
    print(body)

    ## Create row for insert
    if ('type' in body.keys() and
        'id' in body.keys() and
        'state' in body.keys() and
        'data' in body.keys()):
        event_parameters = {
        "event_type": body['type'],
        "event_id": body['id'],
        "event_state": body['state'],
        "event_data": body['data']
        }
    else:
        print('La petición no contiene los parámetros necesarios')
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": "La petición no contiene los parámetros necesarios"
        }

    ## Insert in DynamoDB
    ttl_days = int(os.environ['RETENTION_DAYS'])
    events_table = os.environ['AWS_DYNAMO_EVENTS_TABLE']
    status_code, response = insert_db(
        table_name = events_table, 
        event_parameters = event_parameters, 
        ttl_days = ttl_days
    )

    # Error if status code 4xx o 5xx
    if status_code >= 400 and status_code < 600:
        print("Error inserting row: " + json.dumps(event_parameters))
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": "Error inserting row: " + json.dumps(event_parameters)
        }
    else:
        print("Row inserted in events table")
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": "OK"
        }