# Problem Statement — Cross-Chain Unwrapping

A request for a second opinion. Stated as neutrally as possible so the reader can reach their own conclusion.

---

## 1. The system

A memecoin launches simultaneously on two chains via a launchpad called Twine:

- **Solana side** — a pump.fun token, 1,000,000,000 supply
- **Robinhood Chain side** — a PONS token, 1,000,000,000 supply (RH Chain is an Arbitrum-stack Ethereum L2)

The two tokens are entirely separate. There is no bridge and no message passing between them. They are linked only by an off-chain market maker operated by Twine, which holds inventory on both chains and sells whichever side runs more than 5% ahead, keeping the two market caps within a 5% band of each other.

On top of each token we are deploying a wrap layer, modeled on WrappedBulls:

- Lock 200,000 tokens → receive 1 NFT
- 5,000 numbered NFTs per chain (1–5,000), same numbers on both chains, 10,000 total
- Artwork is derived deterministically from the tier number via `keccak256`, so NFT #42 renders pixel-identically on both chains despite the chains having no connection
- The NFT holder can unwrap at any time: NFT burns, 200,000 tokens release
- Users choose their own tier number, first come first served

The artwork identity is a mathematical guarantee, not a synchronization mechanism.

---

## 2. The question

**Can a user wrap on Robinhood Chain and unwrap on Solana (or vice versa), autonomously and safely?**

Motivation: novel mechanics drive attention and interest in this market. A working cross-chain wrap/unwrap would be a genuinely differentiated feature.

---

## 3. Why it isn't a redemption

Wrapping on RH Chain locks 200,000 **PONS tokens** in a vault on RH Chain. Unwrapping on Solana would have to pay out 200,000 **pump.fun tokens** — a different asset on a different chain.

Two consequences:

1. The Solana program has no pump tokens to pay out unless inventory is pre-funded by the protocol.
2. The PONS in the RH Chain vault becomes stranded, with its NFT burned on the other chain and no one able to retrieve it.

So the mechanic is structurally a **cross-chain swap backed by protocol inventory**, not a redemption. Any design has to solve for that.

---

## 4. The four sub-problems

### 4.1 Proving the burn

Solana must learn that the RH Chain burn occurred. Options:

| Approach | Latency | Trust introduced |
|---|---|---|
| Messaging protocol (LayerZero, Wormhole, Hyperlane) | minutes | the protocol's validator set |
| Trustless light-client proof | ~7 days | none |
| Self-operated relayer | seconds | fully centralized on us |

The 7-day figure is the Arbitrum-stack fraud-proof challenge window and is not optimizable. Trustless means slow; fast means trusted.

Cross-chain messaging has also been the site of the largest exploits in the sector (Wormhole, Nomad, Ronin), which is a relevant base rate.

### 4.2 Arbitrage against the inventory

Twine's peg permits up to 5% divergence between the two market caps.

If redemption is 1:1, then any time the spread is wide, a bot can burn the cheaper side and withdraw the more expensive side from protocol inventory at a profit. This is repeatable, automatable, and continues until inventory is exhausted. The allocation becomes exit liquidity for whichever chain the market currently disfavors.

Mitigating this requires pricing redemptions against the live spread, which requires a price oracle — a second trust assumption and a second attack surface.

### 4.3 Inventory management

Flow will not be symmetric. If most users migrate in one direction, that side's inventory drains while the other accumulates. Rebalancing means selling one token and buying the other, at size, on an ongoing basis.

This is the same job Twine's market maker already performs, and it carries directional exposure.

### 4.4 Marginal benefit

A path already exists today with no new code:

1. Unwrap tier #42 on RH Chain → receive 200,000 PONS
2. Sell PONS, buy pump on open markets
3. Wrap tier #42 on Solana → receive the identical NFT back

Because the artwork is seeded from the tier number, the user's specific individual reappears on the other chain. Because Twine pegs the two tokens within 5%, the exchange rate is already approximately 1:1.

The cross-chain unwrap therefore saves the user two swaps and some slippage.

(Note: this existing path has a gap — after unwrapping, the tier is briefly unclaimed on both chains and could be sniped by someone else before the user re-wraps. Cross-chain unwrapping would close that gap. Whether that alone justifies the machinery is part of the question.)

---

## 5. Alternative under consideration

A **guided migration flow**: a UI that walks the user through unwrap → swap → re-wrap as a single tracked sequence. Non-custodial, no protocol inventory, no bridge, no oracle. Delivers the migration experience without introducing new trust assumptions. Does not close the sniping gap in 4.4.

---

## 6. What a useful answer would address

- Is there a design that avoids both a trusted messaging layer and a 7-day delay?
- Can the 5% arbitrage window be closed without introducing an oracle?
- Is there a structure where inventory is user-supplied rather than protocol-supplied — e.g. a two-sided pool, or matching users migrating in opposite directions against each other?
- Is the marginal benefit over the existing swap path large enough to justify the added surface?
- Counter-consideration worth weighing: the project's stated premise is that the two chains do not communicate. Does adding a bridge undermine the thesis, or is the thesis about artwork determinism only, leaving asset movement as a separate matter?

---

## 7. Constraints

- Two separate codebases: Anchor/Rust on Solana, Solidity on Robinhood Chain
- Neither token contract is modifiable; both are already deployed by their respective launchpads
- The wrap layer holds user funds, so a flaw in the unlock path drains every vault
- The team is small and the project is pre-launch
