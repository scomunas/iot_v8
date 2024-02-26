######################################
## Role and profile creation
######################################

resource "aws_iam_role" "iot_v8_lambda_role" {
  name = "iot-v8-lambda-role"

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "iot_v8_lambda_policy" {
  role       = aws_iam_role.iot_v8_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "iot_dynamo_policy" {
  role       = aws_iam_role.iot_v8_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

# resource "aws_iam_role_policy_attachment" "iot_sqs_policy" {
#   role       = aws_iam_role.iot_v8_lambda_role.name
#   policy_arn = "arn:aws:iam::aws:policy/AmazonSQSFullAccess"
# }

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

  environment {
    variables = {
      RETENTION_DAYS = var.retention,
      AWS_DYNAMO_EVENTS_TABLE = aws_dynamodb_table.iot_v8_events.name,
      IFTTT_URL = "https://maker.ifttt.com/trigger/app_name_change/json/with/key/gcs4wieOf6v8rnA-CD8QbK3XP39vs_FIfnjvM-2Y6LA"
    }
  }

}

resource "aws_cloudwatch_log_group" "iot_lambda_main" {
  for_each = var.lambdas
  name = "/aws/lambda/${aws_lambda_function.iot_v8_lambda_main[each.key].function_name}"

  retention_in_days = var.retention
}