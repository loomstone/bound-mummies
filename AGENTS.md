# AGENTS.md

Read this before doing anything in this repo. Applies to Claude, ChatGPT, and
any other agent.

---

## The one thing this project is

5,000 numbered NFTs exist on two chains that cannot communicate. NFT #4271 must
render pixel-identically on Solana and on Robinhood Chain. They match because
both chains independently run the same deterministic function on the tier
number.

Every rule below exists to protect that.

---

## Rule 1 — `canonical/` is frozen

`canonical/traits.json`, `canonical/reference.py`, and `canonical/vectors.json`
are the source of truth. **Do not edit them.** Not to fix a typo, not to
reorganize, not to "improve" the seeding.

Changing a weight or reordering a slot changes the collection digest and
silently breaks the twin guarantee. You find out at testnet, or worse, after
launch.

If you believe the spec is wrong, say so in your response. Do not edit.

---

## Rule 2 — implementations stay independent

The Rust and Solidity trait selectors are being written **independently from
the same spec**. That is deliberate. If two independent readings converge on the
same digest, the spec is unambiguous. If one is copied from the other, that
evidence is worthless.

- Do not read the other language's implementation.
- Do not ask for it.
- If your output disagrees with `canonical/vectors.json`, the bug is yours or
  the spec is ambiguous. Report which. Do not copy.

---

## Rule 3 — stay in your directory

Full phase-by-phase assignments are in `WORK-SPLIT.md`. Check it before starting
anything, and check it before assuming a task is yours.

| Directory | Owner |
|---|---|
| `canonical/` | nobody — frozen |
| `spec/` | read-only reference |
| `chain/solana/` | Claude |
| `chain/evm/` | ChatGPT |
| `renderer/` | ChatGPT |
| `art/` | ChatGPT |
| `web/` | ChatGPT |
| `tools/` | Claude |

---

## Rule 4 — the digest is the gate

```
0beebbb2d7f6cee419091692001ec6c15ae46070f7bd5459d761407964aee33b
```

Python, Rust, and Solidity must all produce this across all 5,000 tiers.
Nothing downstream starts until all three match.

---

## Rule 5 — no deployment, no keys, no funds

Agents write and test code. The human deploys. No agent handles private keys,
mainnet transactions, or funds, and no agent should ask for them.

---

## Rule 6 — the vault is the dangerous part

The unwrap authority check is the highest-consequence code in this project. A
flaw there drains every vault in the collection.

Keep that path small and obvious. Do not add cleverness near it. It gets a human
review before mainnet regardless of how thorough the tests are.

---

## Known traps

1. **sha3-256 is not keccak256.** Different padding. Test against
   `keccak256("") = c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470`.
2. **Slot order ≠ stack order.**
   Slot order (seed consumption): `wrap, head, eyes, jaw, bind, charm, ground`
   Stack order (art layering): `ground, wrap, bind, jaw, eyes, head, charm`
3. **Strict `>` on the cumulative walk.** `>=` shifts every boundary by one and
   most tiers still look correct, which is what makes it dangerous.
4. **`spec/stage1-art-and-traits.md` is stale on two weights.** It predates
   amendment GOLD-01/02. `ground/gold` is 240 and `ground/tomb` is 2360.
   `canonical/traits.json` wins.
5. **Tiers are 1-indexed**, valid range 1..5000. Reject 0.

---

## Before you say something is done

- [ ] `make verify` passes
- [ ] Your tests include the adversarial cases, not just the happy path
- [ ] You did not touch `canonical/`
- [ ] You stated plainly what you did NOT do or could not verify
