# BOUND — Stage 1 Spec

**Collection:** Wrapped Mummies
**Ticker:** BOUND
**Chains:** Solana (pump.fun) + Robinhood Chain (PONS)

---

## 1. Locked parameters

```
tiers per chain      5,000  (numbered 1..5000, mirrored on both chains)
total objects        10,000  |  5,000 twin pairs
tokens per NFT       200,000  (0.02% of each chain's 1,000,000,000 supply)
art seed             tier index only — byte-identical across chains
variant slots        none
tier assignment      caller-chosen, unclaimed only, first come first served
mechanic             wrap / unwrap, token-gated, permissionless, reversible
cross-chain movement none
```

---

## 2. Seed derivation

Both chain implementations must produce byte-identical output. Every line here is a place they can silently diverge.

```
TAG          = "BOUND/v1"                       exact ASCII, no null terminator
tier_index   = 1 .. 5000                        one-indexed, reject 0 and >5000
seed         = keccak256( TAG || u32_be(tier_index) )      // 32 bytes

for slot i in 0..6:
    roll_i   = u32_be( seed[4i .. 4i+4] ) % 10000
    walk slot i's option list in declared order, accumulating weights;
    the first option where cumulative > roll_i wins

every slot's weights sum to exactly 10000
7 slots consume bytes 0..28 of the 32
no floating point anywhere
```

**Why these choices:**

- **keccak256** — native opcode on EVM, syscall on Solana. Both cheap, both bit-identical. Not sha3-256, which uses different padding.
- **u32 per slot** — modulo bias against 10,000 with a u16 roll is large enough to make the published rarity table inaccurate. With u32 it's about one part in 400,000.
- **Weights summing to 10,000** — every weight reads directly as basis points, and **count per chain = weight ÷ 2**.
- **Strict `>` on the cumulative walk** — `>=` shifts every boundary by one. Inconsistency here desyncs the chains.

### Divergence checklist

- [ ] keccak256 on both sides
- [ ] `abi.encodePacked(uint32)` matches Rust `(tier as u32).to_be_bytes()` byte for byte
- [ ] TAG is raw ASCII, no length prefix, no terminator
- [ ] Tier is 1-indexed on both; both reject 0 and >5000
- [ ] Byte offsets and slot order identical
- [ ] Roll width u32, big-endian, both sides
- [ ] Modulo divisor 10,000 both sides
- [ ] Option arrays declared in identical order, order frozen before deploy

---

## 3. Trait table

Seven slots. `count` is expected instances per chain (weight ÷ 2), so double it for the total across both chains.

### Slot 0 — WRAP

The linen itself. The body layer.

| Option | Weight | Count |
|---|---|---|
| Bone | 2600 | 1300 |
| Ash | 2000 | 1000 |
| Linen | 1700 | 850 |
| Stained | 1200 | 600 |
| Lapis-dyed | 900 | 450 |
| Verdigris | 600 | 300 |
| Bitumen | 450 | 225 |
| Gold-threaded | 350 | 175 |
| Unraveling | 150 | 75 |
| Alabaster | 50 | 25 |

### Slot 1 — HEAD

| Option | Weight | Count |
|---|---|---|
| None | 3000 | 1500 |
| Nemes | 2200 | 1100 |
| Cap | 1500 | 750 |
| Circlet | 1100 | 550 |
| Jackal mask | 800 | 400 |
| Falcon mask | 600 | 300 |
| Pharaoh crown | 400 | 200 |
| Horned crown | 250 | 125 |
| Sun disk | 100 | 50 |
| Gold crown | 50 | 25 |

### Slot 2 — EYES

| Option | Weight | Count |
|---|---|---|
| Hollow | 2800 | 1400 |
| Painted | 2400 | 1200 |
| Lapis | 1600 | 800 |
| Closed | 1200 | 600 |
| Glowing | 900 | 450 |
| Cracked | 550 | 275 |
| Gold | 350 | 175 |
| Twin pupils | 150 | 75 |
| Void | 50 | 25 |

### Slot 3 — JAW

The expression slot. Deliberately capped at moderate rarity so expression stays readable at avatar size — no ultra-rare options here.

| Option | Weight | Count |
|---|---|---|
| Wrapped | 3400 | 1700 |
| Slack | 2300 | 1150 |
| Grin | 1700 | 850 |
| Snarl | 1200 | 600 |
| Gilded teeth | 800 | 400 |
| Scarab in mouth | 450 | 225 |
| Coin in mouth | 150 | 75 |

### Slot 4 — BIND

What's tied around the wrapping.

| Option | Weight | Count |
|---|---|---|
| None | 3500 | 1750 |
| Cord | 2400 | 1200 |
| Leather strap | 1600 | 800 |
| Chain | 1100 | 550 |
| Seal | 700 | 350 |
| Gold wire | 450 | 225 |
| Broken chain | 200 | 100 |
| Thread of light | 50 | 25 |

