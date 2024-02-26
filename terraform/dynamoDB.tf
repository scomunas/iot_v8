resource "aws_dynamodb_table" "iot_v8_events" {
    name = "iot-v8-events"
    billing_mode = "PAY_PER_REQUEST"
    stream_enabled = true
    stream_view_type = "NEW_IMAGE"

    attribute {
        name = "date"
        type = "S"
    }

    attribute {
        name = "id"
        type = "S"
    }

    attribute {
        name = "state"
        type = "S"
    }

    ttl {
        enabled = true
        attribute_name = "date_ttl"
    }

    hash_key = "id"
    range_key = "date"

    global_secondary_index {
        name               = "state_index"
        hash_key           = "state"
        range_key          = "date"
        projection_type    = "ALL"
    }
}

# resource "aws_dynamodb_table" "iot_v8_status" {
#     name = "iot-v8-status"
#     billing_mode = "PAY_PER_REQUEST"
#     stream_enabled = true
#     stream_view_type = "NEW_IMAGE"

#     attribute {
#         name = "device_id"
#         type = "S"
#     }
#     attribute {
#         name = "channel"
#         type = "S"
#     }

#     hash_key = "device_id"
#     range_key = "channel"
# }

# resource "aws_dynamodb_table" "iot_v8_triggers" {
#     name = "iot-v8-triggers"
#     billing_mode = "PAY_PER_REQUEST"
#     stream_enabled = true
#     stream_view_type = "NEW_IMAGE"

#     attribute {
#         name = "device_id"
#         type = "S"
#     }
#     attribute {
#         name = "id"
#         type = "S"
#     }

#     hash_key = "device_id"
#     range_key = "id"
# }

# BBDD para pruebas
# resource "aws_dynamodb_table" "prueba" {
#     name = "prueba"
#     billing_mode = "PAY_PER_REQUEST"
#     stream_enabled = true
#     stream_view_type = "NEW_IMAGE"

#     attribute {
#         name = "id"
#         type = "S"
#         }
#     attribute {
#         name = "fecha"
#         type = "S"
#         }

#     hash_key = "id"
#     range_key = "fecha"

#     global_secondary_index {
#         name               = "pruebaIndex"
#         hash_key           = "fecha"
#         range_key          = "id"
#         projection_type    = "ALL"
#     }
# }

