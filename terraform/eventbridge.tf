
# Eventbridge schedules creation

module "eventbridge" {
  source = "terraform-aws-modules/eventbridge/aws"

  create_bus = false

  schedule_groups = {
    eventbridge_events = {
      name = "iot-v8-events"
    }
    eventbridge_actions = {
      name = var.eventbridge_group
    }
  }
}

# Event for generate irrigation actions
resource "aws_scheduler_schedule" "iot_v8_irrigation_schedule" {
  name       = "iot-v8-irrigation-schedule"
  group_name = "iot-v8-events"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = var.irrigation_cron
  schedule_expression_timezone = "CET"

  target {
    arn      = var.irrigation_lambda_arn
    role_arn = aws_iam_role.iot_v8_eventbridge_role.arn
  }
}

# Event for generate blinds actions
resource "aws_scheduler_schedule" "iot_v8_blinds_schedule" {
  name       = "iot-v8-blinds-schedule"
  group_name = "iot-v8-events"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = var.blinds_cron
  schedule_expression_timezone = "CET"

  target {
    arn      = var.blinds_lambda_arn
    role_arn = aws_iam_role.iot_v8_eventbridge_role.arn
  }
}