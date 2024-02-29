variable "lambdas" {
   type    = map(object({
    name = string
    handler = string
    apiMethod = string
    apiRoute = string
   }))
   default = {
               "inputEvent" = {
                  "name": "iot-v8-sensor-event",
                  "handler": "sensor.sensor_event",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/sensorEvent"
                  },
               "calendarEvent" = {
                  "name": "iot-v8-schedule-event",
                  "handler": "eventbridge.schedule_event",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/scheduleEvent"
                  },
               "configStore" = {
                  "name": "iot-v8-config-store",
                  "handler": "config.config_store",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/configStore"
                  },
               "configRetrieve" = {
                  "name": "iot-v8-config-retrieve",
                  "handler": "config.config_retrieve",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/configRetrieve"
                  }
   }
}

variable "retention"{
   # Retention in days
   # valid for log and DynamoDB
   type = number
   default = 5
}

variable "lambda_timeout"{
   # Lambda timeout in seconds
   type = number
   default = 20
}

variable "events_lambda_arn"{
   # Lambda arn for receiving
   # eventbridge events
   # Need to be defined after creation
   type = string
   default = "PENDIENTE"
}


# variable "lambda_action_event"{
#     type = string
#     default = "actionEvent"
# }

# variable "lambdaTriggerRule"{
#     type = string
#     default = "inputAction"
# }

# variable "cronIrrigation"{
#     type = string
#     default = "cron(0 8,14,21 ? * * *)"
# }

# variable "cronBlinds"{
#     type = string
#     default = "cron(0 0 1 1 ? 2099)"
# }

