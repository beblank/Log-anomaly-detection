output "s3_bucket_name" {
  description = "S3 bucket name for ML models"
  value       = aws_s3_bucket.ml_models.bucket
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN"
  value       = aws_s3_bucket.ml_models.arn
}

output "ml_saas_app_policy_arn" {
  description = "IAM policy ARN for ML SaaS application"
  value       = aws_iam_policy.ml_saas_app.arn
}

output "ml_saas_eks_role_arn" {
  description = "IAM role ARN for EKS service account"
  value       = aws_iam_role.ml_saas_eks_role.arn
}
