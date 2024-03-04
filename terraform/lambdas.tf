######################################
## File creation
######################################
data "archive_file" "iot_v8_lambda_file" {
  type = "zip"

  source_dir  = "../${path.module}/app"
  output_path = "../${path.module}/terraform/files/app.zip"
}

resource "aws_s3_object" "iot_v8_s3_object" {
  bucket = aws_s3_bucket.iot_v8_bucket.id

  key    = "app.zip"
  source = data.archive_file.iot_v8_lambda_file.output_path

  etag = filemd5(data.archive_file.iot_v8_lambda_file.output_path)
}

######################################
## Lambda creation (for each)
######################################
resource "aws_lambda_function" "iot_v8_lambda_main" {
  for_each      = var.lambdas

  function_name = each.value.name

  s3_bucket = aws_s3_bucket.iot_v8_bucket.id
  s3_key    = aws_s3_object.iot_v8_s3_object.key

  runtime = "python3.12"
  handler = each.value.handler

  source_code_hash = data.archive_file.iot_v8_lambda_file.output_base64sha256

  role = aws_iam_role.iot_v8_lambda_role.arn

  timeout = var.lambda_timeout

  environment {
    variables = {
      RETENTION_DAYS = var.retention,
      AWS_DYNAMO_EVENTS_TABLE = aws_dynamodb_table.iot_v8_events.name,
      S3_BUCKET = aws_s3_bucket.iot_v8_bucket.bucket,
      EVENTBRIDGE_ROLE = aws_iam_role.iot_v8_eventbridge_role.arn,
      EVENTBRIDGE_GROUP = var.eventbridge_group,
      EVENTBRIDGE_LAMBDA = each.value.lambda_arn
    }
  }

}

resource "aws_cloudwatch_log_group" "iot_lambda_main" {
  for_each = var.lambdas
  name = "/aws/lambda/${aws_lambda_function.iot_v8_lambda_main[each.key].function_name}"

  retention_in_days = var.retention
}