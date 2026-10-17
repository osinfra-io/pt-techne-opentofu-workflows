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
