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
                  "handler": "sensor_event.sensor_event",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/sensorEvent"
                  },
               "calendarEvent" = {
                  "name": "iot-v8-calendar-event",
                  "handler": "calendar_event.calendar_event",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/calendarEvent"
                  }
   }
}

variable "retention"{
   # Retention in days
   # valid for log and DynamoDB
   type = number
   default = 5
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

