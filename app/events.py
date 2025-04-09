######################################
## Get calendar events and do actions
## 
######################################

from modules import get_config_file, event_create, insert_db, \
                    ifttt_app, get_sunrise, get_holidays, event_check, \
                    event_delete, check_db
import json
import os
from datetime import datetime, timedelta
import pytz

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
    CET = pytz.timezone("Europe/Madrid")
    today_datetime = datetime.now().astimezone(CET)
    today_weekday = days_of_week[today_datetime.weekday()]
    today_date = today_datetime.strftime("%Y-%m-%d")

    # Each row in irrigation list
    print('For each row in irrigation list')
    irrigation_boolean = False
    for row in irrigation:
        if (row['weekday'] == today_weekday and
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
            irrigation_date = today_date + 'T' + irrigation_start + ':00'
            irrigation_name = irrigation_date.replace('-', '').replace(':', '').replace('T', '_')
            event = {
                "type": "irrigation",
                "action": "start"
            }
            event_create(
                name = 'irrigation_start_' + irrigation_name,
                event = event,
                target_lambda = os.environ['EVENTBRIDGE_ACTIONS_LAMBDA'],
                schedule = irrigation_date,
                event_group = os.environ['EVENTBRIDGE_ACTIONS_GROUP']
            )

            # Create event for stop irrigation
            print('Create event for stop irrigation')
            irrigation_date = today_date + 'T' + irrigation_stop + ':00'
            irrigation_name = irrigation_date.replace('-', '').replace(':', '').replace('T', '_')
            event = {
                "type": "irrigation",
                "action": "stop"
            }
            event_create(
                name = 'irrigation_stop_' + irrigation_name,
                event = event,
                target_lambda = os.environ['EVENTBRIDGE_ACTIONS_LAMBDA'],
                schedule = irrigation_date,
                event_group = os.environ['EVENTBRIDGE_ACTIONS_GROUP']
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
                "event_type": 'irrigation',
                "event_id": 'terraza',
                "event_state": 'event_creation',
                "event_data": '-'
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
    body = json.loads(event["body"])
    print(body)

    print("Create blind events -------------------------------------------")
    # Get config data and calculate today variables
    print('Get config data and calculate today variables')
    config = get_config_file()
    blinds = config['blinds']
    holidays = config['holidays']
    config_params = config['config']

    # Calculate dates and holiday
    CET = pytz.timezone("Europe/Madrid")
    today_datetime = datetime.now().astimezone(CET)
    today_weekday = days_of_week[today_datetime.weekday()]
    today_date = today_datetime.strftime("%Y-%m-%d")
    holiday_list = get_holidays("ES", "ES-CT")['results']
    for holiday in holidays:
        holiday_list.append(holiday['date'])

    ##### Deleted because we start having sunrise/sunset event
    # Get sunrise from sunrisesunset.io
    # print('Get sunrise from sunrisesunset.io')
    # sunrise_data = get_sunrise(
    #     lat = config_params['blinds_lat'],
    #     long = config_params['blinds_long']
    # )
    # Get sunrise/sunset time
    sunrise_data = {}
    sunrise_data['status'] = 400
    event_datetime = today_datetime + timedelta(minutes=2)
    event_hour = str(event_datetime.hour) + ":" + str(event_datetime.minute)
    if (body['type'] == 'sunrise'):
        sunrise_data['sunrise'] = datetime.strptime(event_hour, '%H:%M')
        sunrise_data['status'] = 200
    if (body['type'] == 'sunset'):
        sunrise_data['sunset'] = datetime.strptime(event_hour, '%H:%M')
        sunrise_data['status'] = 200

    
    # Each row in blinds list
    print('For each row in blind list')
    row_boolean = False
    for row in blinds:
        if row['sunrise'] == True:
            # Only if sunrise is enabled
            # Get config times
            if (today_weekday not in days_of_weekend and
                today_date not in holiday_list):
                # Normal day
                blind_up = datetime.strptime(row['time_normal'].split('-')[0], '%H:%M')
                blind_down = datetime.strptime(row['time_normal'].split('-')[1], '%H:%M')
            else:
                # "Holiday" day
                blind_up = datetime.strptime(row['time_holiday'].split('-')[0], '%H:%M')
                blind_down = datetime.strptime(row['time_holiday'].split('-')[1], '%H:%M')

            # Correct if sunrise data
            if sunrise_data['status'] == 200:
                # Only if we can get correct data
                # we will correct up and down times
                if ('sunrise' in sunrise_data.keys()):
                    if blind_up < sunrise_data['sunrise']:
                        blind_up = sunrise_data['sunrise']
                if ('sunset' in sunrise_data.keys()):
                    if blind_down < sunrise_data['sunset']:
                        blind_down = sunrise_data['sunset']
            
            # Create event for blind up
            if (body['type'] == 'sunrise'):
                print('Create event for blind ' + row['blind'] + ' up')
                blind_date = today_date + 'T' + blind_up.strftime("%H:%M") + ':00'
                blind_name = row['blind'] + "_" + blind_date.replace('-', '').replace(':', '').replace('T', '_')
                event = {
                    "blind": row['blind'],
                    "action": "up"
                }
                event_create(
                    name = 'blind_up_' + blind_name,
                    event = event,
                    target_lambda = os.environ['EVENTBRIDGE_ACTIONS_LAMBDA'],
                    schedule = blind_date,
                    event_group = os.environ['EVENTBRIDGE_ACTIONS_GROUP']
                )

            # Create event for blind down
            if (body['type'] == 'sunset'):
                print('Create event for blind ' + row['blind'] + ' down')
                blind_date = today_date + 'T' + blind_down.strftime("%H:%M") + ':00'
                blind_name = row['blind'] + "_" + blind_date.replace('-', '').replace(':', '').replace('T', '_')
                event = {
                    "blind": row['blind'],
                    "action": "down"
                }
                event_create(
                    name = 'blind_down_' + blind_name,
                    event = event,
                    target_lambda = os.environ['EVENTBRIDGE_ACTIONS_LAMBDA'],
                    schedule = blind_date,
                    event_group = os.environ['EVENTBRIDGE_ACTIONS_GROUP']
                )

            row_boolean = True      
    
    if (row_boolean == True):
        # Insert log and notify only if there is almost 1 blinds event
        # created
        if (config_params['log_enabled'] == True):
            event = {
                "event_type": 'blinds',
                "event_id": 'all',
                "event_state": body['type'],
                "event_data": '-'
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

def alarm_event(event, context):
    ## Get Event parameters
    print("Sensor Event received-------------------------------------------")
    # print(event)
    body = json.loads(event["body"])
    # print(body)

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
        print('The request have not all the fields required')
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": "The request have not all the fields required"
        }

    print("Create alarm events -------------------------------------------")
    # Get config data and store new config ASAP if needed
    print('Get config data and check if trigger fired')
    config = get_config_file()
    alarms = config['alarms']
    for trigger in alarms:
        print('Checking alarm: ' + json.dumps(trigger)) 
        if ((trigger['type'] == body['type'] or
            trigger['type'] == 'any') and
            (trigger['id'] == body['id'] or
            trigger['id'] == 'any') and
            (trigger['state'] == body['state'] or
            trigger['state'] == 'any')):
            # Alarm triggered, check for events
            event_generated = event_check(
                group = os.environ['EVENTBRIDGE_ALARMS_GROUP'],
                rule = 'alarm_fired_' + str(trigger['rule'])
            )
            # If there's no event, create it
            print("Event fired: " + str(event_generated))
            if (event_generated == False):
                event = {
                    "rule": trigger,
                    "event": body
                }
                CET = pytz.timezone("Europe/Madrid")
                alarm_date = datetime.now().astimezone(CET) + \
                            timedelta(minutes=int(trigger['minutes']))
                event_create(
                    name = 'alarm_fired_' + str(trigger['rule']),
                    event = event,
                    target_lambda = os.environ['EVENTBRIDGE_ALARMS_LAMBDA'],
                    schedule = alarm_date.strftime('%Y-%m-%dT%H:%M:%S'),
                    event_group = os.environ['EVENTBRIDGE_ALARMS_GROUP']
                )

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


    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": "Sensor event processed"
    }

def rain_event(event, context):
    #### ONLY Log events, sensor is not working properly

    ## Get Event parameters
    print("Sensor Event received-------------------------------------------")
    print(event)
    body = json.loads(event["body"])
    # print(body)

    ## Create row for insert
    if ('device_name' in body.keys() and
        'device_action' in body.keys() and
        'event' in body.keys()):
        event_parameters = {
        "event_type": body['device_action'],
        "event_id": body['device_name'],
        "event_state": body['event'],
        "event_data": "-"
        }
    else:
        print('The request have not all the fields required')
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": "The request have not all the fields required"
        }

    print("Create rain events -------------------------------------------")
    # Get config data and calculate today variables
    print('Get config data and calculate today variables')
    config = get_config_file()
    blinds = config['blinds']
    holidays = config['holidays']
    config_params = config['config']

    # # Calculate dates and holiday
    # CET = pytz.timezone("Europe/Madrid")
    # today_datetime = datetime.now().astimezone(CET)
    # today_weekday = days_of_week[today_datetime.weekday()]
    # today_date = today_datetime.strftime("%Y%m%d")
    # holiday_list = get_holidays("ES", "ES-CT")['results']
    # for holiday in holidays:
    #     holiday_list.append(holiday['date'])

    # # Check events for sunrise or sunset
    # event_number, events = check_db(
    #     table_name = os.environ['AWS_DYNAMO_EVENTS_TABLE'], 
    #     type = 'blinds', 
    #     date = today_date, 
    #     id = 'any', 
    #     state = 'any'
    # )
    # # print(events)

    # # Get only last rain event
    # rain_events = []
    # blind_events = {}
    # if (event_number > 0):
    #     for event in events:
    #         event_id = event['event_id']['S']
    #         event_date = event['event_date']['S']
    #         event_state = event['event_state']['S']
    #         if (event_state == 'rain_start') or (event_state == 'rain_stop')):
    #             rain_events.append(event_state)
    #         if ((event_state == "up") or (event_state == "down")):
    #             if (event_id not in blind_events.keys()):
    #                 # No Blind event registered for this id
    #                 blind_events[event_id] = {}
    #                 blind_events[event_id][event_state + "_event_date"] = event_date
    #             else:
    #                 # Event registered for this blind
    #                 if ((event_state + "_event_date") not in blind_events[event_id].keys()):
    #                     # Date not registered for this state
    #                     blind_events[event_id][event_state + "_event_date"] = event_date
    #                 else:
    #                     if (event_date > blind_events[event_id][event_state + "_event_date"]):
    #                         # Event later than registered
    #                         blind_events[event_id][event_state + "_event_date"] = event_date
    # print(blind_events)

    # # Only if stop event comes next to start
    # ##### TODO

    # sunrise_date = pytz.timezone('CET').localize(datetime.strptime('2000-01-01T00:00:00', '%Y-%m-%dT%H:%M:%S'))
    # sunset_date = pytz.timezone('CET').localize(datetime.strptime('2100-01-01T00:00:00', '%Y-%m-%dT%H:%M:%S'))
    # if (event_number > 0):
    #     # If sunrise event has been registered
    #     for event in events:
    #         if (event['event_state']['S'] == 'sunrise'):
    #             event_date = datetime.strptime(event['event_data']['S'], '%Y-%m-%dT%H:%M:%S')
    #             sunrise_date = pytz.timezone('CET').localize(event_date)
    #         if (event['event_state']['S'] == 'sunset'):
    #             event_date = datetime.strptime(event['event_data']['S'], '%Y-%m-%dT%H:%M:%S')
    #             sunset_date = pytz.timezone('CET').localize(event_date)
    # print(today_datetime)
    # print(sunrise_date)
    # print(sunset_date)

    # Check daytime schedule, if it's night do nothing
    # if ((today_datetime > sunrise_date) and
    #     (today_datetime < sunset_date)):
    #     print("Daytime, checking if we have to up or down blinds")
    #     if (body['event'] == 'rain_stop'):
    #         # Rain stops, please up the blinds
    #         # Each row in blinds list
    #         print('Rain Stop... For each row in blind list')
    #         for row in blinds:
    #             if row['rain'] == True:
    #                 # Only if rain is enabled
    #                 print('Create event for blind ' + row['blind'] + ' up')
    #                 blind_date = datetime.strftime(today_datetime + timedelta(minutes=1), '%Y-%m-%dT%H:%M:%S')
    #                 blind_name = row['blind'] + "_" + blind_date.replace('-', '').replace(':', '').replace('T', '_')
    #                 event = {
    #                     "blind": row['blind'],
    #                     "action": "up"
    #                 }
    #                 event_create(
    #                     name = 'blind_up_' + blind_name,
    #                     event = event,
    #                     target_lambda = os.environ['EVENTBRIDGE_ACTIONS_LAMBDA'],
    #                     schedule = blind_date,
    #                     event_group = os.environ['EVENTBRIDGE_ACTIONS_GROUP']
    #                 )

    #     if (body['event'] == 'rain_start'):
    #         # Rain start, please down the blinds
    #         # Each row in blinds list
    #         print('Rain Start... For each row in blind list')
    #         for row in blinds:
    #             if row['rain'] == True:
    #                 # Only if rain is enabled
    #                 print('Create event for blind ' + row['blind'] + ' down')
    #                 blind_date = datetime.strftime(today_datetime + timedelta(minutes=1), '%Y-%m-%dT%H:%M:%S')
    #                 blind_name = row['blind'] + "_" + blind_date.replace('-', '').replace(':', '').replace('T', '_')
    #                 event = {
    #                     "blind": row['blind'],
    #                     "action": "down"
    #                 }
    #                 event_create(
    #                     name = 'blind_down_' + blind_name,
    #                     event = event,
    #                     target_lambda = os.environ['EVENTBRIDGE_ACTIONS_LAMBDA'],
    #                     schedule = blind_date,
    #                     event_group = os.environ['EVENTBRIDGE_ACTIONS_GROUP']
    #                 )

    # Insert log and notify only if there is almost 1 blinds event
    # created
    if (config_params['log_enabled'] == True):
        event = {
            "event_type": 'blinds',
            "event_id": 'all',
            "event_state": body['event'],
            "event_data": body['device_name']
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
                ' | <b>Status</b>: ' + body['event'] + \
                ' | <b>Data</b>: ' + body['device_name']
            }
            ifttt_app(
                key = config_params['ifttt_key'],
                app_name = config_params['telegram_app'],
                body = body
            )
    status = 200
    response_description = 'Registros de persianas insertados por lluvia'
    
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": response_description
    }

