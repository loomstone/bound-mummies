# tools — PARTIALLY BUILT

- [ ] `verify_digest.py` — pull trait sets from live Solana + RH Chain
      contracts, recompute both digests, compare against
      `canonical/vectors.json`. This is the launch-day proof.
- [ ] `adversarial-checklist.md` — the test set both chains must pass
- [ ] `migration_watch.py` — count tiers unwrapped on one chain and re-wrapped
      on the other within a short window. This is the demand signal that
      decides whether the v2 swap venue gets built at all.
