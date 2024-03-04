######################################
## Get calendar events and do actions
## 
######################################

from modules import get_config_file, ifttt_app, insert_db
import json
import os
from datetime import datetime, timedelta

# from modules import get_sunrise
days_of_week = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY','SUNDAY']

def irrigation_action(event, context):
    ## Get Event parameters
    print("Irrigation Action -------------------------------------------")
    print(event)
    # body = json.loads(event["body"])
    # print(body)

    if ('action' in event.keys()):
        print('Evento correcto, acción detectada')
        config = get_config_file()
        config_params = config['config']
        if(event['action'] == 'start' or
            event['action'] == 'stop'):
            print('Acción de riego: ' + event['action'])
            status = 200
            response_description = 'Acción de riego: ' + event['action']
            body = {
                "action": event['action']
            }
            ifttt_app(
                key = config_params['ifttt_key'],
                app_name = config_params['irrigation_app'],
                body = body
            )
            if (config_params['log_enabled'] == True):
                event_parameters = {
                    "type": 'irrigation',
                    "id": 'terraza',
                    "state": event['action'],
                    "data": '-'
                }
                ttl_days = int(os.environ['RETENTION_DAYS'])
                events_table = os.environ['AWS_DYNAMO_EVENTS_TABLE']
                status_code, response = insert_db(
                    table_name = events_table, 
                    event_parameters = event_parameters, 
                    ttl_days = ttl_days
                )
            if (config_params['notify_enabled'] == True):
                body = {
                    "message": '<i>-- IoT v7 Event --</i>' + \
                  '\n<b>Type</b>: irrigation' + \
                  '\n<b>Id</b>: terraza' + \
                  '\n<b>Status</b>: ' + event['action'] + \
                  '\n<b>Data</b>: -'
                }
                ifttt_app(
                    key = config_params['ifttt_key'],
                    app_name = config_params['telegram_app'],
                    body = body
                )
        else:
            status = 400
            response_description = 'Acción no compatible'
    else:
        status = 400
        response_description = 'Acción no detectada'

    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": response_description
    }