def delete_actions(event, context):
    ## Get Event parameters
    print("Sensor Event received-------------------------------------------")
    # print(event)
    body = json.loads(event["body"])
    # print(body)

    ## Check if event have the fields
    ## required
    if ('name_prefix' in body.keys()):
        response = event_delete(
            group = os.environ['EVENTBRIDGE_ACTIONS_GROUP'],
            name_prefix = body['name_prefix']
        )

        if (response == False):
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": "Error deleting events"
            }

    else:
        print('The request have not all the fields required')
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": "The request have not all the fields required"
        }

    # Get config data and calculate today variables
    print('Get config data and calculate today variables')
    config = get_config_file()
    config_params = config['config']

    if (config_params['log_enabled'] == True):
        event = {
            "event_type": 'events',
            "event_id": 'all',
            "event_state": 'actions_deleted',
            "event_data": 'Name prefix: ' + body['name_prefix']
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
                '\n<b>Type</b>: events' + \
                ' | <b>Id</b>: all' + \
                ' | <b>Status</b>: actions_deleted' + \
                ' | <b>Data</b>: Name prefix: ' + body['name_prefix']
            }
            ifttt_app(
                key = config_params['ifttt_key'],
                app_name = config_params['telegram_app'],
                body = body
            )
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": "Events deleted"
    }

