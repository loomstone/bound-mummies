# BOUND — v2 spec: cross-chain swap venue

**Status: designed, not built. Deliberately deferred.**

This exists so the design is on paper and out of your head. Nothing in v1
forecloses it. Do not build this before the collection ships and manual tier
migration is observed happening.

---

## 1. What it does

Lets a holder of a Robinhood Chain BOUND NFT trade directly with a holder of a
Solana BOUND NFT, or sell to someone paying in SOL, without a bridge, an
oracle, or protocol-held inventory.

Both cases use the same primitive. A hashed timelock does not care whether the
other leg is an NFT or a currency — it only needs both legs lockable.

---

## 2. Why it survives when the other cross-chain ideas didn't

Three earlier designs were rejected:

- **Cross-chain unwrap** — structurally impossible. Burning a claim on 200,000
  PONS cannot pay out 200,000 pump tokens; the Solana side has nothing to pay
  with and the PONS vault is orphaned.
- **Swap desk with protocol inventory** — requires a bridge or a 7-day
  Arbitrum fraud-proof window, plus an oracle, and Twine's 5% peg band means
  bots drain the inventory at 1:1 redemption.
- **Cross-chain NFT movement** — contradicts the premise. Mirrored twins
  requires that nothing moves; migratable uniques requires that tiers are not
  mirrored. You cannot have both.

This design touches none of those. **Nothing crosses chains.** Solana #42 stays
on Solana, PONS #42 stays on Robinhood Chain, both keep existing, the pair stays
intact. Only ownership of each side changes.

---

## 3. Mechanism — hashed timelock

No bridge. The secret crosses chains by being published in public.

```
1. Alice generates secret S, publishes H = keccak256(S)
2. Alice locks her Solana NFT:
       claimable by Bob if he reveals S
       refundable to Alice after timeout T1
3. Bob locks his PONS NFT against the same H:
       claimable by Alice if she reveals S
       refundable to Bob after timeout T2,  where T2 < T1
4. Alice claims on Robinhood Chain -> this PUBLISHES S on-chain
5. Bob reads S from that transaction, claims on Solana
```

Either both legs complete or both refund. `T2 < T1` is mandatory: it guarantees
Bob's refund window opens before Alice's, so Alice can never claim Bob's side
after Bob has already refunded.

Both chains support keccak256 natively, so the hash lock is identical on each.

---

## 4. Pricing is nearly solved for free

This is the strongest property and it falls out of the wrap design.

Every NFT on either chain is backed by exactly 200,000 tokens. Twine holds the
two token market caps within 5% of each other. Therefore **any Solana BOUND is
within ~5% of any PONS BOUND in intrinsic value**, automatically, with no
appraisal.

In ordinary barter, valuation is the hard part. Here the floor is identical by
construction, and only the rarity premium is negotiable — a much smaller and
more tractable spread.

**Keep price agreement per-swap and user-determined.** The moment the protocol
tries to enforce "similar price," it needs a rarity price feed, which is an
oracle, which is a trust assumption this design otherwise avoids.

---

## 5. Order flow and the three rules

The venue needs open orders, browsing per chain, filtering, and expiry.

Three rules, all sound:

1. **24-hour offer expiry.** No response within 24h is a decline. Bounds how
   long locked capital can be held hostage.
2. **Void on first acceptance.** If the requester's offer is accepted by someone
   else first, all their other outstanding offers void. Without this, one person
   locks up ten listers with parallel offers and picks whichever moves most in
   their favor.
3. **Rarity-adjusted matching.** Surface listings closest in value to the
   connected wallet's NFT. Display-layer only, never enforced on-chain.

---

## 6. Escrow timing — decision required

| | Lock on listing | Lock on acceptance |
|---|---|---|
| Matching reliability | high | acceptances can fail |
| Pool depth | very low | much higher |
| Asset frozen | indefinitely | only during the swap |

**Lock on acceptance is correct.** An empty pool is fatal; a failed acceptance
is merely annoying. But the UI must be honest that a listing is an intent, not
a guarantee — the lister may have sold elsewhere or gone quiet.

---

## 7. Known unsolved problems

**The free option.** Whoever locks second holds a 24-hour option on a spread of
up to 5% and can simply not complete, leaving the other party's asset frozen for
a day. The 24h expiry bounds this but does not remove it. Mitigation is a SOL/ETH
bond posted by the requester and forfeited on non-completion — more contract
surface. Skip it in a first version; bounded is probably enough at this scale.

**Both parties must stay engaged** through a multi-step timelocked flow across
two wallet types on two chains. This is precisely why atomic swaps have existed
for a decade and almost nobody uses them. The mechanism was never the blocker.
The UX was.

**It competes with just selling.** Anyone willing to trade at market price can
list on OpenSea and buy on Magic Eden instead — two ordinary transactions on
infrastructure that already works. This design only wins for people who
specifically want barter.

**"Listed" must mean listed here.** Marketplace listings on OpenSea or Magic Eden
are signed orders only that marketplace's contract can fill, for its own
currency. This venue can read them but cannot execute against them. Surfacing
matches it cannot complete is worse than surfacing nothing.

---

## 8. Scope, honestly

Two more contracts holding user assets, a timelock state machine, an order book,
and a matching interface, across Anchor/Rust and Solidity. **This is larger than
the collection itself.**

---

## 9. The cheap test that precedes building any of it

Tier migration already works today with zero new code:

1. Unwrap tier #42 on Robinhood Chain, receive 200,000 PONS
2. Sell PONS, buy pump on open markets
3. Wrap tier #42 on Solana, receive the identical character back

The art is tier-seeded, so the same individual reappears on the other chain.
Twine's peg makes the rate roughly 1:1 already.

**Instrument this.** Count how often a tier is unwrapped on one chain and
re-wrapped on the other within a short window. That number is the demand signal.

- If it is meaningful, build this venue with evidence behind it.
- If it is near zero, you saved yourself two audited contracts.

One gap worth noting: during migration the tier is briefly unclaimed on both
chains and can be sniped. This venue would close that gap. Whether that alone
justifies the build is exactly what the measurement answers.

---

## 10. Prerequisites before any of this starts

- [ ] Collection live on both chains, wrap/unwrap proven stable
- [ ] Migration instrumented and the demand signal captured
- [ ] v1 contracts audited and, ideally, upgrade authority revoked
- [ ] Decision on escrow timing (section 6)
- [ ] Decision on the completion bond (section 7)
