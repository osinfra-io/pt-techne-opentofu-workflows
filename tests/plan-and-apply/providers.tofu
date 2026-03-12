terraform {

  # State and Plan Encryption
  # https://opentofu.org/docs/language/state/encryption

  # The commented out sections below demonstrate how to configure
  # fallback encryption methods for state and plan files for bootstrapping.

  encryption {
    # method "unencrypted" "migrate" {}

    key_provider "gcp_kms" "default" {
      key_length         = 32
      kms_encryption_key = var.state_kms_encryption_key
    }

    key_provider "gcp_kms" "logos" {
      encrypted_metadata_alias = "key_provider.gcp_kms.default"
      key_length               = 32
      kms_encryption_key       = "projects/pt-corpus-tf16-prod/locations/us/keyRings/state-encryption/cryptoKeys/default"
    }

    method "aes_gcm" "default" {
      keys = key_provider.gcp_kms.default
    }

    method "aes_gcm" "logos" {
      keys = key_provider.gcp_kms.logos
    }

    plan {
      enforced = true
      method   = method.aes_gcm.default

      # fallback {
      #   method = method.unencrypted.migrate
      # }
    }

    remote_state_data_sources {
      default {
        method = method.aes_gcm.logos
      }
    }

    state {
      enforced = true
      method   = method.aes_gcm.default

      # fallback {
      #   method = method.unencrypted.migrate
      # }
    }
  }

  # Requiring Providers
  # https://opentofu.org/docs/language/providers/requirements#requiring-providers

  required_providers {
    # Google Cloud Platform Provider
    # https://search.opentofu.org/provider/hashicorp/google/latest/docs

    google = {
      source = "hashicorp/google"
    }

    # Random Provider
    # https://opentofu.org/docs/providers/random/index.html

    random = {
      source = "hashicorp/random"
    }
  }
}
