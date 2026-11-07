"""Tests for ctf-reverse exploit automation scripts."""

import importlib.util
import unittest
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parent.parent
REVERSE_SCRIPTS_DIR = REPO_ROOT / "skills" / "ctf-reverse" / "scripts"


def _load_script(script_name: str) -> ModuleType:
    path = REVERSE_SCRIPTS_DIR / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(script_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestReverseScriptImports(unittest.TestCase):
    def test_scripts_exist(self):
        self.assertTrue(
            REVERSE_SCRIPTS_DIR.is_dir(), "ctf-reverse/scripts directory missing"
        )
        self.assertTrue((REVERSE_SCRIPTS_DIR / "unicorn_trace_emu.py").is_file())

    def test_unicorn_trace_emu_import(self):
        mod = _load_script("unicorn_trace_emu")

        for attr in (
            "emulate_x86_shellcode",
            "run_mock_trace",
            "ARCH_CONFIG",
            "HAS_UNICORN",
        ):
            self.assertTrue(hasattr(mod, attr), f"Missing {attr}")

        res = mod.run_mock_trace()
        self.assertTrue(res.get("success", False))


if __name__ == "__main__":
    unittest.main()
