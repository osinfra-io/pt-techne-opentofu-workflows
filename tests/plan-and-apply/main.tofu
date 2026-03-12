# Google Project Module (osinfra.io)
# https://github.com/osinfra-io/opentofu-google-project

module "project" {
  source = "github.com/osinfra-io/opentofu-google-project?ref=912e5f1e334e46f8048109e79ed4f30b32c036f1" # v0.6.0

  billing_account                 = var.project_billing_account
  cis_2_2_logging_sink_project_id = var.project_cis_2_2_logging_sink_project_id
  description                     = "test"
  folder_id                       = module.helpers.environment_folder_id
  labels                          = module.helpers.labels
  prefix                          = module.helpers.team
}

# Google Storage Bucket Module (osinfra.io)
# https://github.com/osinfra-io/opentofu-google-storage-bucket

# Comment or un-comment out the following two resources to test the apply job.

# module "bucket" {
#   source = "github.com/osinfra-io/opentofu-google-storage-bucket?ref=642c3eb45623e0e619dcc3c80c98ef804da7c153" # v0.2.1

#   force_destroy = true
#   labels        = module.helpers.labels
#   location      = "US"
#   name          = "test-${random_id.test.hex}-${module.helpers.env}"
#   project       = module.project.id
# }

# resource "random_id" "test" {
#   byte_length = 4
# }
