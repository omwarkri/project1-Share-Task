# AWS Secrets Manager for sensitive data

resource "random_password" "django_secret_key" {
  length  = 50
  special = true
}

resource "aws_secretsmanager_secret" "django_secret_key" {
  name = "${var.project_name}-django-secret-key"

  tags = {
    Name = "${var.project_name}-django-secret-key"
  }
}

resource "aws_secretsmanager_secret_version" "django_secret_key" {
  secret_id     = aws_secretsmanager_secret.django_secret_key.id
  secret_string = random_password.django_secret_key.result
}

resource "aws_secretsmanager_secret" "db_url" {
  name = "${var.project_name}-database-url"

  tags = {
    Name = "${var.project_name}-database-url"
  }
}

resource "aws_secretsmanager_secret_version" "db_url" {
  secret_id = aws_secretsmanager_secret.db_url.id
  secret_string = "postgresql://admin:${random_password.db_password.result}@${aws_db_instance.main.address}:5432/${var.db_name}"
}

output "secrets_created" {
  value = "Django secret key and database URL secrets created in Secrets Manager"
}
