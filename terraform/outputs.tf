############################################
## Show URL for API GW
############################################
output "iot_api_gw_url" {
  value = aws_apigatewayv2_stage.iot_v8_api_gw_stage.invoke_url
}

# output "iot_sqs_queue_url" {
#   value = aws_sqs_queue.iot_v8_sqs_queue.url
# }
