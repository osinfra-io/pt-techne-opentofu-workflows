# Input Variables
# https://opentofu.org/docs/language/values/variables

variable "project" {
  description = "The project to create and manage resources in"
  type        = string
}

# Intentionally unused to exercise the -lint summary in the called workflows.
variable "intentional_lint_failure" {
  default     = null
  description = "Intentionally unused variable that triggers the core:unused-variable lint warning"
  type        = string
}
