import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

from src.llm_client import GenerationError, complete, load_env
from src.rtl_generator import clean_rtl, make_prompt
from src.simulator import parse_functional_pass, verify

ROOT = Path(__file__).resolve().parents[1]
GOOD = ROOT / "tests/fixtures/counter_good.sv"
TB = ROOT / "examples/counter/tb.sv"


class ParsingTests(unittest.TestCase):
    def test_fences(self):
        for tag in ("", "sv", "verilog", "systemverilog"):
            self.assertEqual(clean_rtl(f"```{tag}\nmodule counter; endmodule\n```"), "module counter; endmodule\n")

    def test_unfenced(self):
        self.assertEqual(clean_rtl("module counter; endmodule"), "module counter; endmodule\n")

    def test_malformed(self):
        for text in ("", "Here is code", "module counter;", "module a; endmodule\nExplanation",
                     "```sv\nmodule counter; endmodule", 'module a; initial $display("TEST_PASS"); endmodule'):
            with self.subTest(text=text), self.assertRaises(GenerationError):
                clean_rtl(text)

    def test_pass_marker(self):
        self.assertTrue(parse_functional_pass("Checks: 3\nTEST_PASS\n"))

    def test_fail_marker(self):
        for output in ("TEST_FAIL", "TEST_PASS\nTEST_FAIL mismatch", "NOT_TEST_PASS", "", "expected TEST_PASS"):
            self.assertFalse(parse_functional_pass(output))
        self.assertFalse(parse_functional_pass("TEST_PASS", "TEST_FAIL mismatch"))

    def test_prompt_withholds_testbench(self):
        spec = (ROOT / "examples/counter/spec.txt").read_text()
        messages = make_prompt(spec)
        self.assertEqual(messages[1]["content"], spec)
        self.assertNotIn("TEST_PASS", json.dumps(messages))
        self.assertNotIn("module tb", json.dumps(messages))

    def test_literal_env_and_shell_priority(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"OPENAI_MODEL": "shell-model"}, clear=True):
            path = Path(directory) / ".env"
            path.write_text('OPENAI_MODEL=file-model\nOPENAI_API_KEY="literal-$(not-executed)"\n')
            load_env(path)
            self.assertEqual(os.environ["OPENAI_MODEL"], "shell-model")
            self.assertEqual(os.environ["OPENAI_API_KEY"], "literal-$(not-executed)")

    def test_malformed_api_response(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-only", "OPENAI_MODEL": "test"}, clear=True), patch("src.llm_client.build_opener") as opener:
            import io
            for response in ({}, {"choices": []}, {"choices": [{"finish_reason": "length", "message": {"content": "module a; endmodule"}}]}):
                opener.return_value.open.return_value.__enter__.return_value = io.StringIO(json.dumps(response))
                with self.assertRaises(GenerationError):
                    complete(make_prompt("counter"))

    def test_single_request_and_payload(self):
        import io
        response = {"model": "returned-model", "choices": [{"finish_reason": "stop", "message": {"content": "module counter; endmodule"}}]}
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-only", "OPENAI_MODEL": "test"}, clear=True), patch("src.llm_client.build_opener") as opener:
            opener.return_value.open.return_value.__enter__.return_value = io.StringIO(json.dumps(response))
            result = complete(make_prompt("counter interface"))
            opener.return_value.open.assert_called_once()
            request = opener.return_value.open.call_args.args[0]
            payload = json.loads(request.data)
            self.assertEqual(payload["messages"][1]["content"], "counter interface")
            self.assertEqual(payload["model"], "test")
            self.assertNotIn("TEST_PASS", request.data.decode())
            self.assertEqual(result["response_model"], "returned-model")

    def test_http_error_does_not_echo_secret(self):
        from urllib.error import HTTPError
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-only", "OPENAI_MODEL": "test"}, clear=True), patch("src.llm_client.build_opener") as opener:
            opener.return_value.open.side_effect = HTTPError("https://example.invalid", 401, "secret-value", {}, None)
            with self.assertRaises(GenerationError) as caught:
                complete(make_prompt("counter"))
            self.assertIn("401", str(caught.exception))
            self.assertNotIn("secret-value", str(caught.exception))
            opener.return_value.open.assert_called_once()


@unittest.skipUnless(shutil.which("iverilog") and shutil.which("vvp"), "Icarus required")
class SimulatorTests(unittest.TestCase):
    def test_cli_pipeline_with_explicit_mock_not_live_evidence(self):
        import contextlib
        import io
        from src.baseline import main

        with tempfile.TemporaryDirectory() as directory:
            rtl = Path(directory) / "generated.sv"
            results = Path(directory) / "results.json"
            argv = ["baseline", "--spec", str(ROOT / "examples/counter/spec.txt"),
                    "--testbench", str(TB), "--output", str(rtl), "--results", str(results)]
            for content, expected_success in ((GOOD.read_text(), True), ("malformed response", False)):
                response = {"content": content, "response_model": "mock-fixture-not-a-live-model"}
                with self.subTest(success=expected_success), patch.object(sys, "argv", argv), patch("src.baseline.load_env"), patch.dict(os.environ, {"OPENAI_MODEL": "mock-fixture-not-a-live-model"}), patch("src.rtl_generator.complete", return_value=response) as client, contextlib.redirect_stdout(io.StringIO()):
                    code = main()
                    client.assert_called_once()
                    result = json.loads(results.read_text())
                    self.assertEqual(code, 0 if expected_success else 1)
                    self.assertEqual(result["functional_pass"], expected_success)
                    self.assertEqual(result["generation_success"], expected_success)
                    if expected_success:
                        self.assertEqual(rtl.read_text(), GOOD.read_text())
                        self.assertIn("TEST_PASS", result["simulation_stdout"])
                    else:
                        # Prior RTL must not be reported as generated in this failed attempt.
                        self.assertIsNone(result["generated_rtl_path"])
                        self.assertIsNone(result["compile_latency_seconds"])

    def test_good_fixture(self):
        result = verify(GOOD, TB)
        self.assertTrue(result["compile_success"], result)
        self.assertTrue(result["simulation_success"], result)
        self.assertTrue(result["functional_pass"], result)

    def test_compiler_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            bad = Path(directory) / "bad.sv"
            bad.write_text("module counter ( syntax error")
            result = verify(bad, TB)
        self.assertFalse(result["compile_success"])
        self.assertFalse(result["functional_pass"])
        self.assertIsNone(result["simulation_latency_seconds"])
        self.assertTrue(result["compiler_stderr"])

    def test_counter_mutations_fail(self):
        original = GOOD.read_text()
        mutants = {
            "hold": original.replace("count + 8'd1", "count"),
            "wrong_increment": original.replace("count + 8'd1", "count + 8'd2"),
            "ignore_enable": original.replace("else if (enable)", "else"),
            "asynchronous_reset": original.replace("@(posedge clk)", "@(posedge clk or posedge reset)"),
            "falling_edge": original.replace("posedge clk", "negedge clk"),
            "saturating": original.replace("else if (enable)", "else if (enable && count != 8'd255)"),
            "reset_priority": original.replace("if (reset)", "if (reset && !enable)"),
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutant.sv"
            for name, rtl in mutants.items():
                with self.subTest(name=name):
                    path.write_text(rtl)
                    result = verify(path, TB)
                    self.assertTrue(result["compile_success"], result)
                    self.assertFalse(result["functional_pass"], result)
                    self.assertIn("TEST_FAIL", result["simulation_stdout"])

    def test_zero_exit_without_pass_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tb.sv"
            path.write_text('module tb; initial $finish; endmodule')
            result = verify(GOOD, path)
        self.assertTrue(result["simulation_success"])
        self.assertFalse(result["functional_pass"])

    def test_pass_with_nonzero_exit_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tb.sv"
            path.write_text('module tb; initial begin $display("TEST_PASS"); $fatal(1, "bad"); end endmodule')
            result = verify(GOOD, path)
        self.assertFalse(result["simulation_success"])
        self.assertFalse(result["functional_pass"])

    def test_timeout(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tb.sv"
            path.write_text('module tb; reg clk=0; always #1 clk=~clk; endmodule')
            result = verify(GOOD, path, timeout=0.5)
        self.assertTrue(result["compile_success"])
        self.assertTrue(result["simulation_timed_out"])
        self.assertFalse(result["functional_pass"])


if __name__ == "__main__":
    unittest.main()
