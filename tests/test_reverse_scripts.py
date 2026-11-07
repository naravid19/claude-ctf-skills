"""Tests for ctf-reverse exploit automation scripts."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REVERSE_SCRIPTS_DIR = REPO_ROOT / "skills" / "ctf-reverse" / "scripts"


class TestReverseScriptImports(unittest.TestCase):
    def test_scripts_exist(self):
        self.assertTrue(
            REVERSE_SCRIPTS_DIR.is_dir(), "ctf-reverse/scripts directory missing"
        )
        self.assertTrue((REVERSE_SCRIPTS_DIR / "unicorn_trace_emu.py").is_file())

    def test_unicorn_trace_emu_import(self):
        import importlib.util

        path = REVERSE_SCRIPTS_DIR / "unicorn_trace_emu.py"
        spec = importlib.util.spec_from_file_location("unicorn_trace_emu", path)
        self.assertIsNotNone(spec and spec.loader)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        self.assertTrue(hasattr(mod, "emulate_x86_shellcode"))
        self.assertTrue(hasattr(mod, "run_mock_trace"))
        self.assertTrue(hasattr(mod, "ARCH_CONFIG"))
        self.assertTrue(hasattr(mod, "HAS_UNICORN"))

        res = mod.run_mock_trace()
        self.assertTrue(res.get("success", False))


if __name__ == "__main__":
    unittest.main()
