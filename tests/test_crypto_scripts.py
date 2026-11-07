"""Tests for ctf-crypto exploit automation scripts."""

import importlib.util
import unittest
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parent.parent
CRYPTO_SCRIPTS_DIR = REPO_ROOT / "skills" / "ctf-crypto" / "scripts"


def _load_script(script_name: str) -> ModuleType:
    path = CRYPTO_SCRIPTS_DIR / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(script_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestCryptoScriptImports(unittest.TestCase):
    def test_scripts_exist(self):
        self.assertTrue(
            CRYPTO_SCRIPTS_DIR.is_dir(), "ctf-crypto/scripts directory missing"
        )
        self.assertTrue((CRYPTO_SCRIPTS_DIR / "padding_oracle_suite.py").is_file())
        self.assertTrue((CRYPTO_SCRIPTS_DIR / "rsa_attack_suite.py").is_file())

    def test_padding_oracle_suite(self):
        mod = _load_script("padding_oracle_suite")

        for attr in (
            "get_intermediate_block",
            "decrypt_block",
            "decrypt_ciphertext",
            "forge_ciphertext",
            "MockPaddingOracle",
            "bleichenbacher_attack",
            "MockBleichenbacherOracle",
        ):
            self.assertTrue(hasattr(mod, attr), f"Missing {attr}")

        # 1. Test CBC PKCS#7 padding oracle decryption
        oracle = mod.MockPaddingOracle(key=b"16byteSecretKey!", block_size=16)
        plaintext = b"CTF{padding_oracle_success_flag}"
        iv, ct = oracle.encrypt(plaintext)
        decrypted = mod.decrypt_ciphertext(
            oracle.is_padding_valid, iv + ct, block_size=16
        )
        self.assertEqual(decrypted, plaintext)

        # 2. Test CBC PKCS#7 arbitrary ciphertext forgery
        target_msg = b"user=admin;role=root"
        forged = mod.forge_ciphertext(
            oracle.is_padding_valid, target_msg, block_size=16
        )
        recovered_forged = mod.decrypt_ciphertext(
            oracle.is_padding_valid, forged, block_size=16
        )
        self.assertEqual(recovered_forged, target_msg)

        # 3. Test RSA PKCS#1 v1.5 Bleichenbacher padding oracle attack
        rsa_oracle = mod.MockBleichenbacherOracle()
        m_expected = rsa_oracle.pad_message(0x4242)
        c_valid = rsa_oracle.encrypt(m_expected)
        m_recovered = mod.bleichenbacher_attack(
            rsa_oracle.n,
            rsa_oracle.e,
            c_valid,
            rsa_oracle.is_pkcs1_conforming,
        )
        self.assertEqual(m_recovered, m_expected)

    def test_rsa_attack_suite(self):
        mod = _load_script("rsa_attack_suite")

        for attr in (
            "wiener_attack",
            "fermat_factorization",
            "common_factor_attack",
            "common_modulus_attack",
            "hastad_broadcast_attack",
        ):
            self.assertTrue(hasattr(mod, attr), f"Missing {attr}")

        # 1. Test Fermat factorization
        p = 1000000007
        q = 1000000009
        n = p * q
        res = mod.fermat_factorization(n)
        self.assertIsNotNone(res)
        f_p, f_q = res
        self.assertEqual(f_p * f_q, n)

        # 2. Test Wiener attack
        phi_w = (p - 1) * (q - 1)
        d_w = 1009
        e_w = pow(d_w, -1, phi_w)
        self.assertEqual(mod.wiener_attack(n, e_w), d_w)

        # 3. Test Common Factor attack
        q2_cf = 1000000021
        cf_res = mod.common_factor_attack([p * q, p * q2_cf])
        self.assertEqual(len(cf_res), 2)
        self.assertEqual(cf_res[0][1], p)

        # 4. Test Common Modulus & Hastad Broadcast
        msg = 13374242
        c1 = pow(msg, 17, n)
        c2 = pow(msg, 19, n)
        self.assertEqual(mod.common_modulus_attack(c1, c2, 17, 19, n), msg)

        mods_h = [1000000007, 1000000009, 1000000021]
        cts_h = [pow(msg, 3, m) for m in mods_h]
        self.assertEqual(mod.hastad_broadcast_attack(cts_h, mods_h, e=3), msg)


if __name__ == "__main__":
    unittest.main()
