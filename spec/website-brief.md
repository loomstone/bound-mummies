# Website Brief — Dual-Chain Wrapped NFT Collection

**Status:** design not started. Project name, subject matter, and artwork are not finalized. Build around placeholders for those.

---

## 1. What the project is

A token launches simultaneously on two blockchains through a launchpad called Twine — one version on Solana (via pump.fun), one on Robinhood Chain (via PONS). Each has a supply of 1,000,000,000 tokens. The two tokens are separate and cannot be moved between chains.

On top of each token, we deploy a "wrap" mechanic:

- A holder locks **200,000 tokens** and receives **1 NFT** in return.
- The NFT can be sold or transferred normally on NFT marketplaces.
- Whoever holds the NFT can "unwrap" it at any time: the NFT is burned and the 200,000 tokens are released to them.

Each chain supports **5,000 NFTs**, numbered 1 to 5,000. The same numbers exist on both chains, so there are **10,000 NFTs total** and **5,000 twin pairs**.

**The core concept:** NFT #42 on Solana and NFT #42 on Robinhood Chain are visually identical, down to the pixel. The artwork is generated mathematically from the number itself, so two blockchains that have no connection to each other independently produce the same image. Owning both halves of a pair is the collecting goal.

Users pick which number they want when wrapping — first come, first served, from whatever is unclaimed.

---

## 2. The defining constraint: two chains, two wallets

This is the biggest thing separating this site from a normal NFT site, and it affects nearly every screen.

- Solana requires a Solana wallet (Phantom, Solflare).
- Robinhood Chain requires an Ethereum-compatible wallet (MetaMask, Rainbow).
- These are different wallet types. A user doing both sides connects two wallets at once.
- Every screen that shows data or takes an action is scoped to one chain at a time, **except** the pair view (see below).
- Users will arrive with one wallet, both wallets, or none. All three states need to work.
- Users on the Ethereum-compatible side may be connected to the wrong network and need to be prompted to switch to Robinhood Chain.

---

## 3. Pages and screens required

### Home
Explains the concept to someone who has never heard of it. Needs to convey the token-into-NFT mechanic and the twin concept quickly. Entry points into wrapping and browsing.

### Wrap
The primary action. Flow:
1. Connect wallet (or prompt to connect)
2. Show the user's token balance and how many NFTs that balance allows
3. Let the user choose an available number
4. Confirm and sign the transaction
5. Pending state
6. Success — show the NFT they just received

Error and edge states that must be designed:
- Wallet not connected
- Insufficient balance (needs 200,000)
- Wrong network (Robinhood Chain side only)
- The number was claimed by someone else while the user was deciding
- Transaction rejected in wallet
- Transaction failed on chain

### Unwrap
Reverse action. Shows the NFTs the connected wallet currently holds. Selecting one and confirming burns it and returns 200,000 tokens. Needs a clear warning that this is irreversible and the NFT is destroyed. Same pending/success/error states as wrap.

### Collection browser
All 5,000 numbers for the selected chain. Each number is in one of two states: **claimed** (someone holds it) or **available** (can be wrapped right now). Needs to handle 5,000 items without becoming unusable — pagination, virtualization, or lazy loading is a technical requirement, not a style choice.

Users need to find specific numbers, so search by number is required. Filtering by availability and by traits should be assumed.

### Individual NFT page
The signature screen of the site. For any number, it shows **both chains side by side**: the Solana version and the Robinhood Chain version, which are identical images. Per side it needs to show whether it is currently wrapped, who holds it, and a link to the relevant marketplace listing.

A pair can be in four states, and all four need a visual treatment:
- Wrapped on both chains (complete pair)
- Wrapped on Solana only
- Wrapped on Robinhood Chain only
- Unwrapped on both (fully available)

### Stats
Total wrapped per chain, tokens currently locked, percentage of supply removed from circulation, and how many complete pairs exist. This updates as people wrap and unwrap.

### Explainer pages
- **How it works** — plain-language walkthrough of wrapping and unwrapping
- **Technical** — the detailed mechanism, contract addresses, and how the identical-artwork guarantee is verified
- **FAQ**

### System status
Whether the contracts are live on each chain, and whether wrapping is currently paused. Two chains means one side can be having problems while the other is fine, and the site must be able to say so.

---

## 4. Data the site consumes

To be provided by the backend. The designer should assume these exist:

- Live claimed/available state for all 5,000 numbers, per chain
- Current holder address per wrapped NFT
- Artwork image per number, served from an image endpoint
- Trait list per number
- Aggregate stats (total wrapped, tokens locked, pairs complete)
- Contract/program status per chain

Note that state changes without the user acting — someone else can claim a number while they are looking at it. Screens showing availability need to account for going stale.

---

## 5. Copy accuracy requirements

These are correctness constraints, not style preferences. The site must not claim any of the following, because none of them are true:

- That NFTs or tokens move between the two chains. They do not. There is no bridge.
- That an NFT can be wrapped on one chain and unwrapped on the other. It cannot.
- That the two chains communicate or are synchronized by any mechanism. They are not. The images match because both chains run the same math on the same number.
- That wrapping earns yield, rewards, staking returns, or any form of passive income. Locked tokens sit inert.

The word "synced" is being used to describe matching artwork, not a technical link between chains. Copy should not imply otherwise.

---

## 6. Placeholders required

Not yet decided, so the design needs to accommodate these being filled in later:

- **Project name and logo**
- **Subject matter** — what the characters or objects actually are
- **Artwork** — none exists yet; assume square pixel-art-style images
- **Trait categories** — expect roughly 5 to 9 categories, names unknown
- **Contract addresses** — not deployed yet

---

## 7. Out of scope

- The NFT marketplace itself. Trading happens on existing marketplaces (Magic Eden and Tensor on Solana; OpenSea, Element, or RhinoMarket on Robinhood Chain). The site links out.
- Token trading. That happens on pump.fun, Axiom, GMGN, and PONS.
- Artwork generation. That is handled by the smart contracts and the image endpoint.

---

## 8. Questions for the designer to raise

- Mobile behavior for the side-by-side pair view, where two images plus two sets of state need to fit
- How to present dual wallet connection without it feeling like an obstacle on arrival
- How the 5,000-item browser should behave on mobile
