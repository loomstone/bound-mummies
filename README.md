# BOUND / Wrapped Mummies

Dual-chain wrapped NFT collection. Solana (pump.fun token) + Robinhood Chain
(PONS token), launched through Twine.

Lock 200,000 tokens, get 1 NFT. Unwrap any time to get them back.
5,000 tiers per chain, same numbers on both, 10,000 objects, 5,000 twin pairs.

**NFT #4271 renders pixel-identically on both chains.** The chains never
communicate. They match because both run the same deterministic function on the
same number. That is the entire thesis.

## Collection digest

```
0beebbb2d7f6cee419091692001ec6c15ae46070f7bd5459d761407964aee33b
```

Both chain implementations must reproduce this across all 5,000 tiers before
either goes to mainnet. Changing any weight or slot order changes this number.

## Layout

```
spec/         design documents. specs, not code.
canonical/    SOURCE OF TRUTH. tier -> traits. everything validates against this.
art/          62 layer PNGs + the generator that makes them
renderer/     trait set -> final image            NOT BUILT
chain/solana/ trait selection DONE, program       NOT BUILT
chain/evm/    Solidity contracts                  NOT BUILT
web/          the site                            NOT BUILT
tools/        verification + monitoring           NOT BUILT
```

## Quick start

```bash
make setup      # pip install -r requirements.txt
make verify     # runs every component that exists — this is the gate
```

Individually:

```bash
make canonical  # reference implementation self-tests + digest
make rust       # solana trait selection (8 tests)
make art        # regenerate 62 layers + gold policy audit
make evm        # not built yet
```

Rust is required for `make rust` (`apt install cargo` or rustup).

**Agents: read `AGENTS.md` first.**

## The rule that protects the project

`canonical/` is frozen. Trait selection must run identically in Python, Rust and
Solidity. If someone "improves" the seeding, the twin guarantee silently breaks
and you find out when the digests disagree.

Art production (`art/`) has full freedom as long as output passes validation.

## Build order

Each stage gates the next.

1. **Port trait selection to Rust and Solidity.** Match `canonical/vectors.json`
   seed-for-seed, then match the digest across all 5,000.
2. **Renderer.** Trait set to final image, plus metadata endpoints.
3. **Contracts.** wrap / unwrap on both chains.
4. **Adversarial tests.** `tools/adversarial-checklist.md`, both chains.
5. **Testnet rehearsal.** Wrap #42 on both, diff the images byte-for-byte.
6. **Site.**
7. **Mainnet.** Revoke Solana upgrade authority, verify sources, publish the
   digest and `canonical/reference.py`.

Do not start stage 2 before stage 1 matches. Porting the renderer against an
unverified trait selector means debugging two things at once.

## Open items

- [ ] Confirm ticker BOUND is free on pump.fun, and the X handle
- [ ] Confirm PONS token decimals (pump.fun uses 6)
- [ ] Confirm RH Chain mainnet chain ID
- [ ] Art revision: restore gold to gilded / gold_wire / gold eyes /
      gold_threaded (now legal under the amended policy)
- [ ] Decide duplicate handling — recommendation is accept
