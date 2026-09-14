# Status

| Component | State | Notes |
|---|---|---|
| Design | **locked** | caller-chosen assignment, no cross-chain movement |
| Trait table | **locked** | 7 slots, 62 options, gold amendment applied |
| Reference implementation (Python) | **done, tested** | self-tests pass, digest computed |
| Trait selection — Rust | **done, tested** | 8 tests, matches digest, `make rust` |
| Trait selection — Solidity | **not started** | brief at `chain/evm/PHASE1-BRIEF.md` |
| Test vectors | **done** | `canonical/vectors.json`, 12 tiers |
| Art layers | **done** | 62/62, validated: 32x32, binary alpha, on-palette |
| Gold policy | **amended** | 3 bands by pixel count; 1 weight moved |
| Art revision | **pending** | restore gold to 4 traits now legal |
| Renderer | **not started** | |
| Solana program | **not started** | trait selection done, wrap/unwrap pending |
| EVM contracts | **not started** | |
| Website | **spec only** | brief written for a designer |
| v2 swap venue | **spec only** | deliberately deferred |

## Decisions made

- **Assignment: caller-chosen.** `wrap(tier_index)`. Not random, not sequential.
  Random without commit-reveal is worse — bots simulate and abort until they hit
  a rare, making reroll free. Caller-chosen makes every rare cost 200,000 tokens.
  Commit-reveal would work but adds a second state machine around the vaults.
- **No cross-chain movement.** Mirrored twins requires nothing moves.
- **Duplicates: accept.** Deduping needs an identical collision rule on both
  chains — the most likely place to break the guarantee.
- **Gold: 3 bands by pixel count**, replacing the broken binary rule.

## Known unresolved

- PONS decimals, RH Chain mainnet chain ID
- Whether gold leaf ground at weight 240 is rare enough to feel special
- Pairwise art coverage does not prove absence of three-way occlusion
