resource "aws_dynamodb_table" "iot_v8_events" {
    name = "iot-v8-events"
    billing_mode = "PAY_PER_REQUEST"
    stream_enabled = true
    stream_view_type = "NEW_IMAGE"

    attribute {
        name = "event_date"
        type = "S"
    }

    attribute {
        name = "event_type"
        type = "S"
    }

    ttl {
        enabled = true
        attribute_name = "event_date_ttl"
    }

    hash_key = "event_type"
    range_key = "event_date"

    # attribute {
    #     name = "state"
    #     type = "S"
    # }

    # global_secondary_index {
    #     name               = "state_index"
    #     hash_key           = "state"
    #     range_key          = "event_date"
    #     projection_type    = "ALL"
    # }
}