def delete_alarms(event, context):
    ## Get Event parameters
    print("Sensor Event received-------------------------------------------")
    # print(event)
    body = json.loads(event["body"])
    # print(body)

    ## Check if event have the fields
    ## required
    if ('name_prefix' in body.keys()):
        response = event_delete(
            group = os.environ['EVENTBRIDGE_ALARMS_GROUP'],
            name_prefix = body['name_prefix']
        )

        if (response == False):
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": "Error deleting alarms"
            }

    else:
        print('The request have not all the fields required')
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": "The request have not all the fields required"
        }

    # Get config data and calculate today variables
    print('Get config data and calculate today variables')
    config = get_config_file()
    config_params = config['config']

    if (config_params['log_enabled'] == True):
        event = {
            "event_type": 'events',
            "event_id": 'all',
            "event_state": 'alarms_deleted',
            "event_data": 'Name prefix: ' + body['name_prefix']
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
                '\n<b>Type</b>: events' + \
                ' | <b>Id</b>: all' + \
                ' | <b>Status</b>: alarms_deleted' + \
                ' | <b>Data</b>: Name prefix: ' + body['name_prefix']
            }
            ifttt_app(
                key = config_params['ifttt_key'],
                app_name = config_params['telegram_app'],
                body = body
            )
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": "Alarms deleted"
    }

def get_events(event, context):
    ## Get Event parameters
    print("Get Events -------------------------------------------")
    # print(event)
    body = json.loads(event["body"])
    # print(body)
    
    if ('event_type' in body.keys()):
        print('Evento correcto, tipo de evento detectado')
        event_type = body['event_type']
        if ((event_type == 'blinds') 
            or (event_type == 'alarm') 
            or (event_type == 'events')
            or (event_type == 'irrigation')):
            # Check events
            event_number, events = check_db(
                table_name = os.environ['AWS_DYNAMO_EVENTS_TABLE'], 
                type = event_type, 
                date = '20250101', 
                id = '', 
                state = ''
            )
            # print(events)
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps(events)
            }
        else:
            status = 400
            response_description = 'Evento no compatible'
    else:
        status = 400
        response_description = 'Tipo de evento no indicado'