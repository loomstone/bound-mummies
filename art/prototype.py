"""
BOUND / Wrapped Mummies — procedural layer generator (PROTOTYPE)

WHAT THIS IS
    Generates the individual transparent PNG layers that make up the NFT art,
    entirely in code. No hand-drawn assets.

WHAT IT IS NOT
    This is NOT the on-chain trait selection logic. See HANDOFF.md section 3.
    This script only PRODUCES ARTWORK FILES. Which traits a given tier gets is
    decided by a separate deterministic function that must be portable to both
    Solidity and Rust.

OUTPUT
    layers/<slot>/<option>.png   one 32x32 transparent PNG per trait option
    preview/*.png                composed sample characters for eyeballing

STATUS
    Prototype covering 5 of 10 wraps, 5 of 9 eyes, 4 of 10 heads,
    4 of 7 jaws, 5 of 9 grounds. BIND and CHARM slots not started.
    See HANDOFF.md section 6 for what needs finishing.
"""

from PIL import Image
import os
import json

# ============================================================
# 1. CANVAS + PALETTE  (both are LOCKED — do not change)
# ============================================================

S = 32                 # canvas is 32x32, every layer is full-canvas
TRANSPARENT = (0, 0, 0, 0)

# Every color used anywhere must come from this dict.
# Validation rejects any pixel not in here.
PAL = {
    "bone":      (232, 226, 208, 255),
    "bone_sh":   (196, 188, 168, 255),
    "bone_dk":   (150, 142, 126, 255),
    "ash":       (176, 176, 180, 255),
    "ash_sh":    (140, 140, 146, 255),
    "ash_dk":    (100, 100, 108, 255),
    "linen":     (226, 200, 156, 255),
    "linen_sh":  (192, 164, 120, 255),
    "linen_dk":  (148, 124, 88, 255),
    "lapis":     (42, 78, 158, 255),
    "lapis_sh":  (30, 56, 118, 255),
    "lapis_dk":  (20, 38, 84, 255),
    "lapis_lt":  (86, 132, 216, 255),
    "gold":      (222, 176, 68, 255),
    "gold_sh":   (176, 130, 42, 255),
    "void":      (18, 16, 24, 255),
    "shadow":    (40, 36, 48, 255),
    "glow":      (140, 200, 240, 255),
    "sand":      (206, 184, 140, 255),
    "sand_dk":   (170, 148, 108, 255),
    "wall":      (110, 96, 82, 255),
    "wall_dk":   (86, 74, 64, 255),
}

# GOLD IS THE SCARCITY SIGNAL.
# "gold" and "gold_sh" may only appear in trait options whose weight is
# under 350 (i.e. under 175 instances per chain). Validation enforces this.
GOLD = {"gold", "gold_sh"}

# Three-tone ramps for wrap colorways. Adding a new wrap colorway = adding
# one entry here. No new drawing required. This is the palette-swap trick:
# one silhouette, N colorways, aligned by construction.
WRAP_RAMPS = {
    "bone":   ("bone", "bone_sh", "bone_dk"),
    "ash":    ("ash", "ash_sh", "ash_dk"),
    "linen":  ("linen", "linen_sh", "linen_dk"),
    "lapis":  ("lapis_lt", "lapis", "lapis_sh"),
    "gold":   ("gold", "gold_sh", "lapis_dk"),
    # TODO stained, verdigris, bitumen, gold_threaded, unraveling, alabaster
}


# ============================================================
# 2. GEOMETRY  (the shared anchor — every layer aligns to this)
# ============================================================
# CRITICAL: every layer is generated against these two functions.
# This is why alignment is free and cannot drift. Do not hardcode
# head coordinates anywhere else in the file.

def in_head(x, y):
    """Rounded skull mass, rows 5..23, tapering at crown and chin."""
    if y < 5 or y > 23:
        return False
    cx = 15.5
    if y <= 7:
        hw = 5.0 + (y - 5) * 1.3
    elif y <= 19:
        hw = 7.6
    else:
        hw = 7.6 - (y - 19) * 1.5
    return abs(x - cx) <= hw


def in_shoulder(x, y):
    """Shoulder mass, rows 24..31."""
    if y < 24:
        return False
    hw = 6.0 + (y - 24) * 2.2
    return abs(x - 15.5) <= min(hw, 14.5)


# Fixed anchor rows. Any new layer must respect these.
EYE_ROWS = (12, 16)     # the recess carved into the wrap
EYE_LINE = 14           # where pupils sit
JAW_ROWS = (19, 20)
EYE_L, EYE_R = 12, 19   # left/right pupil x origins


def blank():
    return Image.new("RGBA", (S, S), TRANSPARENT)


def px(img, x, y, c):
    if 0 <= x < S and 0 <= y < S:
        img.putpixel((x, y), c)


def hline(img, x0, x1, y, c):
    for x in range(x0, x1 + 1):
        px(img, x, y, c)


# ============================================================
# 3. SLOT GENERATORS
# ============================================================

