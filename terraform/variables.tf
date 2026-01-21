variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "ml-saas"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "s3_bucket_name" {
  description = "S3 bucket name for ML models"
  type        = string
  default     = "ml-saas-models"
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "ML-SaaS"
    ManagedBy   = "Terraform"
  }
}