### Slot 5 — CHARM

| Option | Weight | Count |
|---|---|---|
| None | 3600 | 1800 |
| Scarab | 2200 | 1100 |
| Ankh | 1500 | 750 |
| Eye amulet | 1100 | 550 |
| Coin | 800 | 400 |
| Vial | 400 | 200 |
| Key | 250 | 125 |
| Paired scarabs | 120 | 60 |
| Hourglass | 30 | 15 |

### Slot 6 — GROUND

| Option | Weight | Count |
|---|---|---|
| Sand | 2600 | 1300 |
| Tomb wall | 2100 | 1050 |
| Lapis field | 1600 | 800 |
| Torchlit | 1200 | 600 |
| Night sky | 900 | 450 |
| Flood | 700 | 350 |
| Gold leaf | 500 | 250 |
| Void | 300 | 150 |
| Eclipse | 100 | 50 |

---

## 4. Rarity bands

For the site's rarity display. Bands are per-item, not per-NFT.

| Band | Weight range | Count per chain |
|---|---|---|
| Common | 1500+ | 750+ |
| Uncommon | 600–1499 | 300–749 |
| Rare | 250–599 | 125–299 |
| Epic | 100–249 | 50–124 |
| Legendary | under 100 | under 50 |

Legendary items: Alabaster wrap, Gold crown, Void eyes, Thread of light, Hourglass (15 per chain — the rarest single trait in the collection).

**Total combinations:** 10 × 10 × 9 × 7 × 8 × 9 × 9 = 4,082,400 possible, against 5,000 tiers drawn.

---

## 5. Duplicate handling — decision required

With 4.08M combinations and 5,000 draws, roughly **3 pairs of tiers will share an identical trait set** by chance. Two options:

**Accept them.** Simplest, and duplicates are normal in generative collections. No extra code.

**Deterministic re-roll.** On collision, re-hash as `keccak256(TAG || u32_be(tier) || u8(attempt))` and increment until unique. Guarantees 5,000 distinct sets — but **both chains must implement the identical collision rule and iterate tiers in the same order**, or the collections desync. This is the single most dangerous place to introduce a divergence.

**Recommendation: accept duplicates.** The uniqueness gain is small, and the desync risk is the one thing that would break the core guarantee.

---

## 6. Artist brief

**Total layers to draw: 59** (62 options minus 3 "None" entries, which render nothing).

Breakdown: 10 wraps, 9 heads, 9 eyes, 7 jaws, 7 binds, 8 charms, 9 grounds.

**Specifications:**

- **Grid:** 32×32 pixels. Larger than the 24×24 typical of this category, because a fully wrapped face has less expression range and needs the extra rows.
- **Format:** transparent PNG per layer, one file per option, exact grid size, no padding variance.
- **Stack order:** ground → wrap → bind → jaw → eyes → head → charm.
- **Anchors:** every wrap option must place the head, eye line, and jaw at identical pixel coordinates. Every head must sit on the same skull line. Any drift breaks every combination using that layer.
- **Palette:** fixed, 16–20 colors total, shared across all layers. Bone and off-whites for linen, a lapis blue range for accents, gold reserved exclusively for the rarest items. Gold must not appear in any Common or Uncommon option — it is the scarcity signal.
- **Tone:** regal and ancient with a cursed edge. Preserved, not decayed.

**The single most important note:** these must emote. A fully bound face reads as a blank silhouette at avatar size. The eyes and jaw slots carry all the personality, so leave a genuine gap in the wrapping for them and draw them with real expression range. If this is gotten wrong, the result is 5,000 variations of the same blank bandage.

---

## 7. Verification artifact

The proof that the two chains match:

1. Enumerate all 5,000 tiers on each chain via view calls
2. Serialize each result canonically (slot order, option index)
3. Hash the full ordered output into one 32-byte digest
4. If the Solana digest equals the Robinhood Chain digest, every NFT in both collections is proven identical

**Build order:**

- [ ] Reference implementation in Python or JS written **first**, before either chain implementation
- [ ] Both chain implementations validated against it across all 5,000 tiers, not a sample
- [ ] Digest computed from live mainnet contracts after deploy, not local builds
- [ ] Digest and reference implementation published at launch

---

## 8. Open items

- [ ] Confirm ticker BOUND is free on pump.fun and the X handle is available
- [ ] Confirm PONS token decimals (pump.fun uses 6; a mismatch changes the raw integer for 200,000)
- [ ] Confirm RH Chain mainnet chain ID
- [ ] Decide duplicate handling (section 5)
- [ ] Decide whether to track a per-tier generation counter
