# OpenTofu Google Cloud Platform Called Workflows

[![Dependabot](https://img.shields.io/github/actions/workflow/status/osinfra-io/pt-techne-opentofu-workflows/local-dependabot.yml?style=for-the-badge&logo=github&color=2088FF&label=Dependabot)](https://github.com/osinfra-io/pt-techne-opentofu-workflows/actions/workflows/local-dependabot.yml)

Reusable GitHub Actions workflows for OpenTofu validation and environment deployments on Google Cloud. Consumers pin this repository to a full commit SHA and supply their environment, workspace, state encryption, service account, and Workload Identity Federation settings.

## Caller contract

- `plan-and-apply.yml` authenticates to Google Cloud with OIDC, initializes encrypted state, selects the workspace, plans, and applies behind GitHub environment approval.
- `test.yml` runs module validation and tests without deploying infrastructure.
- Callers must grant the permissions required for OIDC and repository contents and provide the documented workflow inputs and inherited secrets.

### Features

- [Approve or reject jobs awaiting review](https://docs.github.com/en/actions/managing-workflow-runs/reviewing-deployments)
- [Dependencies cache](https://docs.github.com/en/actions/advanced-guides/caching-dependencies-to-speed-up-workflows)
- [Job summaries](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#adding-a-job-summary)
- [OpenID connect in Google Cloud Platform](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-google-cloud-platform)
- [OpenTofu state and plan encryption](https://opentofu.org/docs/language/state/encryption)

### Workflows

- [plan-and-apply.yml](.github/workflows/plan-and-apply.yml)
- [test.yml](.github/workflows/test.yml)

### Usage

You can check the [.github/workflows](.github/workflows/) directory for example configurations:

- [sandbox.yml](.github/workflows/sandbox.yml)
- [non-production.yml](.github/workflows/non-production.yml)
- [production.yml](.github/workflows/production.yml)
- [module-test.yml](.github/workflows/module-test.yml)

These set up the system for the testing process by providing all the necessary initial code, thus creating good examples to base your configuration on.

Since we use early variable evaluation for backend and provider configuration, consumers must ensure that the following variables are set in each respective `variables.tofu` file:

```hcl
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
```
