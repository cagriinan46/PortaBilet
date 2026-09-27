terraform {
  backend "s3" {
    bucket              = "portabilet-tf-state-069347174731"
    key                 = "vpc/terraform.tfstate"
    region              = "eu-central-1"
    use_lockfile        = true
    encrypt             = true
    allowed_account_ids = ["069347174731"]
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region              = var.aws_region
  allowed_account_ids = ["069347174731"]
}
