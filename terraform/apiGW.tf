######################################
## API GW Creation
######################################
resource "aws_apigatewayv2_api" "iot_v8_api_gw_api" {
  name          = "iot-v8-api-gw"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"] # O especifica tu dominio aquí: ["https://midominio.com"]
    allow_methods = ["GET", "POST", "OPTIONS", "PUT", "DELETE", "PATCH"]
    allow_headers = ["Content-Type", "Authorization", "X-Amz-Date", "X-Api-Key", "X-Amz-Security-Token"]
    expose_headers = ["Content-Type", "Authorization"]
    max_age = 3600
  }
}

resource "aws_apigatewayv2_stage" "iot_v8_api_gw_stage" {
  api_id = aws_apigatewayv2_api.iot_v8_api_gw_api.id

  name        = "prod"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.iot_v8_api_gw_log_group.arn

    format = jsonencode({
      requestId               = "$context.requestId"
      sourceIp                = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
      }
    )
  }
}


resource "aws_cloudwatch_log_group" "iot_v8_api_gw_log_group" {
  name = "/aws/api-gw/${aws_apigatewayv2_api.iot_v8_api_gw_api.name}"

  retention_in_days = var.retention
}

############################################
## API GW Integration with Lambda (for each)
############################################
resource "aws_apigatewayv2_integration" "iot_v8_api_gw_integration" {
  for_each = var.lambdas

  api_id = aws_apigatewayv2_api.iot_v8_api_gw_api.id

  integration_uri    = aws_lambda_function.iot_v8_lambda_main[each.key].invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = each.value.apiMethod
}

resource "aws_apigatewayv2_route" "iot_v8_api_gw_route" {
  for_each = var.lambdas

  api_id = aws_apigatewayv2_api.iot_v8_api_gw_api.id

  route_key = each.value.apiRoute
  target    = "integrations/${aws_apigatewayv2_integration.iot_v8_api_gw_integration[each.key].id}"
}

resource "aws_lambda_permission" "iot_v8_api_gw_permission" {
  for_each = var.lambdas

  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.iot_v8_lambda_main[each.key].function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.iot_v8_api_gw_api.execution_arn}/*/*"
}