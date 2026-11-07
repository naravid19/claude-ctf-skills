#!/usr/bin/env python3
"""Automated CBC PKCS#7 & RSA Bleichenbacher Padding Oracle Attack Suite.

Implements:
1. Vaudenay's CBC PKCS#7 byte-by-byte plaintext decryption and arbitrary
   ciphertext forgery (`get_intermediate_block`, `decrypt_ciphertext`,
   `forge_ciphertext`).
2. Bleichenbacher's adaptive chosen-ciphertext attack against RSA PKCS#1 v1.5
   padding validation oracles (`bleichenbacher_attack`).
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Callable, List, Tuple


def pad(data: bytes, block_size: int = 16) -> bytes:
    """PKCS#7 padding."""
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)


def unpad(data: bytes, block_size: int = 16) -> bytes:
    """Remove PKCS#7 padding, raises ValueError if invalid."""
    if not data or len(data) % block_size != 0:
        raise ValueError("Invalid padded data length")
    pad_len = data[-1]
    if pad_len == 0 or pad_len > block_size:
        raise ValueError("Invalid padding value")
    if data[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Inconsistent padding bytes")
    return data[:-pad_len]


class MockPaddingOracle:
    """Self-contained mock CBC oracle for testing and demonstrations."""

    def __init__(self, key: bytes | None = None, block_size: int = 16):
        self.block_size = block_size
        self.key = key or os.urandom(block_size)

    def _xor(self, a: bytes, b: bytes) -> bytes:
        return bytes(x ^ y for x, y in zip(a, b))

    def _block_cipher_encrypt(self, block: bytes) -> bytes:
        return self._xor(block, self.key)

    def _block_cipher_decrypt(self, block: bytes) -> bytes:
        return self._xor(block, self.key)

    def encrypt(self, plaintext: bytes) -> tuple[bytes, bytes]:
        padded = pad(plaintext, self.block_size)
        iv = os.urandom(self.block_size)
        blocks = [
            padded[i : i + self.block_size]
            for i in range(0, len(padded), self.block_size)
        ]
        ciphertext = b""
        prev = iv
        for b in blocks:
            xored = self._xor(b, prev)
            enc = self._block_cipher_encrypt(xored)
            ciphertext += enc
            prev = enc
        return iv, ciphertext

    def is_padding_valid(self, iv_and_ciphertext: bytes) -> bool:
        if (
            len(iv_and_ciphertext) < self.block_size * 2
            or len(iv_and_ciphertext) % self.block_size != 0
        ):
            return False
        iv = iv_and_ciphertext[: self.block_size]
        ct = iv_and_ciphertext[self.block_size :]
        blocks = [
            ct[i : i + self.block_size] for i in range(0, len(ct), self.block_size)
        ]
        pt = b""
        prev = iv
        for b in blocks:
            dec = self._block_cipher_decrypt(b)
            pt += self._xor(dec, prev)
            prev = b
        try:
            unpad(pt, self.block_size)
            return True
        except ValueError:
            return False


def get_intermediate_block(
    oracle_fn: Callable[[bytes], bool],
    target_block: bytes,
    block_size: int = 16,
) -> bytes:
    """Recover intermediate decryption state D_k(target_block)
    using a padding oracle.
    """
    intermediate = bytearray(block_size)

    for byte_idx in reversed(range(block_size)):
        target_pad_val = block_size - byte_idx
        prefix = bytearray(os.urandom(byte_idx))
        found = False

        for candidate in range(256):
            test_block = bytearray(prefix)
            test_block.append(candidate)

            for known_idx in range(byte_idx + 1, block_size):
                test_block.append(intermediate[known_idx] ^ target_pad_val)

            payload = bytes(test_block) + target_block
            if oracle_fn(payload):
                # Guard against accidental 0x02 0x02 padding when looking for 0x01
                if target_pad_val == 1 and byte_idx > 0:
                    test_block_mod = bytearray(test_block)
                    test_block_mod[byte_idx - 1] ^= 0x01
                    if not oracle_fn(bytes(test_block_mod) + target_block):
                        continue

                inter_val = candidate ^ target_pad_val
                intermediate[byte_idx] = inter_val
                found = True
                break

        if not found:
            raise RuntimeError(f"Oracle failed to find valid byte at index {byte_idx}")

    return bytes(intermediate)


def decrypt_block(
    oracle_fn: Callable[[bytes], bool],
    prev_block: bytes,
    target_block: bytes,
    block_size: int = 16,
) -> bytes:
    """Recover the plaintext of target_block using a 2-block padding oracle test."""
    intermediate = get_intermediate_block(oracle_fn, target_block, block_size)
    return bytes(i ^ p for i, p in zip(intermediate, prev_block))


def forge_ciphertext(
    oracle_fn: Callable[[bytes], bool],
    desired_plaintext: bytes,
    block_size: int = 16,
) -> bytes:
    """Forge arbitrary CBC ciphertext (including IV) that decrypts
    to desired_plaintext.
    """
    padded = pad(desired_plaintext, block_size)
    pt_blocks = [padded[i : i + block_size] for i in range(0, len(padded), block_size)]

    cipher_blocks = [os.urandom(block_size)]
    for pt in reversed(pt_blocks):
        inter = get_intermediate_block(oracle_fn, cipher_blocks[0], block_size)
        prev_ct = bytes(i ^ p for i, p in zip(inter, pt))
        cipher_blocks.insert(0, prev_ct)

    return b"".join(cipher_blocks)


def decrypt_ciphertext(
    oracle_fn: Callable[[bytes], bool],
    iv_and_ciphertext: bytes,
    block_size: int = 16,
) -> bytes:
    """Decrypt arbitrary CBC ciphertext prepended with IV."""
    if (
        len(iv_and_ciphertext) % block_size != 0
        or len(iv_and_ciphertext) < block_size * 2
    ):
        raise ValueError("Ciphertext must include IV and be a multiple of block_size")

    blocks = [
        iv_and_ciphertext[i : i + block_size]
        for i in range(0, len(iv_and_ciphertext), block_size)
    ]
    plaintext = b""

    for i in range(1, len(blocks)):
        prev_b = blocks[i - 1]
        target_b = blocks[i]
        pt_block = decrypt_block(oracle_fn, prev_b, target_b, block_size)
        plaintext += pt_block

    return unpad(plaintext, block_size)


def _ceil_div(a: int, b: int) -> int:
    return (a + b - 1) // b


def _merge_intervals(intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    if not intervals:
        return []
    sorted_iv = sorted(intervals, key=lambda x: x[0])
    merged = [sorted_iv[0]]
    for low, high in sorted_iv[1:]:
        prev_low, prev_high = merged[-1]
        if low <= prev_high + 1:
            merged[-1] = (prev_low, max(prev_high, high))
        else:
            merged.append((low, high))
    return merged


class MockBleichenbacherOracle:
    """Self-contained mock RSA PKCS#1 v1.5 padding oracle (2B <= m < 3B)."""

    def __init__(self, p: int = 65537, q: int = 65539, e: int = 17):
        self.n = p * q
        self.e = e
        phi = (p - 1) * (q - 1)
        self.d = pow(e, -1, phi)
        self.k = (self.n.bit_length() + 7) // 8
        self.B = 1 << (8 * (self.k - 2))

    def pad_message(self, payload_int: int) -> int:
        """Create a PKCS#1 v1.5 conforming integer in [2B, 3B - 1]."""
        return 2 * self.B + (payload_int % self.B)

    def encrypt(self, m: int) -> int:
        return pow(m, self.e, self.n)

    def is_pkcs1_conforming(self, c: int) -> bool:
        m = pow(c, self.d, self.n)
        return 2 * self.B <= m < 3 * self.B


def bleichenbacher_attack(
    n: int,
    e: int,
    c: int,
    oracle_fn: Callable[[int], bool],
    max_iterations: int = 10000,
) -> int:
    """Recover RSA plaintext m via Bleichenbacher's PKCS#1 v1.5 padding oracle."""
    k = (n.bit_length() + 7) // 8
    B = 1 << (8 * (k - 2))

    # Step 1: Blinding (Ensure c0 is PKCS#1 conforming)
    s0 = 1
    c0 = c
    if not oracle_fn(c0):
        s0 = 2
        while True:
            c_cand = (c * pow(s0, e, n)) % n
            if oracle_fn(c_cand):
                c0 = c_cand
                break
            s0 += 1

    intervals: List[Tuple[int, int]] = [(2 * B, 3 * B - 1)]
    s = 0

    for i in range(1, max_iterations + 1):
        # Step 2a: Starting the search
        if i == 1:
            s = _ceil_div(n, 3 * B)
            while not oracle_fn((c0 * pow(s, e, n)) % n):
                s += 1
        # Step 2b: Searching with more than one interval left
        elif len(intervals) > 1:
            s += 1
            while not oracle_fn((c0 * pow(s, e, n)) % n):
                s += 1
        # Step 2c: Searching with one interval left
        else:
            a, b = intervals[0]
            if a == b:
                return (a * pow(s0, -1, n)) % n
            r = _ceil_div(2 * (b * s - 2 * B), n)
            found = False
            while not found:
                s_min = _ceil_div(2 * B + r * n, b)
                s_max = (3 * B - 1 + r * n) // a
                for s_cand in range(s_min, s_max + 1):
                    if oracle_fn((c0 * pow(s_cand, e, n)) % n):
                        s = s_cand
                        found = True
                        break
                r += 1

        # Step 3: Narrowing the set of solutions
        next_intervals: List[Tuple[int, int]] = []
        for a, b in intervals:
            r_min = _ceil_div(a * s - 3 * B + 1, n)
            r_max = (b * s - 2 * B) // n
            for r in range(r_min, r_max + 1):
                low = max(a, _ceil_div(2 * B + r * n, s))
                high = min(b, (3 * B - 1 + r * n) // s)
                if low <= high:
                    next_intervals.append((low, high))

        intervals = _merge_intervals(next_intervals)
        if not intervals:
            raise RuntimeError("Bleichenbacher intervals collapsed to empty set")

        # Step 4: Computing the solution
        if len(intervals) == 1 and intervals[0][0] == intervals[0][1]:
            return (intervals[0][0] * pow(s0, -1, n)) % n

    raise RuntimeError("Bleichenbacher attack exceeded max_iterations")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CBC PKCS#7 & RSA Bleichenbacher Padding Oracle Exploit Suite"
    )
    parser.add_argument(
        "--test", action="store_true", help="Run self-tests against mock oracles"
    )
    parser.add_argument(
        "--mode",
        choices=["all", "cbc", "bleichenbacher"],
        default="all",
        help="Select padding oracle attack mode for self-test",
    )
    args = parser.parse_args()

    if args.test or len(sys.argv) == 1:
        if args.mode in ("all", "cbc"):
            print("[*] Running CBC PKCS#7 Padding Oracle Self-Test...")
            mock = MockPaddingOracle(b"Secret16ByteKey!", block_size=16)
            secret_msg = b"CTF{cbc_padding_oracle_mastered_congratulations}"
            iv, ct = mock.encrypt(secret_msg)
            print(f"[+] Encrypted mock payload ({len(iv + ct)} bytes)")
            recovered = decrypt_ciphertext(
                mock.is_padding_valid, iv + ct, block_size=16
            )
            print(f"[+] Recovered: {recovered.decode('utf-8', errors='replace')}")
            assert recovered == secret_msg, "Decrypted message mismatch"

            # Test ciphertext forgery
            target_msg = b"admin=true;role=root"
            forged = forge_ciphertext(mock.is_padding_valid, target_msg, block_size=16)
            decrypted_forged = decrypt_ciphertext(
                mock.is_padding_valid, forged, block_size=16
            )
            assert decrypted_forged == target_msg, "Forged message mismatch"
            print(f"[+] Ciphertext Forgery verified for '{target_msg.decode()}'")

        if args.mode in ("all", "bleichenbacher"):
            print("[*] Running RSA PKCS#1 v1.5 Bleichenbacher Self-Test...")
            rsa_oracle = MockBleichenbacherOracle()
            m_orig = rsa_oracle.pad_message(0x1337)
            c_orig = rsa_oracle.encrypt(m_orig)
            m_rec = bleichenbacher_attack(
                rsa_oracle.n,
                rsa_oracle.e,
                c_orig,
                rsa_oracle.is_pkcs1_conforming,
            )
            assert m_rec == m_orig, f"Bleichenbacher mismatch: {m_rec} != {m_orig}"
            print(f"[+] Bleichenbacher RSA Oracle verified (recovered m={hex(m_rec)})")

        print("[+] All Padding Oracle self-tests passed successfully!")


if __name__ == "__main__":
    main()
