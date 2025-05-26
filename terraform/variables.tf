variable "lambdas" {
   type    = map(object({
    name = string
    handler = string
    apiMethod = string
    apiRoute = string
    action_lambda_arn = string
    alarms_lambda_arn = string
   }))
   default = {
               "configStore" = {
                  "name": "iot-v8-config-store",
                  "handler": "config.config_store",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/configStore",
                  "action_lambda_arn": "",
                  "alarms_lambda_arn": ""
                  },
               "configRetrieve" = {
                  "name": "iot-v8-config-retrieve",
                  "handler": "config.config_retrieve",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/configRetrieve",
                  "action_lambda_arn": "",
                  "alarms_lambda_arn": ""
                  },
               "irrigationEvent" = {
                  "name": "iot-v8-irrigation-event",
                  "handler": "events.irrigation_event",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/irrigationEvent",
                  "action_lambda_arn": "arn:aws:lambda:eu-central-1:428652792036:function:iot-v8-irrigation-action",
                  "alarms_lambda_arn": ""
                  },
               "irrigationAction" = {
                  "name": "iot-v8-irrigation-action",
                  "handler": "actions.irrigation_action",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/irrigationAction",
                  "action_lambda_arn": "",
                  "alarms_lambda_arn": ""
                  }
               "blindsEvent" = {
                  "name": "iot-v8-blinds-event",
                  "handler": "events.blinds_event",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/blindsEvent",
                  "action_lambda_arn": "arn:aws:lambda:eu-central-1:428652792036:function:iot-v8-blinds-action",
                  "alarms_lambda_arn": ""
                  },
               "blindsAction" = {
                  "name": "iot-v8-blinds-action",
                  "handler": "actions.blinds_action",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/blindsAction",
                  "action_lambda_arn": "",
                  "alarms_lambda_arn": ""
                  },
               "alarmEvent" = {
                  "name": "iot-v8-alarm-event",
                  "handler": "events.alarm_event",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/alarmEvent",
                  "action_lambda_arn": "",
                  "alarms_lambda_arn": "arn:aws:lambda:eu-central-1:428652792036:function:iot-v8-alarms-action"
                  },
               "alarmsAction" = {
                  "name": "iot-v8-alarms-action",
                  "handler": "actions.alarms_action",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/alarmsAction",
                  "action_lambda_arn": "",
                  "alarms_lambda_arn": ""
                  },
               "deleteActions" = {
                  "name": "iot-v8-delete-Actions",
                  "handler": "events.delete_actions",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/deleteActions",
                  "action_lambda_arn": "",
                  "alarms_lambda_arn": ""
                  },
               "deleteAlarms" = {
                  "name": "iot-v8-delete-alarms",
                  "handler": "events.delete_alarms",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/deleteAlarms",
                  "action_lambda_arn": "",
                  "alarms_lambda_arn": ""
                  },
               "getEvents" = {
                  "name": "iot-v8-get-events",
                  "handler": "events.get_events",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/getEvents",
                  "action_lambda_arn": "",
                  "alarms_lambda_arn": ""
                  },
               "rainEvent" = {
                  "name": "iot-v8-rain-event",
                  "handler": "events.rain_event",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/rainEvent",
                  "action_lambda_arn": "arn:aws:lambda:eu-central-1:428652792036:function:iot-v8-blinds-action",
                  "alarms_lambda_arn": ""
                  },
               "setTemperature" = {
                  "name": "iot-v8-set-temperature",
                  "handler": "temperature.set_temperature",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/setTemperature",
                  "action_lambda_arn": "",
                  "alarms_lambda_arn": ""
                  },
               "fixTemperature" = {
                  "name": "iot-v8-fix-temperature",
                  "handler": "temperature.fix_temperature",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/fixTemperature",
                  "action_lambda_arn": "",
                  "alarms_lambda_arn": ""
                  },
               "getTemperature" = {
                  "name": "iot-v8-get-temperature",
                  "handler": "temperature.get_temperature",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/getTemperature",
                  "action_lambda_arn": "",
                  "alarms_lambda_arn": ""
                  }
   }
}

variable "retention"{
   # Retention in days
   # valid for log and DynamoDB
   type = number
   default = 14
}

variable "lambda_timeout"{
   # Lambda timeout in seconds
   type = number
   default = 25
}

variable "irrigation_lambda_arn"{
   # Lambda arn for create irrigation
   # actions
   type = string
   default = "arn:aws:lambda:eu-central-1:428652792036:function:iot-v8-irrigation-event"
}

variable "blinds_cron"{
   # Cron for generate irrigation actions
   type = string
   default = "cron(05 00 * * ? *)"
}

variable "blinds_lambda_arn"{
   # Lambda arn for create irrigation
   # actions
   type = string
   default = "arn:aws:lambda:eu-central-1:428652792036:function:iot-v8-blinds-event"
}

variable "irrigation_cron"{
   # Cron for generate irrigation actions
   type = string
   default = "cron(05 00 * * ? *)"
}

variable "eventbridge_events_group"{
   # Eventbridge schedule group
   # for create events
   type = string
   default = "iot-v8-events"
}

variable "eventbridge_actions_group"{
   # Eventbridge schedule group
   # for put actions
   type = string
   default = "iot-v8-actions"
}

variable "eventbridge_alarms_group"{
   # Eventbridge schedule group
   # for create alarm triggers
   type = string
   default = "iot-v8-alarms"
}
