.PHONY: help setup verify canonical art rust evm clean

help:
	@echo "make setup     install python deps"
	@echo "make verify    run everything that exists (this is the gate)"
	@echo "make canonical reference implementation self-tests + digest"
	@echo "make art       regenerate all 62 layers and validate"
	@echo "make rust      solana trait selection tests"
	@echo "make evm       evm trait selection tests (not built yet)"

setup:
	pip install -r requirements.txt

verify: canonical rust art
	@echo ""
	@echo "=== all implemented components pass ==="
	@echo "not yet built: renderer, solana program, evm contracts, web"

canonical:
	@echo "--- canonical reference ---"
	cd canonical && python3 reference.py

art:
	@echo "--- art layers ---"
	cd art && python3 build.py >/dev/null && python3 ../canonical/gold_policy.py layers

rust:
	@echo "--- solana trait selection ---"
	cd chain/solana/bound-traits && cargo test

evm:
	@echo "--- evm trait selection ---"
	@if [ -f chain/evm/foundry.toml ]; then cd chain/evm && forge test; \
	else echo "not built yet — see chain/evm/PHASE1-BRIEF.md"; fi

clean:
	find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
	rm -rf chain/solana/bound-traits/target
