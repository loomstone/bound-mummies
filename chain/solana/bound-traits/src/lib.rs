//! BOUND / Wrapped Mummies — trait selection (Solana side)
//!
//! This is an INDEPENDENT implementation of `canonical/reference.py`.
//! It was written from the spec, not ported line-by-line, so that agreement
//! between the two is evidence the spec is unambiguous rather than evidence
//! that one was copied.
//!
//! It must reproduce, exactly:
//!   - every vector in canonical/vectors.json
//!   - the collection digest
//!     0beebbb2d7f6cee419091692001ec6c15ae46070f7bd5459d761407964aee33b
//!
//! ON-CHAIN NOTE
//! Inside an Anchor program, replace `keccak256` below with
//! `solana_program::keccak::hash(data).to_bytes()`. It is the same function;
//! tiny-keccak is used here only so this crate builds standalone.
//!
//! INVARIANTS — changing any of these breaks cross-chain parity:
//!   - keccak256, NOT sha3-256 (different padding, different output)
//!   - tier encoded as u32 big-endian, 4 bytes
//!   - TAG is raw ASCII "BOUND/v1", no length prefix, no null terminator
//!   - slot order: wrap, head, eyes, jaw, bind, charm, ground
//!   - roll = u32 big-endian from seed[4i..4i+4], then % 10000
//!   - cumulative walk uses STRICT `>`; `>=` shifts every boundary by one
//!   - tiers are 1-indexed, valid range 1..=5000

#![allow(clippy::needless_range_loop)]

use tiny_keccak::{Hasher, Keccak};

pub const TAG: &[u8] = b"BOUND/v1";
pub const TIERS: u32 = 5000;
pub const SLOT_COUNT: usize = 7;
pub const WEIGHT_TOTAL: u32 = 10_000;

/// Slot order. This is the order seed bytes are consumed in, and is NOT the
/// same as the art stack order (ground, wrap, bind, jaw, eyes, head, charm).
pub const SLOT_NAMES: [&str; SLOT_COUNT] =
    ["wrap", "head", "eyes", "jaw", "bind", "charm", "ground"];

/// Option names and weights, in DECLARED ORDER. Order is load-bearing: the
/// cumulative walk depends on it, and the serialized digest uses option index.
pub const WRAP: [(&str, u32); 10] = [
    ("bone", 2600), ("ash", 2000), ("linen", 1700), ("stained", 1200),
    ("lapis", 900), ("verdigris", 600), ("bitumen", 450), ("gold_threaded", 350),
    ("unraveling", 150), ("alabaster", 50),
];

pub const HEAD: [(&str, u32); 10] = [
    ("none", 3000), ("nemes", 2200), ("cap", 1500), ("circlet", 1100),
    ("jackal_mask", 800), ("falcon_mask", 600), ("crown", 400),
    ("horned_crown", 250), ("sun_disk", 100), ("gold_crown", 50),
];

pub const EYES: [(&str, u32); 9] = [
    ("hollow", 2800), ("painted", 2400), ("lapis", 1600), ("closed", 1200),
    ("glowing", 900), ("cracked", 550), ("gold", 350), ("twin_pupils", 150),
    ("void", 50),
];

pub const JAW: [(&str, u32); 7] = [
    ("wrapped", 3400), ("slack", 2300), ("grin", 1700), ("snarl", 1200),
    ("gilded", 800), ("scarab_in_mouth", 450), ("coin_in_mouth", 150),
];

pub const BIND: [(&str, u32); 8] = [
    ("none", 3500), ("cord", 2400), ("leather_strap", 1600), ("chain", 1100),
    ("seal", 700), ("gold_wire", 450), ("broken_chain", 200),
    ("thread_of_light", 50),
];

pub const CHARM: [(&str, u32); 9] = [
    ("none", 3600), ("scarab", 2200), ("ankh", 1500), ("eye_amulet", 1100),
    ("coin", 800), ("vial", 400), ("key", 250), ("paired_scarabs", 120),
    ("hourglass", 30),
];

/// ground/gold is 240, not 500 — amendment GOLD-01. Fully gilded backgrounds
/// are dominant-band gold and capped at weight 250. ground/tomb absorbed the
/// freed 260 (2100 -> 2360) so the slot still sums to 10000.
pub const GROUND: [(&str, u32); 9] = [
    ("sand", 2600), ("tomb", 2360), ("lapis", 1600), ("torchlit", 1200),
    ("night_sky", 900), ("flood", 700), ("void", 300), ("gold", 240),
    ("eclipse", 100),
];

