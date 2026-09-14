# renderer — NOT BUILT

Turns a trait set into a final image.

## What it does

    tier -> canonical/reference.py -> trait set -> stack art/layers/*.png -> final PNG

Stack order is fixed and lives in `canonical/traits.json` as `stack_order`:
`ground -> wrap -> bind -> jaw -> eyes -> head -> charm`

## What to build

- [ ] `render.py` — render(tier) -> 32x32 PNG, composing from art/layers
- [ ] Batch mode: render all 5000, write to `out/`
- [ ] `/api/metadata/<chain>/<tier>` — Metaplex-compatible JSON (Solana) and
      ERC-721 `tokenURI` JSON (EVM)
- [ ] `/api/render/<tier>.png` — the image endpoint
- [ ] Upscale option (marketplaces want more than 32px; use NEAREST only)

## Constraint that matters

The Solana side cannot render on-chain — Metaplex metadata points at a URI that
marketplaces fetch over HTTP. So this service is load-bearing for the Solana
collection's images.

The EVM side CAN embed an on-chain SVG renderer in Solidity (cheap on an L2).
If you do that, the two sides have different permanence guarantees. Say so
honestly in the site copy rather than claiming "fully onchain".
