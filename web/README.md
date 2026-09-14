# web — NOT BUILT

See `spec/website-brief.md` for the full requirements brief (written for a
designer, no crypto assumed).

## The constraint that shapes everything

Two chains means two wallet types connected at once — Solana (Phantom,
Solflare) and EVM (MetaMask, Rainbow). Users arrive with one, both, or none.
All three states must work.

## Screens

- [ ] Home
- [ ] Wrap (connect -> balance -> choose tier -> confirm -> pending -> success)
- [ ] Unwrap
- [ ] Collection browser — 5000 items per chain, needs virtualization
- [ ] Tier detail — BOTH chains side by side, the signature screen
- [ ] Stats (wrapped per chain, tokens locked, complete pairs)
- [ ] How it works / Technical / FAQ
- [ ] System status (per chain — one side can be down while the other is fine)

## Copy correctness

`spec/website-brief.md` section 5 lists claims the site must NOT make. They are
correctness constraints, not tone preferences.