pub fn slot_options(slot: usize) -> &'static [(&'static str, u32)] {
    match slot {
        0 => &WRAP,
        1 => &HEAD,
        2 => &EYES,
        3 => &JAW,
        4 => &BIND,
        5 => &CHARM,
        6 => &GROUND,
        _ => panic!("slot index out of range"),
    }
}

#[derive(Debug, PartialEq, Eq)]
pub enum TraitError {
    TierOutOfRange(u32),
}

/// Swap for `solana_program::keccak::hash(data).to_bytes()` on-chain.
pub fn keccak256(data: &[u8]) -> [u8; 32] {
    let mut h = Keccak::v256();
    let mut out = [0u8; 32];
    h.update(data);
    h.finalize(&mut out);
    out
}

pub fn seed_for(tier: u32) -> Result<[u8; 32], TraitError> {
    if tier == 0 || tier > TIERS {
        return Err(TraitError::TierOutOfRange(tier));
    }
    let mut buf = [0u8; 12];
    buf[..8].copy_from_slice(TAG);
    buf[8..].copy_from_slice(&tier.to_be_bytes()); // u32 big-endian
    Ok(keccak256(&buf))
}

/// Cumulative walk, STRICT `>`. Returns the index of the winning option.
fn pick(options: &[(&str, u32)], roll: u32) -> usize {
    let mut cumulative: u32 = 0;
    for (i, (_, weight)) in options.iter().enumerate() {
        cumulative += weight;
        if cumulative > roll {
            return i;
        }
    }
    unreachable!("weights must sum to 10000 and roll must be < 10000");
}

/// The canonical function. Returns one option INDEX per slot, in slot order.
pub fn traits_for(tier: u32) -> Result<[u8; SLOT_COUNT], TraitError> {
    let seed = seed_for(tier)?;
    let mut out = [0u8; SLOT_COUNT];
    for slot in 0..SLOT_COUNT {
        let mut word = [0u8; 4];
        word.copy_from_slice(&seed[slot * 4..slot * 4 + 4]);
        let roll = u32::from_be_bytes(word) % WEIGHT_TOTAL;
        out[slot] = pick(slot_options(slot), roll) as u8;
    }
    Ok(out)
}

pub fn trait_names(tier: u32) -> Result<[&'static str; SLOT_COUNT], TraitError> {
    let idx = traits_for(tier)?;
    let mut out = [""; SLOT_COUNT];
    for slot in 0..SLOT_COUNT {
        out[slot] = slot_options(slot)[idx[slot] as usize].0;
    }
    Ok(out)
}

pub fn weight_of(tier: u32, slot: usize) -> Result<u32, TraitError> {
    let idx = traits_for(tier)?;
    Ok(slot_options(slot)[idx[slot] as usize].1)
}

/// Canonical serialization: u32_be(tier) then one byte per slot (option index).
pub fn serialize(tier: u32) -> Result<[u8; 4 + SLOT_COUNT], TraitError> {
    let idx = traits_for(tier)?;
    let mut buf = [0u8; 4 + SLOT_COUNT];
    buf[..4].copy_from_slice(&tier.to_be_bytes());
    buf[4..].copy_from_slice(&idx);
    Ok(buf)
}

