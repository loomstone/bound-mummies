// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @notice Canonical BOUND tier-to-trait selection.
/// @dev Option indices follow the declared order in canonical/traits.json.
library TraitLib {
    uint32 internal constant MAX_TIER = 5_000;
    bytes8 internal constant TAG = "BOUND/v1";

    error InvalidTier(uint32 tier);
    error InvalidSlot(uint8 slot);
    error InvalidOption(uint8 slot, uint8 option);

    struct Traits {
        uint8 wrap;
        uint8 head;
        uint8 eyes;
        uint8 jaw;
        uint8 bind;
        uint8 charm;
        uint8 ground;
    }

    function seedFor(uint32 tier) internal pure returns (bytes32) {
        _validateTier(tier);
        return keccak256(abi.encodePacked(TAG, tier));
    }

    function traitsFor(uint32 tier) internal pure returns (Traits memory traits) {
        bytes32 seed = seedFor(tier);
        traits.wrap = _pick(0, _roll(seed, 0));
        traits.head = _pick(1, _roll(seed, 1));
        traits.eyes = _pick(2, _roll(seed, 2));
        traits.jaw = _pick(3, _roll(seed, 3));
        traits.bind = _pick(4, _roll(seed, 4));
        traits.charm = _pick(5, _roll(seed, 5));
        traits.ground = _pick(6, _roll(seed, 6));
    }

    function serialize(uint32 tier) internal pure returns (bytes memory) {
        Traits memory traits = traitsFor(tier);
        return abi.encodePacked(
            tier,
            traits.wrap,
            traits.head,
            traits.eyes,
            traits.jaw,
            traits.bind,
            traits.charm,
            traits.ground
        );
    }

    /// @notice Reproduces the canonical digest across tiers 1 through 5,000.
    /// @dev This is a launch-time proof helper, not a runtime minting path.
    function collectionDigest() internal pure returns (bytes32) {
        bytes memory all = new bytes(uint256(MAX_TIER) * 11);
        uint256 cursor;
        for (uint32 tier = 1; tier <= MAX_TIER; ++tier) {
            Traits memory traits = traitsFor(tier);
            uint88 item = (uint88(tier) << 56)
                | (uint88(traits.wrap) << 48)
                | (uint88(traits.head) << 40)
                | (uint88(traits.eyes) << 32)
                | (uint88(traits.jaw) << 24)
                | (uint88(traits.bind) << 16)
                | (uint88(traits.charm) << 8)
                | uint88(traits.ground);
            assembly ("memory-safe") {
                mstore(add(add(all, 32), cursor), shl(168, item))
            }
            cursor += 11;
        }
        return keccak256(all);
    }

    function optionCount(uint8 slot) internal pure returns (uint8) {
        if (slot <= 1) return 10;
        if (slot == 2) return 9;
        if (slot == 3) return 7;
        if (slot == 4) return 8;
        if (slot == 5 || slot == 6) return 9;
        revert InvalidSlot(slot);
    }

    function weight(uint8 slot, uint8 option) internal pure returns (uint16) {
        if (option >= optionCount(slot)) revert InvalidOption(slot, option);

        if (slot == 0) {
            uint16[10] memory wrapWeights = [uint16(2600), 2000, 1700, 1200, 900, 600, 450, 350, 150, 50];
            return wrapWeights[option];
        }
        if (slot == 1) {
            uint16[10] memory headWeights = [uint16(3000), 2200, 1500, 1100, 800, 600, 400, 250, 100, 50];
            return headWeights[option];
        }
        if (slot == 2) {
            uint16[9] memory eyesWeights = [uint16(2800), 2400, 1600, 1200, 900, 550, 350, 150, 50];
            return eyesWeights[option];
        }
        if (slot == 3) {
            uint16[7] memory jawWeights = [uint16(3400), 2300, 1700, 1200, 800, 450, 150];
            return jawWeights[option];
        }
        if (slot == 4) {
            uint16[8] memory bindWeights = [uint16(3500), 2400, 1600, 1100, 700, 450, 200, 50];
            return bindWeights[option];
        }
        if (slot == 5) {
            uint16[9] memory charmWeights = [uint16(3600), 2200, 1500, 1100, 800, 400, 250, 120, 30];
            return charmWeights[option];
        }

        uint16[9] memory groundWeights = [uint16(2600), 2360, 1600, 1200, 900, 700, 300, 240, 100];
        return groundWeights[option];
    }

    function traitAt(Traits memory traits, uint8 slot) internal pure returns (uint8) {
        if (slot == 0) return traits.wrap;
        if (slot == 1) return traits.head;
        if (slot == 2) return traits.eyes;
        if (slot == 3) return traits.jaw;
        if (slot == 4) return traits.bind;
        if (slot == 5) return traits.charm;
        if (slot == 6) return traits.ground;
        revert InvalidSlot(slot);
    }

    function _validateTier(uint32 tier) private pure {
        if (tier == 0 || tier > MAX_TIER) revert InvalidTier(tier);
    }

    function _roll(bytes32 seed, uint8 slot) private pure returns (uint32) {
        return uint32(bytes4(seed << (uint256(slot) * 32))) % 10_000;
    }

    function _pick(uint8 slot, uint32 roll) private pure returns (uint8) {
        // `roll < cumulative` is the canonical strict `cumulative > roll` walk.
        if (slot == 0) {
            if (roll < 2600) return 0;
            if (roll < 4600) return 1;
            if (roll < 6300) return 2;
            if (roll < 7500) return 3;
            if (roll < 8400) return 4;
            if (roll < 9000) return 5;
            if (roll < 9450) return 6;
            if (roll < 9800) return 7;
            if (roll < 9950) return 8;
            return 9;
        }
        if (slot == 1) {
            if (roll < 3000) return 0;
            if (roll < 5200) return 1;
            if (roll < 6700) return 2;
            if (roll < 7800) return 3;
            if (roll < 8600) return 4;
            if (roll < 9200) return 5;
            if (roll < 9600) return 6;
            if (roll < 9850) return 7;
            if (roll < 9950) return 8;
            return 9;
        }
        if (slot == 2) {
            if (roll < 2800) return 0;
            if (roll < 5200) return 1;
            if (roll < 6800) return 2;
            if (roll < 8000) return 3;
            if (roll < 8900) return 4;
            if (roll < 9450) return 5;
            if (roll < 9800) return 6;
            if (roll < 9950) return 7;
            return 8;
        }
        if (slot == 3) {
            if (roll < 3400) return 0;
            if (roll < 5700) return 1;
            if (roll < 7400) return 2;
            if (roll < 8600) return 3;
            if (roll < 9400) return 4;
            if (roll < 9850) return 5;
            return 6;
        }
        if (slot == 4) {
            if (roll < 3500) return 0;
            if (roll < 5900) return 1;
            if (roll < 7500) return 2;
            if (roll < 8600) return 3;
            if (roll < 9300) return 4;
            if (roll < 9750) return 5;
            if (roll < 9950) return 6;
            return 7;
        }
        if (slot == 5) {
            if (roll < 3600) return 0;
            if (roll < 5800) return 1;
            if (roll < 7300) return 2;
            if (roll < 8400) return 3;
            if (roll < 9200) return 4;
            if (roll < 9600) return 5;
            if (roll < 9850) return 6;
            if (roll < 9970) return 7;
            return 8;
        }
        if (slot == 6) {
            if (roll < 2600) return 0;
            if (roll < 4960) return 1;
            if (roll < 6560) return 2;
            if (roll < 7760) return 3;
            if (roll < 8660) return 4;
            if (roll < 9360) return 5;
            if (roll < 9660) return 6;
            if (roll < 9900) return 7;
            return 8;
        }
        revert InvalidSlot(slot);
    }
}
