resource "aws_s3_bucket" "iot_v8_bucket" {
  bucket        = "iot-v8-bucket"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "iot_v8_bucket_access" {
  bucket = aws_s3_bucket.iot_v8_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
