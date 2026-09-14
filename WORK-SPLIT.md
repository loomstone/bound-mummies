# BOUND — work split

Two AIs, one repo. `canonical/` is frozen and is the tiebreaker for both.

## The principle

Claude writes the Solana side. GPT writes the EVM side. **Independently, from
the same spec, without reading each other's code.** If both reproduce
`canonical/vectors.json` and the collection digest, the spec is unambiguous. If
they diverge, `canonical/reference.py` decides who is wrong, and you have found
a spec ambiguity before mainnet.

Do not let either AI "sync up" the two implementations by copying. That destroys
the entire value of the split.

**Neither AI may modify `canonical/`.** If one believes the spec is wrong, it
reports the issue; it does not edit. A change there invalidates the digest and
silently breaks the twin guarantee.

---

## Ownership

| Area | Owner |
|---|---|
| `canonical/` | frozen — neither |
| `chain/solana/` | Claude |
| `chain/evm/` | GPT |
| `renderer/` | GPT |
| `art/` revision | GPT |
| `web/` | GPT (with your designer) |
| `tools/` | Claude |
| Spec briefs, review, verification | Claude |
| Deployment, keys, funds | **you only** |

Enforced in `AGENTS.md`, which both agents read before working.

---

## Phase 1 — trait selection parity

Nothing else starts until this gate passes.

**Claude — DONE.** `chain/solana/bound-traits`, standalone crate, no Anchor so
the math is isolated. 8 tests pass: keccak-not-sha3, weight sums, range
rejection, determinism, all 12 vectors, the full 5,000-tier digest, and
distribution tracking weight/2. Run with `make rust`.

**GPT:** port to Solidity as `TraitLib.sol`. Same requirement. Foundry test that
asserts every vector and the full-collection digest.

**Gate:** three digests identical — Python, Rust, Solidity.
Currently 2 of 3. Solidity outstanding.

```
0beebbb2d7f6cee419091692001ec6c15ae46070f7bd5459d761407964aee33b
```

Watch points, both sides: keccak256 not sha3-256; `u32` big-endian; strict `>`
on the cumulative walk; slot order from `traits.json`, not memory.

---

## Phase 2 — parallel

**GPT — renderer.** `render(tier)` composing `art/layers` in `stack_order`, plus
batch mode for all 5,000, plus `/api/metadata` and `/api/render` endpoints in
both Metaplex and ERC-721 shapes.

**GPT — art revision.** Restore gold to `jaw/gilded`, `bind/gold_wire`,
`eyes/gold`, `wrap/gold_threaded`. All four are legal under the amended policy.
Re-run `canonical/gold_policy.py` and `art/build.py`. Note this changes asset
hashes, so it must happen before anything pins them.

**Claude — Solana program.** Anchor. `wrap(tier_index)` / `unwrap(tier_index)`,
vault authority `PDA(["vault", nft_mint])`, tier claimed/unclaimed state.

**Claude — verification tooling.** `tools/verify_digest.py` reading from live
contracts, plus a shared adversarial harness both chains run.

---

## Phase 3

**GPT — EVM contracts.** `BoundNFT.sol`, `BoundVault.sol`, wired to its own
`TraitLib`. Unwrap gated on ERC-721 ownership.

**GPT — website.** Per `spec/website-brief.md`. Dual wallet connection is the
hard part. Section 5 of that brief lists claims the copy must not make.

**Claude — review.** I read GPT's contracts against the spec and the adversarial
checklist, same as I did with the art pack: independent verification, not
rubber-stamping.

---

## Phase 4 — testnet

**You:** deploy to devnet and RH Chain testnet.
**Both AIs:** all 13 items in `tools/adversarial-checklist.md` on their own chain.
**Claude:** cross-chain check — wrap #42 on both, diff rendered images
byte-for-byte, recompute both digests from live contracts.

**Gate:** every adversarial test passes on both chains and the images are
byte-identical.

---

## Before mainnet — not AI work

- [ ] **Human review of the unwrap authority path on both chains.** Neither AI
      substitutes for this. A flaw here drains every vault in the collection,
      and it is the single highest-consequence code path in the project.
- [ ] Revoke Solana upgrade authority, or state publicly that you have not
- [ ] Verify sources on both explorers, confirm bytecode matches the repo
- [ ] Publish the digest and `canonical/reference.py`
- [ ] Confirm PONS decimals and RH Chain mainnet chain ID (still open)

---

## Claude's queue

In order:

1. ~~Rust trait selection matching the digest~~ **done**
2. Verify GPT's `TraitLib.sol` independently — build it, run it, check the
   digest myself rather than trusting the report
3. `tools/verify_digest.py` — recompute both digests from live contracts
4. Anchor program: `wrap(tier_index)` / `unwrap(tier_index)`, vault authority
   `PDA(["vault", nft_mint])`, tier claimed/unclaimed state
5. Shared adversarial harness both chains run
6. Review GPT's EVM vault and NFT contracts against the spec
7. Cross-chain check at testnet: wrap #42 on both, diff rendered images
   byte-for-byte

## Working rules

1. The repo is the source of truth, not either chat. Commit after every
   delivery.
2. Give each AI only its own directory plus `canonical/` and `spec/`. Do not
   paste GPT's Solidity into Claude before Phase 1 clears.
3. Every delivery gets independently verified before it counts as done. GPT's
   art pack passed that check; assume the next one might not.
4. Neither AI deploys, holds keys, or touches funds. That is yours alone.
