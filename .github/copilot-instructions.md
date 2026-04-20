# pt-techne-opentofu-workflows

Reusable GitHub Actions called workflows for OpenTofu deployments across all platform repos. Handles OIDC authentication, state backend configuration, plan/apply job summaries, and Workload Identity Federation.

## README Badges

The platform README badge convention says to add an "OpenTofu Tests" badge whenever a `test.yml` workflow exists. This repo intentionally **does not** include that badge: `test.yml` here is a reusable called workflow consumed by other repos (the `tofu test` runner), not a local CI test of this repo. Its run history reflects callers, not this repo, so the badge would be misleading.

