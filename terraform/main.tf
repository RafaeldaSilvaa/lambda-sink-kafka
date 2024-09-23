provider "aws" {
  access_key = "test"
  secret_key = "test"
  region     = "us-east-1"
  skip_credentials_validation = true
  skip_requesting_account_id = true
  skip_metadata_api_check    = true
  endpoints {
    secretsmanager = "http://localhost:4566"
    rds           = "http://localhost:4566"
  }
}

resource "aws_secretsmanager_secret" "mysql_secret" {
  name        = "mysql_credential"
  description = "MySQL credentials"
}

resource "aws_secretsmanager_secret_version" "mysql_secret_version" {
  secret_id     = aws_secretsmanager_secret.mysql_secret.id
  secret_string = jsonencode({
    username = "root"
    password = "root"
    host     = "localhost"
    database = "test_db"
  })
}

