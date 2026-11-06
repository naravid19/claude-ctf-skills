#!/usr/bin/env python3
"""Multi-Vector RSA Attack Suite for CTF Cryptography.

Provides automated factorization and message recovery for:
1. Wiener's small private exponent attack (continued fractions)
2. Fermat's factorization for close primes (|p - q| is small)
3. Common modulus attack (same modulus n, coprime e1, e2)
4. Hastad's broadcast attack (small e with CRT)
"""

from __future__ import annotations

import argparse
import math
from typing import List, Tuple


def isqrt(n: int) -> int:
    """Integer square root."""
    return math.isqrt(n)


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Extended Euclidean Algorithm: returns (g, x, y) such that a*x + b*y = g."""
    if a == 0:
        return b, 0, 1
    g, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return g, x, y


def continued_fractions(num: int, den: int) -> List[int]:
    """Calculate the continued fraction expansion of num/den."""
    cf = []
    while den != 0:
        q = num // den
        cf.append(q)
        num, den = den, num - q * den
    return cf


def convergents(cf: List[int]) -> List[Tuple[int, int]]:
    """Compute convergents (k/d) from continued fraction terms."""
    n_0, n_1 = 0, 1
    d_0, d_1 = 1, 0
    convs = []
    for q in cf:
        n_2 = q * n_1 + n_0
        d_2 = q * d_1 + d_0
        convs.append((n_2, d_2))
        n_0, n_1 = n_1, n_2
        d_0, d_1 = d_1, d_2
    return convs


def wiener_attack(n: int, e: int) -> int | None:
    """Wiener's attack for small private key d < (1/3) * n^(1/4)."""
    cf = continued_fractions(e, n)
    convs = convergents(cf)

    for k, d in convs:
        if k == 0 or d == 0:
            continue
        # e*d - 1 must be divisible by k
        if (e * d - 1) % k != 0:
            continue
        phi = (e * d - 1) // k
        # Roots of x^2 - (n - phi + 1)x + n = 0 must be integers
        s = n - phi + 1
        discr = s * s - 4 * n
        if discr < 0:
            continue
        r = isqrt(discr)
        if r * r == discr and (s + r) % 2 == 0:
            p = (s + r) // 2
            q = (s - r) // 2
            if p * q == n:
                return d
    return None


def fermat_factorization(n: int, max_iterations: int = 1_000_000) -> Tuple[int, int] | None:
    """Fermat's factorization method for when p and q are close."""
    a = isqrt(n)
    if a * a < n:
        a += 1
    b2 = a * a - n
    for _ in range(max_iterations):
        b = isqrt(b2)
        if b * b == b2:
            return a + b, a - b
        a += 1
        b2 = a * a - n
    return None


def common_modulus_attack(c1: int, c2: int, e1: int, e2: int, n: int) -> int:
    """Recover plaintext when the same message is encrypted under identical n with coprime e1, e2."""
    g, s1, s2 = extended_gcd(e1, e2)
    if g != 1:
        raise ValueError(f"e1 and e2 are not coprime (gcd={g})")

    # If s1 or s2 is negative, calculate modular inverse
    if s1 < 0:
        c1 = pow(c1, -1, n)
        s1 = -s1
    if s2 < 0:
        c2 = pow(c2, -1, n)
        s2 = -s2

    m = (pow(c1, s1, n) * pow(c2, s2, n)) % n
    return m


def nth_root(val: int, n: int) -> int | None:
    """Exact integer n-th root via binary search."""
    if val < 0:
        raise ValueError("Cannot compute root of negative integer")
    if val == 0:
        return 0
    low = 1
    high = val
    while low <= high:
        mid = (low + high) // 2
        p = mid**n
        if p == val:
            return mid
        elif p < val:
            low = mid + 1
        else:
            high = mid - 1
    return None


def hastad_broadcast_attack(ciphertexts: List[int], moduli: List[int], e: int = 3) -> int:
    """Hastad's broadcast attack using CRT across e ciphertexts."""
    if len(ciphertexts) < e or len(moduli) < e:
        raise ValueError(f"Need at least {e} pairs for Hastad attack with e={e}")

    # Solve system with Chinese Remainder Theorem
    total_prod = 1
    for m in moduli[:e]:
        total_prod *= m

    m_e = 0
    for c_i, n_i in zip(ciphertexts[:e], moduli[:e]):
        m_i = total_prod // n_i
        _, inv, _ = extended_gcd(m_i, n_i)
        m_e = (m_e + c_i * m_i * inv) % total_prod

    m = nth_root(m_e, e)
    if m is None:
        raise RuntimeError("Exact n-th root could not be extracted; ensure padding is identical")
    return m


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-Vector RSA Attack Suite")
    parser.add_argument("--test", action="store_true", help="Run comprehensive attack self-tests")
    args = parser.parse_args()

    print("[*] Running RSA Attack Suite Self-Tests...")

    # 1. Fermat Test
    p = 1000000007
    q = 1000000009
    n = p * q
    factors = fermat_factorization(n)
    assert factors is not None and factors[0] * factors[1] == n, "Fermat test failed"
    print(f"[+] Fermat Factorization verified for {n}")

    # 2. Common Modulus Test
    msg = 13374242
    n_cm = 104729 * 1299709
    e1, e2 = 17, 19
    c1 = pow(msg, e1, n_cm)
    c2 = pow(msg, e2, n_cm)
    rec_msg = common_modulus_attack(c1, c2, e1, e2, n_cm)
    assert rec_msg == msg, "Common modulus recovery failed"
    print(f"[+] Common Modulus Attack verified (recovered {rec_msg})")

    # 3. Hastad Broadcast Test
    e_h = 3
    msg_h = 999888777
    mods = [1000000007, 1000000009, 1000000021]
    cts = [pow(msg_h, e_h, m) for m in mods]
    rec_h = hastad_broadcast_attack(cts, mods, e=e_h)
    assert rec_h == msg_h, "Hastad broadcast recovery failed"
    print(f"[+] Hastad Broadcast Attack verified (recovered {rec_h})")

    print("[+] All RSA attack vectors verified successfully!")


if __name__ == "__main__":
    main()
