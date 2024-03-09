######################################
## Get calendar events and do actions
## 
######################################

from modules import get_config_file, action_create, insert_db, ifttt_app, get_sunrise
import json
import os
from datetime import datetime, timedelta

# from modules import get_sunrise
days_of_week = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY','SUNDAY']
days_of_weekend = ['SATURDAY', 'SUNDAY']

def irrigation_event(event, context):
    ## Get Event parameters
    print("Irrigation Event -------------------------------------------")
    print(event)
    # body = json.loads(event["body"])
    # print(body)

    print("Create irrigation events -------------------------------------------")
    # Get config data and calculate today variables
    print('Get config data and calculate today variables')
    config = get_config_file()
    irrigation = config['irrigation']
    config_params = config['config']
    tomorrow_datetime = datetime.now() + timedelta(days = 1)
    tomorrow_weekday = days_of_week[tomorrow_datetime.weekday()]
    tomorrow_date = tomorrow_datetime.strftime("%Y-%m-%d")

    # Each row in irrigation list
    print('For each row in irrigation list')
    irrigation_boolean = False
    for row in irrigation:
        if (row['weekday'] == tomorrow_weekday and
            row['enable'] == True):
            # Row in today weekday
            print ('Row in today weekday: ' + str(row))

            # Calculate event times for start and stop
            print('Calculate event times for start and stop')
            irrigation_time = datetime.strptime(row['time'], '%H:%M')
            irrigation_start = irrigation_time.strftime('%H:%M')
            irrigation_stop = (irrigation_time + timedelta(minutes=row['duration'])).strftime('%H:%M')

            # Create event for start irrigation
            print('Create event for start irrigation')
            irrigation_date = tomorrow_date + 'T' + irrigation_start + ':00'
            irrigation_name = irrigation_date.replace('-', '').replace(':', '').replace('T', '_')
            event = {
                "type": "irrigation",
                "action": "start"
            }
            action_create(
                name = 'irrigation_start_' + irrigation_name,
                event = event,
                target_lambda = os.environ['EVENTBRIDGE_LAMBDA'],
                schedule = irrigation_date
            )

            # Create event for stop irrigation
            print('Create event for stop irrigation')
            irrigation_date = tomorrow_date + 'T' + irrigation_stop + ':00'
            irrigation_name = irrigation_date.replace('-', '').replace(':', '').replace('T', '_')
            event = {
                "type": "irrigation",
                "action": "stop"
            }
            action_create(
                name = 'irrigation_stop_' + irrigation_name,
                event = event,
                target_lambda = os.environ['EVENTBRIDGE_LAMBDA'],
                schedule = irrigation_date
            )

            # Irrigation is OK and has been active
            irrigation_boolean = True
        else:
            # Row not in today weekday
            print ('Row NOT in today weekday: ' + str(row))
    
    if (irrigation_boolean == True):
        # Insert log and notify only if there is almost 1 irrigation event
        # created
        if (config_params['log_enabled'] == True):
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
        if (config_params['notify_enabled'] == True):
                body = {
                    "message": '<i>-- IoT v8 Event --</i>' + \
                  '\n<b>Type</b>: irrigation' + \
                  ' | <b>Id</b>: terraza' + \
                  ' | <b>Status</b>: event_creation' + \
                  ' | <b>Data</b>: -'
                }
                ifttt_app(
                    key = config_params['ifttt_key'],
                    app_name = config_params['telegram_app'],
                    body = body
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

def blinds_event(event, context):
    ## Get Event parameters
    print("Blinds Event -------------------------------------------")
    print(event)
    # body = json.loads(event["body"])
    # print(body)

    print("Create blind events -------------------------------------------")
    # Get config data and calculate today variables
    print('Get config data and calculate today variables')
    config = get_config_file()
    blinds = config['blinds']
    config_params = config['config']
    today_datetime = datetime.now()
    today_weekday = days_of_week[today_datetime.weekday()]
    today_date = today_datetime.strftime("%Y-%m-%d")

    # Each row in blinds list
    print('For each row in blind list')
    row_boolean = False
    for row in blinds:
        if row['sunrise'] == True:
            # Only if sunrise is enabled
            # Get config times
            if today_weekday not in days_of_weekend:
                # Normal day
                blind_up = datetime.strptime(row['time_normal'].split('-')[0], '%H:%M')
                blind_down = datetime.strptime(row['time_normal'].split('-')[1], '%H:%M')
            else:
                # "Holiday" day
                blind_up = datetime.strptime(row['time_holiday'].split('-')[0], '%H:%M')
                blind_down = datetime.strptime(row['time_holiday'].split('-')[1], '%H:%M')

            # Get sunrise from sunrisesunset.io
            print('Get sunrise from sunrisesunset.io')
            sunrise_data = get_sunrise(
                lat = config_params['blinds_lat'],
                long = config_params['blinds_long']
            )
            if sunrise_data['status'] == 200:
                # Only if we can get correct data
                # we will correct up and down times
                if blind_up < sunrise_data['results']['sunrise']:
                    blind_up = sunrise_data['results']['sunrise']
                if blind_down < sunrise_data['results']['sunset']:
                    blind_down = sunrise_data['results']['sunset']
            
            # Create event for blind up
            print('Create event for blind ' + row['blind'] + ' up')
            blind_up_date = today_date + 'T' + blind_up.strftime("%H:%M") + ':00'
            blind_up_name = row['blind'] + "_" + blind_up_date.replace('-', '').replace(':', '').replace('T', '_')
            event = {
                "blind": row['blind'],
                "action": "up"
            }
            action_create(
                name = 'blind_up_' + blind_up_name,
                event = event,
                target_lambda = os.environ['EVENTBRIDGE_LAMBDA'],
                schedule = blind_up_date
            )

            # Create event for blind down
            print('Create event for blind ' + row['blind'] + ' down')
            blind_down_date = today_date + 'T' + blind_down.strftime("%H:%M") + ':00'
            blind_down_name = row['blind'] + "_" + blind_down_date.replace('-', '').replace(':', '').replace('T', '_')
            event = {
                "blind": row['blind'],
                "action": "down"
            }
            action_create(
                name = 'blind_down_' + blind_down_name,
                event = event,
                target_lambda = os.environ['EVENTBRIDGE_LAMBDA'],
                schedule = blind_down_date
            )

            row_boolean = True      
    
    if (row_boolean == True):
        # Insert log and notify only if there is almost 1 irrigation event
        # created
        if (config_params['log_enabled'] == True):
            event = {
                "type": 'blinds',
                "id": 'all',
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
        if (config_params['notify_enabled'] == True):
                body = {
                    "message": '<i>-- IoT v8 Event --</i>' + \
                  '\n<b>Type</b>: blinds' + \
                  ' | <b>Id</b>: all' + \
                  ' | <b>Status</b>: event_creation' + \
                  ' | <b>Data</b>: -'
                }
                ifttt_app(
                    key = config_params['ifttt_key'],
                    app_name = config_params['telegram_app'],
                    body = body
                )
        status = 200
        response_description = 'Registros de persianas insertados'
    else:
        status = 200
        response_description = 'Registros de persianas NO insertados'
    
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": response_description
    }

