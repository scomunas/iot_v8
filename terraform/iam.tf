######################################
## Role and profile creation for
## lambdas
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

resource "aws_iam_role_policy_attachment" "iot_v8_policy_lambda_execution" {
  role       = aws_iam_role.iot_v8_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "iot_v8_policy_lambda_execution1" {
  role       = aws_iam_role.iot_v8_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaInvocation-DynamoDB"
}

resource "aws_iam_role_policy_attachment" "iot_v8_policy_lambda_dynamo" {
  role       = aws_iam_role.iot_v8_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_iam_role_policy_attachment" "iot_v8_policy_lambda_s3" {
  role       = aws_iam_role.iot_v8_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "iot_v8_policy_lambda_eventbridge" {
  role       = aws_iam_role.iot_v8_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess"
}

######################################
## Role and profile creation for
## eventbridge
######################################

resource "aws_iam_role" "iot_v8_eventbridge_role" {
  name = "iot-v8-eventbridge-role"

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "scheduler.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "iot_v8_policy_eventbridge_execution" {
  role       = aws_iam_role.iot_v8_eventbridge_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "iot_v8_policy_eventbridge_execution2" {
  role       = aws_iam_role.iot_v8_eventbridge_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambdaInvocation-DynamoDB"
}

