variable "lambdas" {
   type    = map(object({
    name = string
    handler = string
    apiMethod = string
    apiRoute = string
    lambda_arn = string
   }))
   default = {
               "configStore" = {
                  "name": "iot-v8-config-store",
                  "handler": "config.config_store",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/configStore",
                  "lambda_arn": ""
                  },
               "configRetrieve" = {
                  "name": "iot-v8-config-retrieve",
                  "handler": "config.config_retrieve",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/configRetrieve",
                  "lambda_arn": ""
                  },
               "irrigationEvent" = {
                  "name": "iot-v8-irrigation-event",
                  "handler": "events.irrigation_event",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/irrigationEvent",
                  "lambda_arn": "arn:aws:lambda:eu-central-1:428652792036:function:iot-v8-irrigation-action"
                  },
               "irrigationAction" = {
                  "name": "iot-v8-irrigation-action",
                  "handler": "actions.irrigation_action",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/irrigationAction",
                  "lambda_arn": ""
                  }
               "blindsEvent" = {
                  "name": "iot-v8-blinds-event",
                  "handler": "events.blinds_event",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/blindsEvent",
                  "lambda_arn": "arn:aws:lambda:eu-central-1:428652792036:function:iot-v8-blinds-action"
                  },
               "blindsAction" = {
                  "name": "iot-v8-blinds-action",
                  "handler": "actions.blinds_action",
                  "apiMethod": "POST",
                  "apiRoute": "POST /v8/blindsAction",
                  "lambda_arn": ""
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
   default = "cron(00 02 * * ? *)"
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
   default = "cron(00 23 * * ? *)"
}

variable "eventbridge_group"{
   # Eventbridge schedule group
   # for put actions
   type = string
   default = "iot-v8-actions"
}

