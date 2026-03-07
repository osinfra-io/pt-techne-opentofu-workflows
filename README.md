# <img align="left" width="45" height="45" src="https://user-images.githubusercontent.com/1610100/201473670-e0e6bdeb-742f-4be1-a47a-3506309620a3.png"> OpenTofu Google Cloud Platform Called Workflows

[![Dependabot](https://img.shields.io/github/actions/workflow/status/osinfra-io/pt-techne-github-opentofu-gcp-called-workflows/local-dependabot.yml?style=for-the-badge&logo=github&color=2088FF&label=Dependabot)](https://github.com/osinfra-io/pt-techne-github-opentofu-gcp-called-workflows/actions/workflows/local-dependabot.yml)

Reusing workflows avoids duplication. This makes workflows easier to maintain and allows you to create new workflows
more quickly by building on the work of others, just as you do with actions.

Workflow reuse also promotes best practices by helping you use well-designed, tested, and proven effective workflows. Your organization can build up a library of reusable workflows that can
be centrally maintained.

## Reusing Workflows

Rather than copying and pasting from one workflow to another, you can make workflows [reusable](https://docs.github.com/en/actions/learn-github-actions/reusing-workflows). You and anyone with access to the reusable workflow can then call the reusable workflow from another workflow.

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
