# OpenTofu Google Cloud Platform Called Workflows

[![Dependabot](https://img.shields.io/github/actions/workflow/status/osinfra-io/pt-techne-opentofu-workflows/local-dependabot.yml?style=for-the-badge&logo=github&color=2088FF&label=Dependabot)](https://github.com/osinfra-io/pt-techne-opentofu-workflows/actions/workflows/local-dependabot.yml)

Reusable GitHub Actions workflows for OpenTofu validation and environment deployments on Google Cloud. Consumers pin this repository to a full commit SHA and supply their environment, workspace, state encryption, service account, and Workload Identity Federation settings.

## Caller contract

- `plan-and-apply.yml` authenticates to Google Cloud with OIDC, initializes encrypted state, selects the workspace, plans, and applies. GitHub pauses the job for approval only when the selected environment has a required-reviewer protection rule.
- `test.yml` runs module validation and tests without deploying infrastructure.
- Callers must grant the permissions required by each workflow: `plan-and-apply.yml` requires `id-token: write` and repository contents access, while `test.yml` requires `contents: read`. Provide inherited secrets only when using the corresponding optional secret inputs.

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

State encryption and the backend are configured by the called workflow, so consumers don't declare any `state_*` variables:

- `TF_ENCRYPTION` supplies the default `gcp_kms` key provider, the `aes_gcm` method, and enforced plan and state encryption. It is merged with any `encryption {}` block in the root module, which can reference `method.aes_gcm.default` (for example in `remote_state_data_sources`).
- `GOOGLE_KMS_ENCRYPTION_KEY` supplies the GCS backend's KMS key.
- `tofu init` receives the bucket and prefix through `-backend-config`, so the root module only declares an empty backend:

```hcl
terraform {
  backend "gcs" {}
}
```
