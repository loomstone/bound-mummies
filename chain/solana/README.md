# chain/solana — NOT BUILT

Anchor program. Rust.

## Instructions

    wrap(tier_index)
        reject if tier < 1 or > 5000
        reject if tier already claimed
        reject if caller balance < 200_000 tokens
        move 200_000 tokens -> vault ATA, authority PDA(["vault", nft_mint])
        mint Metaplex NFT to caller
        mark tier claimed

    unwrap(tier_index)
        verify caller's ATA holds the NFT for this tier
        drain vault -> caller
        burn NFT
        return tier to unclaimed

## The one check that matters

The unwrap authority check. A flaw there drains every vault in the collection.
Everything else is secondary.

## Trait selection

Port `canonical/reference.py` exactly. Match every vector in
`canonical/vectors.json`, then match the digest across all 5000 tiers.

    keccak::hash()              not sha3
    (tier as u32).to_be_bytes() big-endian
    strict > on the cumulative walk

## Build order

- [ ] Port trait selection, match vectors.json
- [ ] Match the collection digest across all 5000
- [ ] wrap / unwrap instructions
- [ ] Adversarial tests (see /tools/adversarial-checklist.md)
- [ ] Devnet deploy
- [ ] Revoke upgrade authority before mainnet, or publicly state you have not
