######################################
## Get Sunrise Fumction
## 
## Get Sunset/Sunrise from 
## https://sunrisesunset.io/api/
######################################

import json
import os
from modules import get_sunrise

def calendar_event(event, context):
    ## Get Event parameters
    print("Calendar Event -------------------------------------------")
    # print(event)
    body = json.loads(event["body"])
    print(body)

    if (body['event_type'] == 'get_sunrise'):
        print(get_sunrise(41.61899359318845, 2.289165292862088))
    elif (body['event_type'] == 'move_blinds'):
        print(1)
    else:
        print(1)
    
    return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": "OK"
        }
