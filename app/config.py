######################################
## Store config file
## 
## Store JSON with all configuration
## in S3 bucket
######################################

import json
import os
from modules import put_file, get_file

def config_store(event, context):
    ## Get Event parameters
    print("Calendar Event -------------------------------------------")
    # print(event)
    body = json.loads(event["body"])
    print(body)

    # Store config file
    status_code, response = put_file(body)
    
    return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(response)
        }

def config_retrieve(event, context):
    ## Get Event parameters
    print("Calendar Event -------------------------------------------")
    # print(event)
    body = json.loads(event["body"])
    print(body)

    # Store config file
    data = get_file()
    print(data)
    
    return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(data)
        }
