import json
from pathlib import Path
import shutil
import tempfile
import unittest

from src.rtl_generator import make_prompt
from src.simulator import verify

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/fifo_good.sv"
TB = ROOT / "examples/fifo/tb.sv"


@unittest.skipUnless(shutil.which("iverilog") and shutil.which("vvp"), "Icarus required")
class FIFOTests(unittest.TestCase):
    def test_fixture(self):
        result = verify(FIXTURE, TB)
        self.assertTrue(result["functional_pass"], result)
        self.assertIn("Coverage:", result["simulation_stdout"])

    def test_faulty_fifos_are_rejected(self):
        original = FIXTURE.read_text()
        variants = {
            "reject_full_simultaneous_write": original.replace("(!full || pop)", "!full"),
            "read_when_empty": original.replace("rd_en && !empty", "rd_en"),
            "write_when_full": original.replace("wr_en && (!full || pop)", "wr_en"),
            "incorrect_full_flag": original.replace("count == 16", "count == 15"),
            "wrong_read_address": original.replace("memory[head]", "memory[tail]"),
            "bad_pointer_wrap": original.replace("head + 1'b1", "(head == 14 ? 0 : head + 1'b1)"),
            "count_on_simultaneous": original.replace("default: count <= count;", "2'b11: count <= count + 1'b1; default: count <= count;"),
            "asynchronous_reset": original.replace("@(posedge clk)", "@(posedge clk or posedge reset)"),
            "reset_priority": original.replace("if (reset)", "if (reset && !wr_en && !rd_en)"),
            "registered_data_hold": original.replace("if (pop) begin", "data_out <= 0;\n            if (pop) begin"),
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutant.sv"
            for name, rtl in variants.items():
                with self.subTest(name=name):
                    path.write_text(rtl)
                    result = verify(path, TB)
                    self.assertTrue(result["compile_success"], result)
                    self.assertFalse(result["functional_pass"], result)
                    self.assertIn("TEST_FAIL", result["simulation_stdout"])

    def test_testbench_withheld(self):
        spec = (ROOT / "examples/fifo/spec.txt").read_text()
        prompt = make_prompt(spec)
        self.assertEqual(prompt[1]["content"], spec)
        self.assertNotIn("TEST_PASS", json.dumps(prompt))
        self.assertNotIn("598cafe1", json.dumps(prompt))
