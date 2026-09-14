# Adversarial test set — both chains must pass all

Run on testnet before any mainnet deploy.

- [ ] unwrap called by someone who does not hold the NFT — must fail
- [ ] unwrap after the NFT has been transferred — only the NEW holder succeeds
- [ ] wrap a tier that is already claimed — must fail
- [ ] wrap with balance below 200,000 — must fail
- [ ] wrap tier 0 — must fail
- [ ] wrap tier 5001 — must fail
- [ ] double-wrap in the same transaction — must fail
- [ ] unwrap twice — second must fail
- [ ] wrap, unwrap, re-wrap the same tier — identical art returns
- [ ] vault balance is exactly 200,000 after wrap, exactly 0 after unwrap
- [ ] tier returns to unclaimed after unwrap and can be re-claimed by anyone
- [ ] pause (if implemented) NEVER blocks unwrap
- [ ] reentrancy on unwrap (EVM side)
