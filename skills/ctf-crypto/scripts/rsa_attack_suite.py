#!/usr/bin/env python3
"""Multi-Vector RSA Attack Suite for CTF Cryptography.

Provides automated factorization and message recovery for:
1. Wiener's Attack (small private exponent d < 1/3 * N^(1/4)) via continued fractions
2. Fermat's factorization for close primes (|p - q| is small)
3. Common modulus attack (same modulus n, coprime e1, e2)
4. Hastad's broadcast attack (small e with CRT)
5. Common factor attack (shared prime factors across moduli via pairwise GCD)
"""

from __future__ import annotations

import argparse
import math
from typing import List, Tuple


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Extended Euclidean Algorithm: returns (g, x, y) such that a*x + b*y = g."""
    if a == 0:
        return b, 0, 1
    x0, x1, y0, y1 = 1, 0, 0, 1
    while b != 0:
        q, a, b = a // b, b, a % b
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return a, x0, y0


def continued_fraction(num: int, den: int) -> List[int]:
    """Expand rational num/den into continued fraction coefficients."""
    coeffs = []
    while den != 0:
        q = num // den
        coeffs.append(q)
        num, den = den, num - q * den
    return coeffs


def convergents(cf: List[int]) -> List[Tuple[int, int]]:
    """Compute convergents (k, d) from continued fraction expansion."""
    convs = []
    h_prev2, h_prev1 = 0, 1
    k_prev2, k_prev1 = 1, 0
    for q in cf:
        h = q * h_prev1 + h_prev2
        k = q * k_prev1 + k_prev2
        convs.append((h, k))
        h_prev2, h_prev1 = h_prev1, h
        k_prev2, k_prev1 = k_prev1, k
    return convs


def wiener_attack(n: int, e: int) -> int | None:
    """Recover small private exponent d using Wiener's continued fractions attack."""
    cf = continued_fraction(e, n)
    convs = convergents(cf)
    for k, d in convs:
        if k == 0 or d == 0:
            continue
        if (e * d - 1) % k != 0:
            continue
        phi = (e * d - 1) // k
        s = n - phi + 1
        discr = s * s - 4 * n
        if discr < 0:
            continue
        r = math.isqrt(discr)
        if r * r == discr and (s + r) % 2 == 0:
            p = (s + r) // 2
            q = (s - r) // 2
            if p * q == n:
                return d
    return None


def fermat_factorization(
    n: int, max_iterations: int = 1_000_000
) -> Tuple[int, int] | None:
    """Fermat's factorization method for when p and q are close."""
    a = math.isqrt(n)
    if a * a < n:
        a += 1
    b2 = a * a - n
    for _ in range(max_iterations):
        b = math.isqrt(b2)
        if b * b == b2:
            return a + b, a - b
        a += 1
        b2 = a * a - n
    return None


