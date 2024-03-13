######################################
## Get calendar events and do actions
## 
######################################

from modules import get_config_file, ifttt_app, insert_db, check_db
import json
import os
from datetime import datetime, timedelta
import time

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
                    "event_type": 'irrigation',
                    "event_id": 'terraza',
                    "event_state": event['action'],
                    "event_data": '-'
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
                    "message": '<i>-- IoT v8 Action --</i>' + \
                  '\n<b>Type</b>: irrigation' + \
                  ' | <b>Id</b>: terraza' + \
                  ' | <b>Status</b>: ' + event['action'] + \
                  ' | <b>Data</b>: -'
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

def blinds_action(event, context):
    ## Get Event parameters
    print("Blinds Action -------------------------------------------")
    print(event)
    # body = json.loads(event["body"])
    # print(body)

    if ('action' in event.keys() and
        'blind' in event.keys()):
        print('Evento correcto, acción detectada')
        config = get_config_file()
        config_params = config['config']
        if(event['action'] == 'up' or
            event['action'] == 'down'):
            print('Acción ' + event['action'] + ' para la persiana ' + event['blind'])
            status = 200
            response_description = 'Acción ' + event['action'] + ' para la persiana ' + event['blind']
            body = {
                "blind": event['blind'],
                "action": event['action']
            }
            ifttt_app(
                key = config_params['ifttt_key'],
                app_name = config_params['blinds_off_app'],
                body = body
            )
            time.sleep(1)
            ifttt_app(
                key = config_params['ifttt_key'],
                app_name = config_params['blinds_app'],
                body = body
            )           
            if (config_params['log_enabled'] == True):
                event_parameters = {
                    "event_type": 'blinds',
                    "event_id": event['blind'],
                    "event_state": event['action'],
                    "event_data": '-'
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
                    "message": '<i>-- IoT v8 Action --</i>' + \
                  '\n<b>Type</b>: blinds' + \
                  ' | <b>Id</b>: ' + event['blind'] + \
                  ' | <b>Status</b>: ' + event['action'] + \
                  ' | <b>Data</b>: -'
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

def alarms_action(event, context):
    ## Get Event parameters
    print("Irrigation Action -------------------------------------------")
    print(event)
    # body = json.loads(event["body"])
    # print(body)

    if ('rule' in event.keys()):
        print('Evento correcto, alarma detectada')
        # Check if there is events that fits condition
        date_check = datetime.now() - timedelta(minutes=int(event['rule']['minutes']))
        event_number = check_db(
            table_name = os.environ['AWS_DYNAMO_EVENTS_TABLE'], 
            type = event['rule']['type'], 
            date = date_check.strftime('%Y%m%d_%H%M%S'), 
            id = event['rule']['id'], 
            state = event['rule']['id']
        )
        print('Eventos detectados coincidentes: ' + str(event_number))
        # Run alarm if trigger overflow
        if (event_number >= int(event['rule']['trigger'])):
            print('Alarma disparada')
            config = get_config_file()
            config_params = config['config']
            status = 200
            response_description = 'Alarma disparada por: ' + json.dumps(event['rule'])
            # body = {
            #     "action": event['action']
            # }
            # ifttt_app(
            #     key = config_params['ifttt_key'],
            #     app_name = config_params['irrigation_app'],
            #     body = body
            # )
            if (config_params['log_enabled'] == True):
                event_parameters = {
                    "event_type": 'alarm',
                    "event_id": event['rule']['id'],
                    "event_state": 'fired',
                    "event_data": json.dumps(event['rule'])
                }
                ttl_days = int(os.environ['RETENTION_DAYS'])
                events_table = os.environ['AWS_DYNAMO_EVENTS_TABLE']
                status_code, response = insert_db(
                    table_name = events_table, 
                    event_parameters = event_parameters, 
                    ttl_days = ttl_days
                )
            if (event['rule']['fire_telegram'] == 'TRUE'):
                body = {
                    "message": '<i>-- IoT v8 Action --</i>' + \
                  '\n<b>Type</b>: alarm!!!!!!!' + \
                  ' | <b>Id</b>: ' + event['rule']['id'] + \
                  ' | <b>Status</b>: fired!!!' + \
                  ' | <b>Data</b>: ' + json.dumps(event['rule'])
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
