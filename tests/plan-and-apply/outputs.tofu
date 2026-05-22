# Output Values
# https://opentofu.org/docs/language/values/outputs

output "project_id" {
  description = "The project ID"
  value       = var.project
}

output "random_string" {
  description = "The random string value"
  value       = random_string.test.result
}

output "sensitive_value" {
  description = "A sensitive output to verify HTML escaping of <sensitive>"
  sensitive   = true
  value       = random_string.test.result
}

output "simple_map" {
  description = "A multi-line map output to verify details rendering"
  value = {
    environment = module.core_helpers.environment
    env         = module.core_helpers.env
    project_id  = var.project
    region      = "us-east1"
  }
}

output "nested_object" {
  description = "A nested object output to verify complex details rendering"
  value = {
    cluster = {
      name     = "test-cluster"
      location = "us-east1-b"
      node_pools = {
        default = {
          machine_type   = "e2-standard-2"
          min_node_count = 1
          max_node_count = 3
        }
      }
    }
  }
}