def common_factor_attack(moduli: List[int]) -> List[Tuple[int, int, int]]:
    """Factor RSA moduli that share common prime factors via pairwise GCD.

    Returns a list of tuples: (index, p, q) where moduli[index] == p * q.
    """
    results = []
    n_count = len(moduli)
    for i in range(n_count):
        for j in range(i + 1, n_count):
            g = math.gcd(moduli[i], moduli[j])
            if 1 < g < moduli[i]:
                results.append((i, g, moduli[i] // g))
            if 1 < g < moduli[j]:
                results.append((j, g, moduli[j] // g))
    return sorted(list(set(results)), key=lambda x: x[0])


def common_modulus_attack(c1: int, c2: int, e1: int, e2: int, n: int) -> int:
    """Recover plaintext when the same message is encrypted under identical n
    with coprime e1, e2.
    """
    g, s1, s2 = extended_gcd(e1, e2)
    if g != 1:
        raise ValueError(f"e1 and e2 are not coprime (gcd={g})")

    if s1 < 0:
        c1 = pow(c1, -1, n)
        s1 = -s1
    if s2 < 0:
        c2 = pow(c2, -1, n)
        s2 = -s2

    m1 = pow(c1, s1, n)
    m2 = pow(c2, s2, n)
    return (m1 * m2) % n


def integer_nth_root(x: int, n: int) -> Tuple[int, bool]:
    """Compute floor(x^(1/n)) and whether x is a perfect nth power."""
    if x < 0:
        raise ValueError("Cannot extract root of negative integer")
    if x == 0:
        return 0, True
    high = 1 << ((x.bit_length() + n - 1) // n)
    low = 1 << ((x.bit_length() - 1) // n)
    while low < high:
        mid = (low + high) // 2
        p = mid**n
        if p < x:
            low = mid + 1
        elif p > x:
            high = mid
        else:
            return mid, True
    return low - 1, (low - 1) ** n == x


def hastad_broadcast_attack(
    ciphertexts: List[int], moduli: List[int], e: int = 3
) -> int | None:
    """Recover message m when m^e is broadcast across e coprime moduli
    without padding.
    """
    if len(ciphertexts) < e or len(moduli) < e:
        raise ValueError(f"Need at least {e} pairs for Hastad attack with e={e}")

    total_prod = 1
    for m in moduli[:e]:
        total_prod *= m

    result = 0
    for c_i, n_i in zip(ciphertexts[:e], moduli[:e]):
        m_i = total_prod // n_i
        _, inv, _ = extended_gcd(m_i, n_i)
        result = (result + c_i * m_i * (inv % n_i)) % total_prod

    root, exact = integer_nth_root(result, e)
    return root if exact else None


def run_self_tests() -> None:
    print("[*] Running RSA Attack Suite Self-Tests...")

    # 1. Wiener Test
    p_w = 1000000007
    q_w = 1000000009
    n_w = p_w * q_w
    phi_w = (p_w - 1) * (q_w - 1)
    d_w = 1009
    e_w = pow(d_w, -1, phi_w)
    rec_d = wiener_attack(n_w, e_w)
    assert rec_d == d_w, f"Wiener attack failed: expected {d_w}, got {rec_d}"
    print(f"[+] Wiener Attack verified for small d={d_w}")

    # 2. Fermat Test
    p_f = 1000000007
    q_f = 1000000009
    n_f = p_f * q_f
    factors = fermat_factorization(n_f)
    assert factors is not None and factors[0] * factors[1] == n_f, "Fermat test failed"
    print(f"[+] Fermat Factorization verified for {n_f}")

    # 3. Common Factor Test
    p_cf = 1000000007
    q1_cf = 1000000009
    q2_cf = 1000000021
    mods = [p_cf * q1_cf, p_cf * q2_cf]
    cf_res = common_factor_attack(mods)
    assert len(cf_res) == 2 and cf_res[0][1] == p_cf, "Common factor attack failed"
    print(f"[+] Common Factor Attack verified across {len(mods)} moduli")

    # 4. Common Modulus Test
    msg = 13374242
    n_cm = 104729 * 1299709
    e1, e2 = 17, 19
    c1 = pow(msg, e1, n_cm)
    c2 = pow(msg, e2, n_cm)
    rec_msg = common_modulus_attack(c1, c2, e1, e2, n_cm)
    assert rec_msg == msg, "Common modulus recovery failed"
    print(f"[+] Common Modulus Attack verified (recovered {rec_msg})")

    # 5. Hastad Broadcast Test
    e_h = 3
    msg_h = 999888777
    h_mods = [1000000007, 1000000009, 1000000021]
    cts = [pow(msg_h, e_h, m) for m in h_mods]
    rec_h = hastad_broadcast_attack(cts, h_mods, e=e_h)
    assert rec_h == msg_h, "Hastad broadcast recovery failed"
    print(f"[+] Hastad Broadcast Attack verified (recovered {rec_h})")

    print("[+] All RSA Attack Suite self-tests passed!")


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-Vector RSA Attack Suite")
    parser.add_argument(
        "--test", action="store_true", help="Run comprehensive attack self-tests"
    )
    parser.add_argument(
        "--attack",
        choices=["wiener", "fermat"],
        help="Run a specific single-modulus attack from CLI",
    )
    parser.add_argument("--n", type=int, help="RSA modulus n")
    parser.add_argument("--e", type=int, help="RSA public exponent e")
    args = parser.parse_args()

    if args.attack == "wiener":
        if args.n is None or args.e is None:
            parser.error("--attack wiener requires --n and --e")
        d = wiener_attack(args.n, args.e)
        print(f"[+] Wiener result d = {d}")
    elif args.attack == "fermat":
        if args.n is None:
            parser.error("--attack fermat requires --n")
        factors = fermat_factorization(args.n)
        print(f"[+] Fermat factors = {factors}")
    else:
        run_self_tests()


if __name__ == "__main__":
    main()