/// The cross-chain proof artifact. Hash of every tier's serialization, in order.
pub fn collection_digest() -> [u8; 32] {
    let mut h = Keccak::v256();
    for tier in 1..=TIERS {
        let s = serialize(tier).expect("tier in range");
        h.update(&s);
    }
    let mut out = [0u8; 32];
    h.finalize(&mut out);
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    /// If this fails, the hash function is wrong — most likely sha3-256.
    #[test]
    fn keccak_is_keccak_not_sha3() {
        assert_eq!(
            hex::encode(keccak256(b"")),
            "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"
        );
    }

    #[test]
    fn every_slot_sums_to_ten_thousand() {
        for slot in 0..SLOT_COUNT {
            let total: u32 = slot_options(slot).iter().map(|(_, w)| w).sum();
            assert_eq!(total, WEIGHT_TOTAL, "slot {} sums to {}", SLOT_NAMES[slot], total);
        }
    }

    #[test]
    fn gold_amendment_applied() {
        let g = GROUND.iter().find(|(n, _)| *n == "gold").unwrap().1;
        assert_eq!(g, 240, "GOLD-01 not applied");
        let t = GROUND.iter().find(|(n, _)| *n == "tomb").unwrap().1;
        assert_eq!(t, 2360, "GOLD-02 not applied");
    }

    #[test]
    fn rejects_out_of_range_tiers() {
        assert!(seed_for(0).is_err());
        assert!(seed_for(TIERS + 1).is_err());
        assert!(seed_for(u32::MAX).is_err());
        assert!(seed_for(1).is_ok());
        assert!(seed_for(TIERS).is_ok());
    }

    #[test]
    fn deterministic() {
        for t in [1u32, 42, 2500, 5000] {
            assert_eq!(traits_for(t).unwrap(), traits_for(t).unwrap());
        }
    }

    /// Vectors from canonical/vectors.json — generated by reference.py.
    #[test]
    fn matches_reference_vectors() {
        let cases: [(u32, &str, [&str; 7]); 12] = [
            (1, "7b16508aafbb1aba",
             ["alabaster", "nemes", "void", "snarl", "cord", "scarab", "sand"]),
            (2, "ad9fc6fb2292cc3f",
             ["gold_threaded", "cap", "hollow", "snarl", "cord", "eye_amulet", "lapis"]),
            (3, "867134e729c626a7",
             ["linen", "none", "twin_pupils", "grin", "leather_strap", "scarab", "lapis"]),
            (42, "194d278718290a5d",
             ["stained", "none", "lapis", "wrapped", "cord", "none", "sand"]),
            (100, "1ba51000e619bef5",
             ["bone", "circlet", "closed", "grin", "cord", "scarab", "sand"]),
            (777, "e74f7e8405050a43",
             ["stained", "cap", "hollow", "wrapped", "none", "vial", "flood"]),
            (1234, "b4de6f6adc7e1734",
             ["stained", "none", "lapis", "gilded", "none", "coin", "tomb"]),
            (2500, "ad470c7026dfc898",
             ["linen", "none", "lapis", "grin", "leather_strap", "coin", "night_sky"]),
            (3333, "a1be23cd6e11c618",
             ["ash", "jackal_mask", "painted", "wrapped", "none", "scarab", "tomb"]),
            (4271, "552488e0afa3f783",
             ["lapis", "jackal_mask", "closed", "slack", "cord", "paired_scarabs", "flood"]),
            (4999, "83545ffed28cf6c5",
             ["linen", "nemes", "hollow", "grin", "broken_chain", "vial", "sand"]),
            (5000, "f09db8666cd51ea1",
             ["lapis", "cap", "hollow", "snarl", "seal", "scarab", "torchlit"]),
        ];
        for (tier, seed_prefix, expected) in cases {
            let seed = seed_for(tier).unwrap();
            assert_eq!(
                hex::encode(&seed[..8]),
                seed_prefix,
                "seed mismatch at tier {} — check TAG bytes and u32 endianness",
                tier
            );
            assert_eq!(
                trait_names(tier).unwrap(),
                expected,
                "trait mismatch at tier {} — check slot order and the cumulative walk",
                tier
            );
        }
    }

    /// The gate. Three implementations must produce this.
    #[test]
    fn collection_digest_matches() {
        assert_eq!(
            hex::encode(collection_digest()),
            "0beebbb2d7f6cee419091692001ec6c15ae46070f7bd5459d761407964aee33b"
        );
    }

    /// Observed counts should track weight/2 across 5000 tiers.
    #[test]
    fn distribution_tracks_weights() {
        let mut counts = [[0u32; 10]; SLOT_COUNT];
        for tier in 1..=TIERS {
            let idx = traits_for(tier).unwrap();
            for slot in 0..SLOT_COUNT {
                counts[slot][idx[slot] as usize] += 1;
            }
        }
        for slot in 0..SLOT_COUNT {
            for (i, (name, w)) in slot_options(slot).iter().enumerate() {
                let expected = *w as f64 / 2.0;
                let got = counts[slot][i] as f64;
                let tol = (4.0 * expected.sqrt()).max(5.0);
                assert!(
                    (got - expected).abs() <= tol,
                    "{}/{}: expected ~{:.0}, got {}",
                    SLOT_NAMES[slot], name, expected, got
                );
            }
        }
    }
}
