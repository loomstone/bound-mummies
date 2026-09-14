"""
BOUND — gold policy validator (amendment GOLD-01 / GOLD-02)

DROP-IN REPLACEMENT for the binary rule in the art pack's validator.

The original rule was:
    gold or gold_sh may only appear in options with weight < 350

That rule was wrong, and it was my error. It tested for the PRESENCE of gold
rather than the AMOUNT, which forced five traits named after gold to contain
none at all: gilded teeth, gold wire, gold eyes, gold-threaded wrap, and gold
leaf. Their names promised something the art did not deliver.

The replacement tests gold QUANTITY against rarity, in three bands:

    trace     1-8 px      any weight        a tooth, a coin, a pupil
    accent    9-40 px     weight <= 500     a wire, a circlet, threading
    dominant  41+ px      weight <= 250     a fully gilded surface

Effect on the five conflicted traits:

    jaw/gilded         800   trace     gets real gold teeth
    bind/gold_wire     450   accent    gets real gold wire
    eyes/gold          350   trace     gets real gold pupils
    wrap/gold_threaded 350   accent    gets real gold threading
    ground/gold        500   dominant  EXCEEDS CAP -> weight amended to 240

Only one weight moves. ground/gold 500 -> 240, and ground/tomb 2100 -> 2360
absorbs the difference so the slot still sums to exactly 10000.

Gold now correlates with rarity more tightly than it did under the binary
rule, because quantity scales with scarcity instead of gold being all-or-
nothing at a single cutoff.

Usage in build.py, replacing the old gold check:

    from gold_policy import check_gold
    errs += check_gold(img, slot, option, weight, PAL)
"""

BANDS = [
    ("trace",    1,    8, 10000),
    ("accent",   9,   40,   500),
    ("dominant", 41, 1024,  250),
]


def gold_pixel_count(img, PAL):
    gold = {PAL["gold"], PAL["gold_sh"]}
    n = 0
    w, h = img.size
    for y in range(h):
        for x in range(w):
            if img.getpixel((x, y)) in gold:
                n += 1
    return n


def band_for(px):
    for name, lo, hi, max_weight in BANDS:
        if lo <= px <= hi:
            return name, max_weight
    return None, None


def check_gold(img, slot, option, weight, PAL):
    """Returns a list of error strings. Empty list means the layer passes."""
    px = gold_pixel_count(img, PAL)
    if px == 0:
        return []

    band, max_weight = band_for(px)
    if band is None:
        return [f"{slot}/{option}: {px} gold pixels exceeds the canvas"]

    if weight > max_weight:
        return [
            f"{slot}/{option}: {px} gold px is band '{band}' "
            f"(cap weight {max_weight}) but weight is {weight}. "
            f"Either reduce gold below {BANDS[[b[0] for b in BANDS].index(band)-1][2] if band != 'trace' else 0} px "
            f"or lower the weight to {max_weight}."
        ]
    return []


def audit(layers_dir, traits_cfg, PAL, Image):
    """
    Audit an entire layers/ directory. Returns (errors, report_rows).
    report_rows: (slot, option, weight, gold_px, band, ok)
    """
    import os
    errors, rows = [], []
    for slot, opts in traits_cfg["slots"].items():
        for option, weight in opts:
            path = os.path.join(layers_dir, slot, option + ".png")
            if not os.path.exists(path):
                errors.append(f"{slot}/{option}: layer file missing at {path}")
                continue
            img = Image.open(path).convert("RGBA")
            px = gold_pixel_count(img, PAL)
            band, _ = band_for(px) if px else ("none", None)
            errs = check_gold(img, slot, option, weight, PAL)
            errors += errs
            if px:
                rows.append((slot, option, weight, px, band, not errs))
    rows.sort(key=lambda r: -r[3])
    return errors, rows


if __name__ == "__main__":
    import json
    import os
    import sys
    from PIL import Image

    here = os.path.dirname(os.path.abspath(__file__))
    cfg = json.load(open(os.path.join(here, "traits.json")))

    layers = sys.argv[1] if len(sys.argv) > 1 else "layers"
    proto = sys.argv[2] if len(sys.argv) > 2 else "prototype.py"


    sys.path.insert(0, os.path.dirname(os.path.abspath(proto)) or ".")
    from prototype import PAL

    errs, rows = audit(layers, cfg, PAL, Image)

    print(f"{'slot':8} {'option':18} {'weight':>7} {'goldpx':>7} {'band':10} ok")
    for slot, option, weight, px, band, ok in rows:
        print(f"{slot:8} {option:18} {weight:>7} {px:>7} {band:10} {'yes' if ok else 'NO'}")
    print()
    if errs:
        print(f"{len(errs)} FAILURES")
        for e in errs:
            print("  -", e)
        sys.exit(1)
    print("gold policy: pass")
