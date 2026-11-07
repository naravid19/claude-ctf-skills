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

        self.assertTrue(hasattr(mod, "get_intermediate_block"))
        self.assertTrue(hasattr(mod, "decrypt_block"))
        self.assertTrue(hasattr(mod, "decrypt_ciphertext"))
        self.assertTrue(hasattr(mod, "forge_ciphertext"))
        self.assertTrue(hasattr(mod, "MockPaddingOracle"))

        # Test self-contained mock attack
        oracle = mod.MockPaddingOracle(key=b"16byteSecretKey!", block_size=16)
        plaintext = b"CTF{padding_oracle_success_flag}"
        iv, ct = oracle.encrypt(plaintext)
        decrypted = mod.decrypt_ciphertext(
            oracle.is_padding_valid, iv + ct, block_size=16
        )
        self.assertEqual(decrypted, plaintext)

        # Test ciphertext forgery
        target_msg = b"user=admin;role=root"
        forged = mod.forge_ciphertext(
            oracle.is_padding_valid, target_msg, block_size=16
        )
        recovered_forged = mod.decrypt_ciphertext(
            oracle.is_padding_valid, forged, block_size=16
        )
        self.assertEqual(recovered_forged, target_msg)

    def test_rsa_attack_suite(self):
        import importlib.util

        path = CRYPTO_SCRIPTS_DIR / "rsa_attack_suite.py"
        spec = importlib.util.spec_from_file_location("rsa_attack_suite", path)
        self.assertIsNotNone(spec and spec.loader)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        self.assertTrue(hasattr(mod, "wiener_attack"))
        self.assertTrue(hasattr(mod, "fermat_factorization"))
        self.assertTrue(hasattr(mod, "common_factor_attack"))
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

        # Test Wiener attack
        p_w = 1000000007
        q_w = 1000000009
        n_w = p_w * q_w
        phi_w = (p_w - 1) * (q_w - 1)
        d_w = 1009
        e_w = pow(d_w, -1, phi_w)
        self.assertEqual(mod.wiener_attack(n_w, e_w), d_w)

        # Test Common Factor attack
        p_cf = 1000000007
        q1_cf = 1000000009
        q2_cf = 1000000021
        cf_res = mod.common_factor_attack([p_cf * q1_cf, p_cf * q2_cf])
        self.assertEqual(len(cf_res), 2)
        self.assertEqual(cf_res[0][1], p_cf)


if __name__ == "__main__":
    unittest.main()
