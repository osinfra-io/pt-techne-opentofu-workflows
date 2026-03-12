# Google Storage Bucket Module (osinfra.io)
# https://github.com/osinfra-io/opentofu-google-storage-bucket

# Comment or un-comment out the following two resources to test the apply job.

module "bucket" {
  source = "github.com/osinfra-io/opentofu-google-storage-bucket?ref=642c3eb45623e0e619dcc3c80c98ef804da7c153" # v0.2.1

  force_destroy = true
  labels        = module.helpers.labels
  location      = "US"
  name          = "test-${random_id.test.hex}-${module.helpers.env}"
  project       = "pt-techne-testing-tf0d-sb"
}

resource "random_id" "test" {
  byte_length = 4
}
