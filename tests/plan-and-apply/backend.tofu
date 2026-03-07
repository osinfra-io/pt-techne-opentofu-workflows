terraform {
  backend "gcs" {
    bucket             = var.state_bucket
    kms_encryption_key = var.state_kms_encryption_key
    prefix             = var.state_prefix
  }
}
