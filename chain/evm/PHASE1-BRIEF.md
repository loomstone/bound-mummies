# Phase 1 brief — TraitLib.sol

Implement BOUND trait selection in Solidity. This is the only task right now.
Do not write the NFT or vault contracts yet.

## Context

A collection of 5,000 numbered NFTs exists on two chains that cannot
communicate: Solana and Robinhood Chain (Arbitrum stack). NFT #4271 must render
identically on both. They match because both chains independently run the same
deterministic function on the tier number.

Your Solidity implementation and a separate Rust implementation are being
written **independently from this spec**. If both reproduce the vectors and the
digest below, the spec is unambiguous. That is the point of doing it twice.

**Do not ask for, look at, or reconcile against the Rust implementation.** If
your output disagrees with the target values, the bug is in your code or the
spec is ambiguous — report which, do not copy.

## Reference

`canonical/reference.py` is the source of truth. `canonical/traits.json` holds
the weights. `canonical/vectors.json` holds the targets. Read those. Do not
modify anything in `canonical/`.

## The algorithm

```
TAG      = "BOUND/v1"          raw ASCII, 8 bytes, no length prefix, no terminator
tier     = 1..5000             reject 0 and anything above 5000
seed     = keccak256(abi.encodePacked(TAG, uint32(tier)))     // 32 bytes

for slot i in 0..6:
    roll = uint32(bytes4(seed[4i : 4i+4])) % 10000
    walk that slot's options in DECLARED ORDER, accumulating weights
    first option where cumulative > roll wins        // STRICT >
```

Slot order (the order seed bytes are consumed):
`0 wrap, 1 head, 2 eyes, 3 jaw, 4 bind, 5 charm, 6 ground`

Note this is NOT the art stack order, which is
`ground, wrap, bind, jaw, eyes, head, charm`. Do not confuse them.

Every slot's weights sum to exactly 10000.

## Serialization and digest

```
serialize(tier) = abi.encodePacked(uint32(tier), uint8 optionIndex per slot in slot order)
                  // 11 bytes total

collection_digest = keccak256( serialize(1) || serialize(2) || ... || serialize(5000) )
```

Option **index**, not name. The digest must be computable via a view function or
an off-chain loop over view calls — your choice, but it must be reproducible by
a third party.

## Targets

Digest:

```
0beebbb2d7f6cee419091692001ec6c15ae46070f7bd5459d761407964aee33b
```

Spot vectors (seed shown is the first 8 bytes):

| tier | seed[0..8] | wrap | head | eyes | jaw | bind | charm | ground |
|---|---|---|---|---|---|---|---|---|
| 1 | 7b16508aafbb1aba | alabaster | nemes | void | snarl | cord | scarab | sand |
| 3 | 867134e729c626a7 | linen | none | twin_pupils | grin | leather_strap | scarab | lapis |
| 42 | 194d278718290a5d | stained | none | lapis | wrapped | cord | none | sand |
| 777 | e74f7e8405050a43 | stained | cap | hollow | wrapped | none | vial | flood |
| 4271 | 552488e0afa3f783 | lapis | jackal_mask | closed | slack | cord | paired_scarabs | flood |
| 5000 | f09db8666cd51ea1 | lapis | cap | hollow | snarl | seal | scarab | torchlit |

The full 12 vectors are in `canonical/vectors.json`.

## Required tests (Foundry)

- [ ] `keccak256("")` equals
      `c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470`
      — catches accidentally using sha3-256
- [ ] every slot's weights sum to exactly 10000
- [ ] tier 0 reverts; tier 5001 reverts; tier 1 and 5000 succeed
- [ ] all 12 vectors match, seed and traits
- [ ] the collection digest matches across all 5000 tiers
- [ ] observed option counts track weight/2 within tolerance
- [ ] `ground/gold` has weight 240 and `ground/tomb` has weight 2360
      (amendment GOLD-01/02 — if you see 500 and 2100 anywhere, that source is stale)

## Where this usually goes wrong

1. **sha3-256 instead of keccak256.** Different padding, different output. The
   empty-string test catches it immediately.
2. **Endianness.** `uint32` must be big-endian, 4 bytes. `abi.encodePacked`
   gives this; manual byte assembly often does not.
3. **`>=` instead of `>`** on the cumulative walk. Shifts every boundary by one.
   Most tiers still look right, which is what makes it dangerous.
4. **Slot order confused with stack order.** They are different lists.
5. **Reading weights from a stale doc.** `spec/stage1-art-and-traits.md` predates
   the gold amendment. `canonical/traits.json` is authoritative.

## Deliverable

`chain/evm/src/TraitLib.sol` plus `chain/evm/test/TraitLib.t.sol`, with
`forge test` passing all of the above. Nothing else in this phase.

## Gas

Not a concern yet. Correctness first. If the digest loop is too expensive
on-chain, compute it off-chain over view calls — the digest is a launch-time
proof artifact, not a runtime path.