def wrap_layer(name):
    """Slot 0 — the linen. Body layer, always present."""
    lt, md, dk = (PAL[c] for c in WRAP_RAMPS[name])
    img = blank()
    for y in range(S):
        for x in range(S):
            if in_head(x, y) or in_shoulder(x, y):
                band = (y + (x // 9)) % 3          # bandage seam every 3rd row
                c = md if band == 0 else lt
                if x < 11:                          # left-side shading
                    c = dk if band == 0 else md
                edge = not (in_head(x + 1, y) or in_shoulder(x + 1, y)) or \
                       not (in_head(x - 1, y) or in_shoulder(x - 1, y))
                if edge:
                    c = dk
                px(img, x, y, c)
    # carve the eye recess
    for y in range(EYE_ROWS[0], EYE_ROWS[1] + 1):
        for x in range(S):
            if in_head(x, y) and 9 <= x <= 22:
                px(img, x, y, PAL["shadow"] if y in EYE_ROWS else PAL["void"])
    # loose bandage tail
    px(img, 23, 20, dk); px(img, 24, 21, dk); px(img, 24, 22, md)
    return img


def eyes_layer(name):
    """Slot 2 — pupils inside the recess. Carries most of the personality."""
    img = blank()
    L, R = EYE_L, EYE_R
    if name == "hollow":
        for x in (L, L + 1, R, R + 1):
            px(img, x, EYE_LINE, PAL["shadow"])
    elif name == "lapis":
        for x in (L, L + 1, R, R + 1):
            px(img, x, EYE_LINE, PAL["lapis_lt"])
        px(img, L, EYE_LINE, PAL["lapis"]); px(img, R + 1, EYE_LINE, PAL["lapis"])
    elif name == "glowing":
        for x in range(L - 1, L + 3):
            px(img, x, EYE_LINE, PAL["glow"])
        for x in range(R - 1, R + 3):
            px(img, x, EYE_LINE, PAL["glow"])
        for x in (L, L + 1, R, R + 1):
            px(img, x, EYE_LINE - 1, PAL["lapis_lt"])
            px(img, x, EYE_LINE + 1, PAL["lapis_lt"])
    elif name == "gold":
        for x in (L, L + 1, R, R + 1):
            px(img, x, EYE_LINE, PAL["gold"])
            px(img, x, EYE_LINE + 1, PAL["gold_sh"])
    elif name == "closed":
        hline(img, L - 1, L + 2, EYE_LINE, PAL["bone_dk"])
        hline(img, R - 1, R + 2, EYE_LINE, PAL["bone_dk"])
    # TODO painted, cracked, twin_pupils, void
    return img


def head_layer(name):
    """Slot 1 — headwear / mask. Sits on the crown."""
    img = blank()
    if name == "none":
        return img
    if name == "nemes":
        for y in range(4, 12):
            for x in range(S):
                if in_head(x, y) or (6 <= y <= 11 and abs(x - 15.5) <= 9.5):
                    px(img, x, y, PAL["gold"] if y % 2 == 0 else PAL["lapis"])
        for y in range(12, 22):
            for x in (6, 7, 24, 25):
                px(img, x, y, PAL["gold"] if y % 2 == 0 else PAL["lapis"])
    elif name == "circlet":
        for x in range(8, 24):
            px(img, x, 8, PAL["gold"]); px(img, x, 9, PAL["gold_sh"])
        px(img, 15, 7, PAL["lapis_lt"]); px(img, 16, 7, PAL["lapis_lt"])
    elif name == "crown":
        for x in range(9, 23):
            px(img, x, 7, PAL["gold"]); px(img, x, 8, PAL["gold_sh"])
        for x in (10, 13, 15, 16, 18, 21):
            px(img, x, 6, PAL["gold"]); px(img, x, 5, PAL["gold"])
        px(img, 15, 4, PAL["lapis_lt"]); px(img, 16, 4, PAL["lapis_lt"])
    # TODO cap, jackal_mask, falcon_mask, horned_crown, sun_disk, gold_crown
    return img


def jaw_layer(name):
    """Slot 3 — mouth region. Second personality slot."""
    img = blank()
    if name == "wrapped":
        return img
    if name == "grin":
        hline(img, 13, 18, 19, PAL["void"])
        for x in (13, 15, 17):
            px(img, x, 20, PAL["bone"])
        for x in (14, 16, 18):
            px(img, x, 20, PAL["void"])
    elif name == "gilded":
        hline(img, 13, 18, 19, PAL["void"])
        hline(img, 13, 18, 20, PAL["gold"])
    elif name == "slack":
        hline(img, 14, 17, 19, PAL["shadow"])
        hline(img, 14, 17, 20, PAL["void"])
    # TODO snarl, scarab_in_mouth, coin_in_mouth
    return img


def ground_layer(name):
    """Slot 6 — background. Fully opaque, drawn first."""
    img = blank()
    if name == "sand":
        for y in range(S):
            hline(img, 0, S - 1, y, PAL["sand"] if y < 20 else PAL["sand_dk"])
    elif name == "tomb":
        for y in range(S):
            hline(img, 0, S - 1, y, PAL["wall"])
        for y in range(0, S, 6):
            hline(img, 0, S - 1, y, PAL["wall_dk"])
        for x in range(0, S, 8):
            for y in range(S):
                px(img, x, y, PAL["wall_dk"])
    elif name == "lapis":
        for y in range(S):
            hline(img, 0, S - 1, y, PAL["lapis"] if y % 7 else PAL["lapis_sh"])
    elif name == "void":
        for y in range(S):
            hline(img, 0, S - 1, y, PAL["void"])
        for (x, y) in [(4, 5), (27, 9), (9, 26), (22, 3), (14, 29), (29, 20)]:
            px(img, x, y, PAL["lapis_lt"])
    elif name == "gold":
        for y in range(S):
            hline(img, 0, S - 1, y, PAL["gold_sh"])
        for y in range(0, S, 4):
            hline(img, 0, S - 1, y, PAL["gold"])
    # TODO torchlit, flood, eclipse, night_sky
    return img


# TODO bind_layer()  — slot 4, cord/strap/chain/seal around the wrapping
# TODO charm_layer() — slot 5, scarab/ankh/amulet/coin


# ============================================================
# 4. COMPOSITION  (stack order is LOCKED)
# ============================================================

STACK = ["ground", "wrap", "bind", "jaw", "eyes", "head", "charm"]

GENERATORS = {
    "wrap":   (wrap_layer,   list(WRAP_RAMPS.keys())),
    "head":   (head_layer,   ["none", "nemes", "circlet", "crown"]),
    "eyes":   (eyes_layer,   ["hollow", "lapis", "glowing", "gold", "closed"]),
    "jaw":    (jaw_layer,    ["wrapped", "slack", "grin", "gilded"]),
    "ground": (ground_layer, ["sand", "tomb", "lapis", "void", "gold"]),
}


def compose(traits):
    """traits: dict of slot -> option name. Returns composed 32x32 RGBA."""
    out = Image.new("RGBA", (S, S), TRANSPARENT)
    for slot in STACK:
        if slot not in GENERATORS or slot not in traits:
            continue
        fn, _ = GENERATORS[slot]
        out = Image.alpha_composite(out, fn(traits[slot]))
    return out


# ============================================================
# 5. VALIDATION  (run on every layer before shipping)
# ============================================================

def validate(img, slot, option, weight=None):
    """Returns list of error strings. Empty list = layer passes."""
    errs = []
    if img.size != (S, S):
        errs.append(f"{slot}/{option}: wrong size {img.size}, expected {(S, S)}")
    allowed = set(PAL.values())
    gold_vals = {PAL[k] for k in GOLD}
    uses_gold = False
    for y in range(S):
        for x in range(S):
            p = img.getpixel((x, y))
            if p[3] == 0:
                continue
            if p[3] != 255:
                errs.append(f"{slot}/{option}: semi-transparent pixel at {x},{y}")
            if p not in allowed:
                errs.append(f"{slot}/{option}: off-palette color {p} at {x},{y}")
            if p in gold_vals:
                uses_gold = True
    if uses_gold and weight is not None and weight >= 350:
        errs.append(f"{slot}/{option}: uses gold but weight {weight} is too common "
                    f"(gold is reserved for weight < 350)")
    return errs


# ============================================================
# 6. EXPORT
# ============================================================

def export_layers(outdir="layers"):
    manifest = {}
    for slot, (fn, options) in GENERATORS.items():
        os.makedirs(f"{outdir}/{slot}", exist_ok=True)
        manifest[slot] = []
        for opt in options:
            img = fn(opt)
            errs = validate(img, slot, opt)
            if errs:
                for e in errs:
                    print("FAIL", e)
            img.save(f"{outdir}/{slot}/{opt}.png")
            manifest[slot].append(opt)
    with open(f"{outdir}/manifest.json", "w") as f:
        json.dump({"canvas": S, "stack": STACK, "slots": manifest}, f, indent=2)
    return manifest


def export_previews(outdir="preview", scale=10):
    os.makedirs(outdir, exist_ok=True)
    samples = [
        {"ground": "sand",  "wrap": "bone",  "jaw": "wrapped", "eyes": "hollow",  "head": "none"},
        {"ground": "tomb",  "wrap": "linen", "jaw": "slack",   "eyes": "lapis",   "head": "nemes"},
        {"ground": "void",  "wrap": "ash",   "jaw": "grin",    "eyes": "glowing", "head": "circlet"},
        {"ground": "lapis", "wrap": "gold",  "jaw": "gilded",  "eyes": "gold",    "head": "crown"},
    ]
    for i, t in enumerate(samples):
        img = compose(t)
        img.resize((S * scale, S * scale), Image.NEAREST).save(f"{outdir}/sample_{i}.png")


if __name__ == "__main__":
    m = export_layers()
    export_previews()
    total = sum(len(v) for v in m.values())
    print(f"exported {total} layers across {len(m)} slots")
    print("target is 62 layers across 7 slots — see HANDOFF.md section 6")
