terraform {

  # State and Plan Encryption
  # https://opentofu.org/docs/language/state/encryption

  # The default key provider, method, and enforced plan/state encryption are supplied by the
  # called workflow through TF_ENCRYPTION and merged with this configuration.

  encryption {
    key_provider "gcp_kms" "logos" {
      encrypted_metadata_alias = "key_provider.gcp_kms.default"
      key_length               = 32
      kms_encryption_key       = "projects/pt-corpus-tf16-prod/locations/us/keyRings/state-encryption/cryptoKeys/default"
    }

    method "aes_gcm" "logos" {
      keys = key_provider.gcp_kms.logos
    }

    remote_state_data_sources {
      default {
        method = method.aes_gcm.logos
      }
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
