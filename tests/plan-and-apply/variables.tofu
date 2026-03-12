# Input Variables
# https://opentofu.org/docs/language/values/variables

variable "project" {
  description = "The project to create and manage resources in"
  type        = string
}

variable "project_billing_account" {
  default     = "01C550-A2C86B-B8F16B"
  description = "The billing account to associate with the project"
  type        = string
}

variable "project_cis_2_2_logging_sink_project_id" {
  description = "The CIS 2.2 logging sink project ID"
  type        = string
}

# These three state_* variables are required for early variable evaluation for backend and provider configuration.
# They are defined in the GitHub Actions called workflows and should NOT be set in the OpenTofu configuration.

variable "state_bucket" {
  description = "The name of the GCS bucket to store state files"
  type        = string
}

variable "state_kms_encryption_key" {
  description = "The KMS encryption key for state and plan files"
  type        = string
}

variable "state_prefix" {
  description = "The prefix for state files in the GCS bucket"
  type        = string
}
