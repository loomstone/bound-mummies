# HANDOFF — BOUND art generation

You are picking up the art pipeline for an NFT collection. This document is the
complete brief. The working prototype is `bound_layers.py`.

---

## 1. The project in one paragraph

A memecoin launches simultaneously on two blockchains (Solana via pump.fun, and
Robinhood Chain via PONS) through a launchpad called Twine. On top of each token
sits a "wrap" mechanic: lock 200,000 tokens, receive 1 NFT; the NFT holder can
unwrap at any time to get the tokens back. There are 5,000 numbered NFTs per
chain, numbered 1–5,000, **the same numbers on both chains**, so 10,000 objects
and 5,000 twin pairs.

Collection name: Wrapped Mummies. Ticker: BOUND. The art is pixel-art mummies.

---

## 2. The one guarantee everything serves

**NFT #4271 must render pixel-identically on Solana and on Robinhood Chain.**

The two chains have no bridge, no message passing, and no shared state. The
images match because both chains independently run the same deterministic
function on the same input (the tier number). That is the entire thesis of the
project, and it is the constraint that governs every decision below.

---

## 3. CRITICAL — two separate systems, do not confuse them

This trips people up. There are two distinct pieces:

**(A) Trait selection — tier number → which traits.**
Must eventually run identically inside a Solana program (Rust) and an EVM
contract (Solidity). Rules are strict: keccak256 only, u32 big-endian integers,
integer math only, no floating point, no language-specific library behavior.
The spec for this is in section 5 and is **frozen**. Do not "improve" it.

**(B) Layer artwork production — this codebase.**
Runs once, off-chain, in Python. Produces 62 PNG files. Nothing here touches a
blockchain. You have full freedom in how you generate the pixels, as long as the
output files meet the constraints in section 4.

**Your job is (B).** Do not modify (A).

---

## 4. Hard constraints on output

Every layer file must satisfy all of these. `validate()` in the script enforces
most of them.

- Canvas exactly 32×32 pixels. Every layer is full-canvas, not cropped.
- Transparent PNG. Alpha is 0 or 255 only — **no semi-transparent pixels**.
  Anti-aliasing is a bug here, not a feature.
- Every non-transparent pixel must be a color from the `PAL` dict. No new
  colors, no off-by-one shades.
- `gold` and `gold_sh` may only appear in options with weight under 350.
  Gold is the scarcity signal and must not appear in common traits.
- Filenames must match the manifest exactly. A renamed file silently deletes a
  trait from the collection.
- Layers must align to the shared geometry (`in_head`, `in_shoulder`, and the
  anchor constants `EYE_ROWS`, `EYE_LINE`, `JAW_ROWS`). **Never hardcode head
  coordinates anywhere else** — that is how drift gets introduced.

---

## 5. Trait selection spec (FROZEN — reference only, do not implement)

```
TAG        = "BOUND/v1"                  exact ASCII, no terminator
tier       = 1..5000                     reject 0 and >5000
seed       = keccak256( TAG || u32_be(tier) )     // 32 bytes

for slot i in 0..6:
    roll_i = u32_be( seed[4i .. 4i+4] ) % 10000
    walk slot i's options in declared order, accumulating weights;
    first option where cumulative > roll_i wins

all weights per slot sum to exactly 10000
count per chain = weight / 2
```

Slot order is fixed: `0 wrap, 1 head, 2 eyes, 3 jaw, 4 bind, 5 charm, 6 ground`.
Composition stack order is different and is also fixed:
`ground → wrap → bind → jaw → eyes → head → charm`.

---

## 6. What exists and what is missing

The prototype generates **23 of 62 layers across 5 of 7 slots**. It runs, exports
individual PNGs, writes a manifest, and validates.

| Slot | Done | Target | Missing |
|---|---|---|---|
| wrap | 5 | 10 | stained, verdigris, bitumen, gold_threaded, unraveling, alabaster |
| head | 4 | 10 | cap, jackal_mask, falcon_mask, horned_crown, sun_disk, gold_crown |
| eyes | 5 | 9 | painted, cracked, twin_pupils, void |
| jaw | 4 | 7 | snarl, scarab_in_mouth, coin_in_mouth |
| bind | 0 | 8 | entire slot — cord, leather_strap, chain, seal, gold_wire, broken_chain, thread_of_light, none |
| charm | 0 | 9 | entire slot — scarab, ankh, eye_amulet, coin, vial, key, paired_scarabs, hourglass, none |
| ground | 5 | 9 | torchlit, flood, eclipse, night_sky |

Note: new wrap colorways require **no new drawing** — add a three-tone ramp to
`WRAP_RAMPS` and the silhouette recolors automatically. Same trick applies
anywhere a trait is a color variant rather than a new shape.

---

## 7. Known problems to fix

These are visible in the current output and are the highest-value work:

1. **The eye recess reads as a flat black bar.** It currently spans rows 12–16
   as a solid block. It needs internal shaping — a brow shadow, some depth, a
   hint of socket — or every character looks like it is wearing a censor bar.
   This is the single biggest quality problem.

2. **Expression range is too thin.** The jaw slot is carrying all the
   personality on its own. At avatar size these need to actually emote, and
   right now they mostly don't. Eyes and jaw are where the effort goes.

3. **Silhouette merges with background on matching colorways.** A gold wrap on
   a gold-adjacent ground loses its edge entirely. Two possible fixes: add a
   1px dark rim outline on the wrap silhouette, or define exclusion rules
   preventing certain wrap/ground pairs. The outline is simpler and preferred —
   but note it must not use a color outside `PAL`.

4. **All silhouettes are currently identical.** Only color and accessories vary.
   Consider whether some wrap options should alter the silhouette slightly
   (unraveling, for example, should visibly fray).

---

## 8. How to run

```bash
pip install pillow
python3 bound_layers.py
```

Outputs `layers/<slot>/<option>.png`, `layers/manifest.json`, and
`preview/sample_*.png`.

---

## 9. What to deliver back

1. All 62 layers generated and passing `validate()` with zero failures
2. The four problems in section 7 addressed
3. A contact sheet rendering every slot-pair cross product (wrap × head,
   wrap × eyes, head × eyes, etc.) so alignment can be reviewed — roughly a few
   hundred images total. **Errors live in layer pairs, not in the 5,000 final
   outputs**, so verifying all pairs verifies everything.
4. A crop test: a sample rendered in a circle at 48px, to confirm expression is
   still readable at avatar size. If it isn't readable there, the design fails
   regardless of how good it looks at 10× zoom.

---

## 10. Things not to do

- Do not change the canvas size, the palette, the stack order, or the slot order.
- Do not implement or modify the trait selection logic in section 5.
- Do not introduce semi-transparent pixels or anti-aliasing.
- Do not add colors to `PAL` without flagging it — the palette is shared with
  the on-chain Solidity renderer, where every color costs contract size.
- Do not use floating point in anything that will later be ported on-chain.
  (Floating point inside the Python artwork generator is fine — it never runs
  on-chain.)
