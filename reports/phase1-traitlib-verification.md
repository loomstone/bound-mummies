# Phase 1 verification — `chain/evm/src/TraitLib.sol`

Independent verification of GPT's Solidity port, per `WORK-SPLIT.md` queue item 2.
Performed by Claude. Method: compile from source and execute, not read-and-approve.

**Result: PASS.** The Solidity reproduces the canonical digest.

```
0beebbb2d7f6cee419091692001ec6c15ae46070f7bd5459d761407964aee33b
```

---

## What was done

`forge` was not available, so GPT's own `test/TraitLib.t.sol` was **not** run.
Instead `TraitLib.sol` was compiled with solc and executed in an EVM against an
independently written harness, which is the stronger check for this purpose — it
does not inherit any assumption from GPT's test file.

- solc 0.8.26 (npm `solc`), `@ethereumjs/evm` 3.1.0
- Harness exposes `collectionDigest()`, `seedFor()`, `traitsFor()`, `serialize()`
- `canonical/` was not modified

## Checks and outcomes

| # | Check | Result |
|---|---|---|
| 1 | Python `reference.py` self-tests + digest | pass — `0beebbb2…` |
| 2 | Solidity `collectionDigest()` over all 5,000 tiers | pass — `0beebbb2…` |
| 3 | All 12 vectors in `canonical/vectors.json` — seeds | 12/12 match |
| 4 | All 12 vectors — trait indices | 12/12 match |
| 5 | `serialize()` bytes vs Python, tiers 1 / 42 / 4271 / 5000 | byte-identical, 11 bytes each |
| 6 | Tier 0 rejected | reverts `InvalidTier` |
| 7 | Tier 5001 rejected | reverts `InvalidTier` |
| 8 | Static diff of all 7 slots' weights vs `traits.json` | all match, each sums to 10000 |
| 9 | Static diff of `_pick` cumulative boundaries vs `traits.json` | all match |
| 10 | Digest stability across compiler settings | identical in all 7 configs |

Config matrix for check 10 — optimizer off; optimizer on at 200 runs; optimizer
on at 1,000,000 runs; viaIR + optimizer; and `evmVersion` paris, shanghai,
cancun. Same digest every time.

## Known traps from `AGENTS.md` — confirmed handled

- **keccak256 vs sha3-256** — correct. Seeds match the reference for all 12 vectors;
  sha3 padding would diverge on the first one.
- **Slot order** — `traitsFor` consumes `wrap, head, eyes, jaw, bind, charm, ground`,
  matching `slot_order` in `traits.json`. Stack order is a renderer concern and is
  not touched here.
- **Strict `>` on the cumulative walk** — implemented as `roll < cumulative`, which
  is the correct transposition. Verified by boundary diff (check 9), not by eye.
- **1-indexed, reject 0** — confirmed by checks 6 and 7.
- **`u32` big-endian** — `abi.encodePacked(uint32)` is big-endian; seeds match.

---

## What was NOT verified

Stated plainly, per the `AGENTS.md` closing checklist.

1. **The Rust leg was not re-run this session.** No `cargo`/`rustc` in the
   container. `make rust` did not execute. This report closes Python↔Solidity
   directly; the Rust digest is taken from `STATUS.md`'s prior result. The
   three-way gate is therefore 3/3 **on record** but 2/3 **re-confirmed today**.
   Re-run `make rust` on a machine with the Rust toolchain to close that.
2. **GPT's `test/TraitLib.t.sol` was never executed.** Its assertions are
   unverified. The library is verified; its test file is not.
3. **solc version drift.** `foundry.toml` pins `0.8.24`; this used `0.8.26`.
   Digest identical, but the pinned version was not the one exercised.
4. **Nothing downstream** — no vault, NFT, or renderer code exists or was reviewed.

---

## Review finding — low severity, not digest-affecting

`collectionDigest()` writes past the end of its buffer on the final iteration.

```solidity
bytes memory all = new bytes(uint256(MAX_TIER) * 11);   // 55,000 bytes
...
assembly ("memory-safe") {
    mstore(add(add(all, 32), cursor), shl(168, item))   // 32-byte write
}
```

The last write is at `cursor = 4999 * 11 = 54,989` and is 32 bytes wide, so it
spans bytes 54,989–55,021 of a 55,000-byte array. Solidity pads the allocation to
55,008, leaving roughly 13 bytes written beyond the allocated region.

It is harmless today: `keccak256(all)` reads only the first 55,000 bytes, and the
memory it spills into holds a `Traits` struct allocated back in iteration 1, long
dead by then. The digest was stable across all seven compiler configurations
above, including viaIR.

The problem is the `("memory-safe")` annotation, which is a promise to the
optimizer that the block writes only inside its own allocations. That promise is
false here. Nothing exploits it today; a future optimizer that reuses memory on
the strength of that annotation could. Blast radius is small — this is a
launch-time proof helper, explicitly not a runtime minting path.

Suggested fix for GPT, either:
- allocate `MAX_TIER * 11 + 32` and keep the fast path, or
- drop the `memory-safe` annotation, or
- write the last item with a masked read-modify-write.

This is reported, not edited. `chain/evm/` is GPT's directory.

---

## Gate status

Phase 1 is clear on the evidence available. Phase 2 unblocks:

- Claude — Anchor program: `wrap(tier_index)` / `unwrap(tier_index)`, vault
  authority `PDA(["vault", nft_mint])`, tier claimed/unclaimed state
- Claude — `tools/verify_digest.py`
- GPT — renderer, art revision
