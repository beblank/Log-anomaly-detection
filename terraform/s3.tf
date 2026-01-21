# S3 Bucket for Model Storage
resource "aws_s3_bucket" "ml_models" {
  bucket = var.s3_bucket_name
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-models"
    }
  )
}

resource "aws_s3_bucket_versioning" "ml_models" {
  bucket = aws_s3_bucket.ml_models.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "ml_models" {
  bucket = aws_s3_bucket.ml_models.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "ml_models" {
  bucket = aws_s3_bucket.ml_models.id
  
  rule {
    id     = "delete-old-versions"
    status = "Enabled"
    
    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
}

# S3 Bucket Policy for tenant isolation
resource "aws_s3_bucket_policy" "ml_models" {
  bucket = aws_s3_bucket.ml_models.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DenyIncorrectTenantAccess"
        Effect = "Deny"
        Principal = "*"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.ml_models.arn}/*"
        Condition = {
          StringNotLike = {
            "s3:prefix" = "tenant-*/*"
          }
        }
      }
    ]
  })
}
