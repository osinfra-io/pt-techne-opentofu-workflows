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


def workflow_script(step_name):
    workflow = WORKFLOW_PATH.read_text()
    step_marker = f"      - name: {step_name}\n"
    step_start = workflow.index(step_marker)
    next_step = workflow.find("\n      - name:", step_start + len(step_marker))
    step = workflow[step_start:next_step if next_step >= 0 else len(workflow)]
    run_marker = "        run: |\n"
    script = step.split(run_marker, 1)[1]
    return textwrap.dedent(script)


class OpenBaoWorkflowAuthTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp_path = pathlib.Path(self.temp_dir.name)
        bin_dir = self.temp_path / "bin"
        bin_dir.mkdir()

        curl = bin_dir / "curl"
        curl.write_text(
            """#!/usr/bin/env python3
import json
import os
import sys

args = sys.argv[1:]
with open(os.environ["CURL_LOG"], "a") as stream:
    stream.write(json.dumps(args) + "\\n")
if "--get" in args:
    print(json.dumps({"value": "test-jwt"}))
else:
    payload = json.loads(args[args.index("--data") + 1])
    with open(os.environ["CURL_LOGIN"], "w") as stream:
        json.dump(payload, stream)
    print(json.dumps({"auth": {"client_token": "test-client-token"}}))
"""
        )
        curl.chmod(0o755)

        tofu = bin_dir / "tofu"
        tofu.write_text(
            """#!/usr/bin/env python3
import json
import os

with open(os.environ["TOFU_ENV"], "w") as stream:
    json.dump(
        {"address": os.environ.get("VAULT_ADDR"), "token": os.environ.get("VAULT_TOKEN")},
        stream,
    )
"""
        )
        tofu.chmod(0o755)

        self.env = os.environ.copy()
        self.env.update(
            {
                "PATH": f"{bin_dir}:{self.env['PATH']}",
                "ACTIONS_ID_TOKEN_REQUEST_URL": "https://actions.example/token",
                "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "request-token",
                "OPENBAO_ADDRESS": "",
                "OPENBAO_JWT_AUTH_MOUNT": "",
                "OPENBAO_JWT_AUDIENCE": "",
                "OPENBAO_JWT_PLAN_ROLE": "",
                "OPENBAO_JWT_APPLY_ROLE": "",
                "OPENTOFU_PLAN_ARGS": "",
                "OPENTOFU_PLAN_SECRET_ARGS": "",
                "CURL_LOG": str(self.temp_path / "curl.log"),
                "CURL_LOGIN": str(self.temp_path / "curl-login.json"),
                "TOFU_ENV": str(self.temp_path / "tofu-env.json"),
                "GITHUB_OUTPUT": str(self.temp_path / "github-output"),
                "RUNNER_TEMP": str(self.temp_path),
            }
        )
        pathlib.Path(self.env["GITHUB_OUTPUT"]).touch()

    def run_step(self, step_name, values=None):
        self.env.update(values or {})
        return subprocess.run(
            ["bash", "-euo", "pipefail", "-c", workflow_script(step_name)],
            cwd=REPOSITORY_ROOT,
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )

    def curl_calls(self):
        log = pathlib.Path(self.env["CURL_LOG"])
        if not log.exists():
            return []
        return [json.loads(line) for line in log.read_text().splitlines()]

    def assert_token_not_leaked(self, result):
        output = pathlib.Path(self.env["GITHUB_OUTPUT"]).read_text()
        self.assertNotIn("test-jwt", output)
        self.assertNotIn("test-client-token", output)
        for line in result.stdout.splitlines():
            if not line.startswith("::add-mask::"):
                self.assertNotIn("test-jwt", line)
                self.assertNotIn("test-client-token", line)
        self.assertRegex(result.stdout, re.compile(r"::add-mask::test-jwt"))
        self.assertRegex(result.stdout, re.compile(r"::add-mask::test-client-token"))

    def test_plan_without_openbao_inputs_keeps_existing_behavior(self):
        result = self.run_step("OpenTofu plan")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.curl_calls(), [])
        tofu_env = json.loads(pathlib.Path(self.env["TOFU_ENV"]).read_text())
        self.assertEqual(tofu_env, {"address": None, "token": None})

    def test_plan_exchanges_jwt_using_read_only_plan_role(self):
        result = self.run_step(
            "OpenTofu plan",
            {
                "OPENBAO_ADDRESS": "https://bao.example",
                "OPENBAO_JWT_AUTH_MOUNT": "jwt",
                "OPENBAO_JWT_AUDIENCE": "https://bao.example",
                "OPENBAO_JWT_PLAN_ROLE": "pneuma-plan",
                "OPENBAO_JWT_APPLY_ROLE": "pneuma-apply",
            },
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.curl_calls()), 2)
        payload = json.loads(pathlib.Path(self.env["CURL_LOGIN"]).read_text())
        self.assertEqual(payload["role"], "pneuma-plan")
        tofu_env = json.loads(pathlib.Path(self.env["TOFU_ENV"]).read_text())
        self.assertEqual(
            tofu_env, {"address": "https://bao.example", "token": "test-client-token"}
        )
        self.assert_token_not_leaked(result)

    def test_apply_exchanges_jwt_using_protected_apply_role(self):
        result = self.run_step(
            "OpenTofu apply",
            {
                "OPENBAO_ADDRESS": "https://bao.example",
                "OPENBAO_JWT_AUTH_MOUNT": "jwt",
                "OPENBAO_JWT_AUDIENCE": "https://bao.example",
                "OPENBAO_JWT_PLAN_ROLE": "pneuma-plan",
                "OPENBAO_JWT_APPLY_ROLE": "pneuma-apply",
            },
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.curl_calls()), 2)
        payload = json.loads(pathlib.Path(self.env["CURL_LOGIN"]).read_text())
        self.assertEqual(payload["role"], "pneuma-apply")
        tofu_env = json.loads(pathlib.Path(self.env["TOFU_ENV"]).read_text())
        self.assertEqual(
            tofu_env, {"address": "https://bao.example", "token": "test-client-token"}
        )
        self.assert_token_not_leaked(result)

    def test_partial_openbao_configuration_fails_before_token_request(self):
        result = self.run_step(
            "OpenTofu plan", {"OPENBAO_ADDRESS": "https://bao.example"}
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.curl_calls(), [])
        self.assertFalse(pathlib.Path(self.env["TOFU_ENV"]).exists())


if __name__ == "__main__":
    unittest.main()
