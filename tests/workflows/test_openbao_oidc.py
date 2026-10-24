import json
import os
import pathlib
import re
import subprocess
import tempfile
import textwrap
import unittest


REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPOSITORY_ROOT / ".github/workflows/plan-and-apply.yml"


def workflow_step(name):
    workflow = WORKFLOW_PATH.read_text()
    marker = f"      - name: {name}\n"
    start = workflow.index(marker)
    end = workflow.find("\n      - name:", start + len(marker))
    return workflow[start:end if end >= 0 else len(workflow)]


class OpenBaoWorkflowAuthTests(unittest.TestCase):
    def test_action_authenticates_each_job_with_its_own_role(self):
        for job in ("plan", "apply"):
            with self.subTest(job=job):
                step = workflow_step(f"Authenticate to OpenBao for {job}")
                self.assertRegex(step, r"uses: hashicorp/vault-action@[a-f0-9]{40} # v")
                for setting in (
                    "if: inputs.openbao_address != ''",
                    "id: openbao",
                    "method: jwt",
                    "url: ${{ inputs.openbao_address }}",
                    "path: ${{ inputs.openbao_jwt_auth_mount }}",
                    "jwtGithubAudience: ${{ inputs.openbao_jwt_audience }}",
                    f"role: ${{{{ inputs.openbao_jwt_{job}_role }}}}",
                    "exportEnv: false",
                    "exportToken: false",
                    "outputToken: true",
                ):
                    self.assertIn(setting, step)
                tofu = workflow_step(f"OpenTofu {job}")
                self.assertIn("VAULT_ADDR: ${{ inputs.openbao_address }}", tofu)
                self.assertIn("VAULT_TOKEN: ${{ steps.openbao.outputs.vault_token }}", tofu)
                self.assertNotIn("curl", tofu)

    def test_optional_inputs_are_validated_before_authentication(self):
        for job in ("plan", "apply"):
            script = textwrap.dedent(
                workflow_step(f"Validate OpenBao inputs for {job}").split("        run: |\n", 1)[1]
            )
            complete = {
                "OPENBAO_ADDRESS": "https://bao.example",
                "OPENBAO_JWT_AUTH_MOUNT": "github-actions",
                "OPENBAO_JWT_AUDIENCE": "pneuma",
                "OPENBAO_JWT_PLAN_ROLE": "plan",
                "OPENBAO_JWT_APPLY_ROLE": "apply",
            }
            for values, success in (
                ({key: "" for key in complete}, True),
                (complete, True),
                ({**complete, "OPENBAO_JWT_PLAN_ROLE": ""}, False),
                ({**complete, "OPENBAO_JWT_AUTH_MOUNT": "nested/path"}, False),
            ):
                with self.subTest(job=job, values=values):
                    result = subprocess.run(
                        ["bash", "-euo", "pipefail", "-c", script],
                        env={**os.environ, **values}, capture_output=True, text=True,
                    )
                    self.assertEqual(result.returncode == 0, success, result.stderr)

    def test_token_is_not_promoted_to_job_outputs_or_environment_files(self):
        workflow = WORKFLOW_PATH.read_text()
        self.assertNotIn("ACTIONS_ID_TOKEN_REQUEST", workflow)
        self.assertNotRegex(workflow, r"(?m)^.*(?:vault_token|VAULT_TOKEN).*GITHUB_ENV")
        self.assertEqual(workflow.count("steps.openbao.outputs.vault_token"), 2)
        for outputs in re.findall(r"    outputs:\n(.*?)(?=\n    \S)", workflow, re.DOTALL):
            self.assertNotIn("vault_token", outputs)

    def test_disabled_authentication_keeps_tofu_plan_and_apply_working(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            tofu = root / "tofu"
            tofu.write_text(
                "#!/usr/bin/env python3\n"
                "import json, os\n"
                "with open(os.environ['TEST_ENV'], 'w') as stream:\n"
                "    json.dump([os.environ['VAULT_ADDR'], os.environ['VAULT_TOKEN']], stream)\n"
            )
            tofu.chmod(0o755)
            for job in ("plan", "apply"):
                script = textwrap.dedent(
                    workflow_step(f"OpenTofu {job}").split("        run: |\n", 1)[1]
                )
                result = subprocess.run(
                    ["bash", "-euo", "pipefail", "-c", script],
                    env={
                        **os.environ, "PATH": f"{root}:{os.environ['PATH']}",
                        "VAULT_ADDR": "", "VAULT_TOKEN": "",
                        "OPENTOFU_PLAN_ARGS": "", "OPENTOFU_PLAN_SECRET_ARGS": "",
                        "RUNNER_TEMP": directory, "GITHUB_OUTPUT": str(root / "output"),
                        "TEST_ENV": str(root / "env"),
                    },
                    capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads((root / "env").read_text()), ["", ""])


if __name__ == "__main__":
    unittest.main()
