# Google Storage Bucket Module (osinfra.io)
# https://github.com/osinfra-io/pt-arche-google-storage-bucket

# Comment or un-comment out the following two resources to test the apply job.

module "bucket" {
  source = "github.com/osinfra-io/pt-arche-google-storage-bucket?ref=4767539fa395255ecb9c814c010938ef2878fc6e" # v0.3.1

  force_destroy = true
  labels        = module.helpers.labels
  location      = "US"
  name          = "test-${random_id.test.hex}-${module.helpers.env}"
  project       = var.project
}

# Random ID Resource
# https://search.opentofu.org/provider/hashicorp/random/latest/docs/resources/id

resource "random_id" "test" {
  byte_length = 4
}
