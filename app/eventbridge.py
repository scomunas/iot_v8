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

def schedule_event(event, context):
    ## Get Event parameters
    print("Calendar Event -------------------------------------------")
    print(event)
    body = json.loads(event["body"])
    # print(body)

    ## Irrigation Event for Create Event received-----------------------------------------------------
    if (body['title'] == 'irrigation_create'):
        print("Create irrigation events -------------------------------------------")
        # Get config data and calculate today variables
        print('Get config data and calculate today variables')
        config = get_config_file()
        irrigation = config['irrigation']
        tomorrow_datetime = datetime.now() + timedelta(days = 1)
        today_weekday = days_of_week[tomorrow_datetime.weekday()]
        tomorrow_date = tomorrow_datetime.strftime("%Y-%m-%d")

        # Each row in irrigation list
        print('For each row in irrigation list')
        irrigation_boolean = False
        for row in irrigation:
            if row['weekday'] == today_weekday:
                # Row in today weekday
                print ('Row in today weekday: ' + str(row))

                # Calculate event times for start and stop
                print('Calculate event times for start and stop')
                irrigation_time = datetime.strptime(row['time'], '%H:%M')
                irrigation_start = irrigation_time.strftime('%H:%M')
                irrigation_stop = (irrigation_time + timedelta(minutes=row['duration'])).strftime('%H:%M')
                irrigation_end = (irrigation_time + timedelta(minutes=60)).strftime('%H:%M')

                # Create event for start irrigation
                print('Create event for start irrigation')
                ifttt_app(
                    key = config['config']['ifttt_key'],
                    app_name = config['config']['create_calendar_app'],
                    body = {
                        'start_time': tomorrow_date + ' ' + irrigation_start,
                        'end_time': tomorrow_date + ' ' + irrigation_end,
                        'title': 'irrigation_action',
                        'description': 'on'
                    }
                )

                # Create event for stop irrigation
                print('Create event for stop irrigation')
                ifttt_app(
                    key = config['config']['ifttt_key'],
                    app_name = config['config']['create_calendar_app'],
                    body = {
                        'start_time': tomorrow_date + ' ' + irrigation_stop,
                        'end_time': tomorrow_date + ' ' + irrigation_end,
                        'title': 'irrigation_action',
                        'description': 'off'
                    }
                )

                # Irrigation is OK and has been active
                irrigation_boolean = True
            else:
                # Row not in today weekday
                print ('Row NOT in today weekday: ' + str(row))
        
        if (irrigation_boolean == True):
            # Insert log only if there is almost 1 irrigation event
            # created
            event = {
                "type": 'irrigation',
                "id": 'terraza',
                "state": 'event_creation',
                "data": '-'
            }
            ttl_days = int(os.environ['RETENTION_DAYS'])
            events_table = os.environ['AWS_DYNAMO_EVENTS_TABLE']
            status_code, response = insert_db(
                table_name = events_table, 
                event_parameters = event, 
                ttl_days = ttl_days
            )
            status = 200
            response_description = 'Registros de riego insertados'
        else:
            status = 200
            response_description = 'Registros de riego NO insertados'
        
        return {
            "statusCode": status,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": response_description
        }
    ## Irrigation Event for Create Event received----------------------------------------------------
    elif (body['title'] == 'irrigation_action'):
        print("Irrigation Action -------------------------------------------")
        # Get config data and calculate today variables
        print('Get config data and calculate today variables')
        config = get_config_file()
        
        # Start or Stop irrigation based on description of the event
        status = ifttt_app(
            key = config['config']['ifttt_key'],
            app_name = config['config']['irrigation_app'],
            body = {
                'action': body['description']
            }
        )

        if status == 200:
            response_description = 'Acción de riego ejecutada correctamente'

            # Insert log
            event = {
                "type": 'irrigation',
                "id": 'terraza',
                "state": body['description'],
                "data": '-'
            }
            ttl_days = int(os.environ['RETENTION_DAYS'])
            events_table = os.environ['AWS_DYNAMO_EVENTS_TABLE']
            insert_db(
                table_name = events_table, 
                event_parameters = event, 
                ttl_days = ttl_days
            )
        else:
            response_description = 'Error al ejecutar la acción de riego'
        
        return {
            "statusCode": status,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": response_description
        }
    elif (body['title'] == 'move_blinds'):
        print(1)
    # Event type not recognized
    else:
        # print(get_sunrise(41.61899359318845, 2.289165292862088))
        return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": "Event type not recognized"
            }

