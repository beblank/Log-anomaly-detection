# IAM Policy for ML SaaS Application
resource "aws_iam_policy" "ml_saas_app" {
  name        = "${var.project_name}-app-policy"
  description = "IAM policy for ML SaaS application"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.ml_models.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "${aws_s3_bucket.ml_models.arn}/*"
        ]
      }
    ]
  })
  
  tags = var.tags
}

# IAM Role for EKS Service Account (IRSA)
resource "aws_iam_role" "ml_saas_eks_role" {
  name = "${var.project_name}-eks-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/${var.eks_oidc_provider}"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${var.eks_oidc_provider}:sub" = "system:serviceaccount:ml-saas:ml-saas-api"
          }
        }
      }
    ]
  })
  
  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "ml_saas_eks_policy" {
  role       = aws_iam_role.ml_saas_eks_role.name
  policy_arn = aws_iam_policy.ml_saas_app.arn
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# Tenant IAM Role Template (to be created per tenant)
resource "aws_iam_role" "tenant_role_template" {
  count = 0  # Set to 0 as template, created dynamically per tenant
  
  name = "${var.project_name}-tenant-${count.index}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
  
  tags = var.tags
}

# Tenant IAM Policy Template
resource "aws_iam_policy" "tenant_policy_template" {
  count = 0  # Set to 0 as template
  
  name        = "${var.project_name}-tenant-${count.index}-policy"
  description = "IAM policy for tenant ${count.index}"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.ml_models.arn
        ]
        Condition = {
          StringLike = {
            "s3:prefix" = "tenant-${count.index}/*"
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "${aws_s3_bucket.ml_models.arn}/tenant-${count.index}/*"
        ]
      }
    ]
  })
  
  tags = var.tags
}
