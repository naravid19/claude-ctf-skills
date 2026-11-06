"""Tests for ctf-crypto exploit automation scripts."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CRYPTO_SCRIPTS_DIR = REPO_ROOT / "skills" / "ctf-crypto" / "scripts"


class TestCryptoScriptImports(unittest.TestCase):
    def test_scripts_exist(self):
        self.assertTrue(
            CRYPTO_SCRIPTS_DIR.is_dir(), "ctf-crypto/scripts directory missing"
        )
        self.assertTrue((CRYPTO_SCRIPTS_DIR / "padding_oracle_suite.py").is_file())
        self.assertTrue((CRYPTO_SCRIPTS_DIR / "rsa_attack_suite.py").is_file())

    def test_padding_oracle_suite(self):
        import importlib.util

        path = CRYPTO_SCRIPTS_DIR / "padding_oracle_suite.py"
        spec = importlib.util.spec_from_file_location("padding_oracle_suite", path)
        self.assertIsNotNone(spec and spec.loader)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        self.assertTrue(hasattr(mod, "decrypt_block"))
        self.assertTrue(hasattr(mod, "decrypt_ciphertext"))
        self.assertTrue(hasattr(mod, "MockPaddingOracle"))

        # Test self-contained mock attack
        oracle = mod.MockPaddingOracle(key=b"16byteSecretKey!", block_size=16)
        plaintext = b"CTF{padding_oracle_success_flag}"
        iv, ct = oracle.encrypt(plaintext)
        decrypted = mod.decrypt_ciphertext(
            oracle.is_padding_valid, iv + ct, block_size=16
        )
        self.assertEqual(decrypted, plaintext)

    def test_rsa_attack_suite(self):
        import importlib.util

        path = CRYPTO_SCRIPTS_DIR / "rsa_attack_suite.py"
        spec = importlib.util.spec_from_file_location("rsa_attack_suite", path)
        self.assertIsNotNone(spec and spec.loader)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        self.assertTrue(hasattr(mod, "wiener_attack"))
        self.assertTrue(hasattr(mod, "fermat_factorization"))
        self.assertTrue(hasattr(mod, "common_modulus_attack"))
        self.assertTrue(hasattr(mod, "hastad_broadcast_attack"))

        # Test Fermat factorization
        p = 1000000007
        q = 1000000009
        n = p * q
        res = mod.fermat_factorization(n)
        self.assertIsNotNone(res)
        f_p, f_q = res
        self.assertEqual(f_p * f_q, n)


if __name__ == "__main__":
    unittest.main()
