"""
BOUND / Wrapped Mummies — CANONICAL REFERENCE IMPLEMENTATION

This file is the single source of truth for tier -> traits.

The Solana program (Rust) and the Robinhood Chain contract (Solidity) must each
reproduce this exactly, for all 5,000 tiers, before either goes to mainnet.
If the three collection digests do not match, something is wrong and nothing
ships.

    python3 reference.py            run self-tests and print the digest
    python3 reference.py 42         show the traits for one tier
    python3 reference.py --vectors  emit test vectors for the porters

Requires: pycryptodome  (pip install pycryptodome)
"""

import json
import os
import sys
from Crypto.Hash import keccak

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(HERE, "traits.json")))

TAG = CFG["tag"].encode("ascii")          # b"BOUND/v1" — exact, no terminator
TIERS = CFG["tiers_per_chain"]            # 5000
SLOT_ORDER = CFG["slot_order"]            # consumes seed bytes in this order
SLOTS = CFG["slots"]


# ----------------------------------------------------------------------
# Primitives. Every line here has a Solidity and a Rust equivalent that
# must behave identically. Deviations here are how the chains desync.
# ----------------------------------------------------------------------

def keccak256(data: bytes) -> bytes:
    """Solidity: keccak256(...)   Rust/Solana: keccak::hash(...).to_bytes()"""
    h = keccak.new(digest_bits=256)
    h.update(data)
    return h.digest()


def u32_be(n: int) -> bytes:
    """
    4 bytes, big-endian.
    Solidity: abi.encodePacked(uint32(n))
    Rust:     (n as u32).to_be_bytes()
    """
    if not 0 <= n < 2**32:
        raise ValueError("u32 out of range")
    return n.to_bytes(4, "big")


def seed_for(tier: int) -> bytes:
    if not 1 <= tier <= TIERS:
        raise ValueError(f"tier must be 1..{TIERS}, got {tier}")
    return keccak256(TAG + u32_be(tier))


def pick(options, roll: int):
    """
    Cumulative walk in DECLARED ORDER. Strict '>' comparison.

    Using '>=' instead shifts every boundary by one and will silently
    desync two implementations. This comparison is load-bearing.
    """
    cumulative = 0
    for name, weight in options:
        cumulative += weight
        if cumulative > roll:
            return name
    # Unreachable when weights sum to 10000 and roll is in 0..9999.
    raise AssertionError("weights do not sum to 10000")


def traits_for(tier: int) -> dict:
    """The canonical function. tier -> {slot: option}."""
    seed = seed_for(tier)
    out = {}
    for i, slot in enumerate(SLOT_ORDER):
        roll = int.from_bytes(seed[4 * i:4 * i + 4], "big") % 10000
        out[slot] = pick(SLOTS[slot], roll)
    return out


# ----------------------------------------------------------------------
# Collection digest — the cross-chain proof artifact.
# One 32-byte number that proves all 5,000 trait sets are identical.
# ----------------------------------------------------------------------

def serialize(tier: int, traits: dict) -> bytes:
    """
    Canonical serialization. Option INDEX, not name, so the digest is
    language- and encoding-independent.
    """
    buf = u32_be(tier)
    for slot in SLOT_ORDER:
        names = [n for n, _ in SLOTS[slot]]
        buf += bytes([names.index(traits[slot])])
    return buf


def collection_digest() -> str:
    h = keccak.new(digest_bits=256)
    for tier in range(1, TIERS + 1):
        h.update(serialize(tier, traits_for(tier)))
    return h.hexdigest()


# ----------------------------------------------------------------------
# Self-tests. These run every time. If any fail, do not ship.
# ----------------------------------------------------------------------

def self_test():
    fails = []

    k = keccak256(b"").hex()
    if k != "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470":
        fails.append(f"keccak256 is wrong (got {k}) — is this sha3-256 instead?")

    for slot, opts in SLOTS.items():
        total = sum(w for _, w in opts)
        if total != 10000:
            fails.append(f"{slot}: weights sum to {total}, must be 10000")

    if len(SLOT_ORDER) != 7:
        fails.append(f"expected 7 slots, got {len(SLOT_ORDER)}")
    if set(SLOT_ORDER) != set(SLOTS):
        fails.append("slot_order does not match the slots table")

    for bad in (0, TIERS + 1, -1):
        try:
            traits_for(bad)
            fails.append(f"tier {bad} should have been rejected")
        except ValueError:
            pass

    if traits_for(1) != traits_for(1):
        fails.append("traits_for is not deterministic")

    # Gold policy: dominant gold must be rare.
    bands = CFG["gold_policy"]["bands"]
    dom = next(b for b in bands if b["name"] == "dominant")
    for slot, opts in SLOTS.items():
        for name, w in opts:
            if slot == "ground" and name == "gold" and w > dom["max_weight"]:
                fails.append(f"ground/gold weight {w} exceeds dominant cap "
                             f"{dom['max_weight']} — amendment GOLD-01 not applied")

    # Distribution sanity: observed counts should track weight/2.
    counts = {s: {} for s in SLOT_ORDER}
    for t in range(1, TIERS + 1):
        for s, o in traits_for(t).items():
            counts[s][o] = counts[s].get(o, 0) + 1
    for slot, opts in SLOTS.items():
        for name, w in opts:
            expected = w / 2.0
            got = counts[slot].get(name, 0)
            tol = max(4 * (expected ** 0.5), 5)
            if abs(got - expected) > tol:
                fails.append(f"{slot}/{name}: expected ~{expected:.0f}, got {got}")

    return fails, counts


def print_vectors(n=12):
    """Test vectors for whoever ports this to Rust and Solidity."""
    print("tier | seed (first 8 bytes) | " + " | ".join(SLOT_ORDER))
    for t in [1, 2, 42, 100, 777, 1234, 2500, 3333, 4271, 4999, 5000, 1337][:n]:
        s = seed_for(t)
        tr = traits_for(t)
        print(f"{t:4} | {s[:8].hex()} | " + " | ".join(tr[k] for k in SLOT_ORDER))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--vectors":
        print_vectors()
        sys.exit(0)

    if len(sys.argv) > 1:
        t = int(sys.argv[1])
        print(f"tier {t}")
        print(f"  seed   {seed_for(t).hex()}")
        for slot, opt in traits_for(t).items():
            w = dict(SLOTS[slot])[opt]
            print(f"  {slot:7} {opt:18} weight {w:>5}  (~{w//2} per chain)")
        sys.exit(0)

    fails, counts = self_test()
    if fails:
        print("SELF-TEST FAILED")
        for f in fails:
            print("  -", f)
        sys.exit(1)

    print("self-test passed")
    print()
    print("rarest options actually present:")
    rare = []
    for slot, opts in SLOTS.items():
        for name, w in opts:
            if w <= 250:
                rare.append((w, slot, name, counts[slot].get(name, 0)))
    for w, slot, name, got in sorted(rare)[:10]:
        print(f"  {slot:7} {name:18} weight {w:>4}  actual {got:>4} per chain")
    print()
    print("COLLECTION DIGEST")
    print(f"  {collection_digest()}")
    print()
    print("Both chain implementations must reproduce this exact digest.")
