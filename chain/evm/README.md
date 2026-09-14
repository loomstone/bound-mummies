# chain/evm — NOT BUILT

Robinhood Chain (Arbitrum stack). Solidity. Foundry or Hardhat.

## Contracts

    BoundNFT.sol        ERC-721, 5000 max, tier index = tokenId
    BoundVault.sol      wrap / unwrap, 200_000 PONS per NFT
    TraitLib.sol        port of canonical/reference.py
    Renderer.sol        optional on-chain SVG tokenURI

## Trait selection

    keccak256(abi.encodePacked("BOUND/v1", uint32(tier)))
    roll = uint32(bytes4(seed[4i:4i+4])) % 10000
    strict > on the cumulative walk

Match `canonical/vectors.json`, then the digest across all 5000 tiers.

## Unresolved

- [ ] PONS token decimals (pump.fun uses 6; if PONS is 18 the raw integer for
      200,000 differs and both sides must agree on display units)
- [ ] RH Chain mainnet chain ID (sources cite 4663; testnet appears to be 46630)

## Build order

- [ ] Port TraitLib, match vectors.json
- [ ] Match the collection digest
- [ ] Vault + NFT, unwrap gated on ERC-721 ownership
- [ ] Adversarial tests
- [ ] Testnet deploy
- [ ] Verify source on the explorer
