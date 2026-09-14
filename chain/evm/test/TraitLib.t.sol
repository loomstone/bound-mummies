// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {TraitLib} from "../src/TraitLib.sol";

contract TraitHarness {
    function seedFor(uint32 tier) external pure returns (bytes32) {
        return TraitLib.seedFor(tier);
    }

    function serialize(uint32 tier) external pure returns (bytes memory) {
        return TraitLib.serialize(tier);
    }

    function digest() external pure returns (bytes32) {
        return TraitLib.collectionDigest();
    }

    function weight(uint8 slot, uint8 option) external pure returns (uint16) {
        return TraitLib.weight(slot, option);
    }

    function optionCount(uint8 slot) external pure returns (uint8) {
        return TraitLib.optionCount(slot);
    }

    function traitAt(uint32 tier, uint8 slot) external pure returns (uint8) {
        return TraitLib.traitAt(TraitLib.traitsFor(tier), slot);
    }
}

contract TraitLibTest {
    TraitHarness private harness;

    function setUp() public {
        harness = new TraitHarness();
    }

    function testKeccakIsEthereumKeccak() public pure {
        _assertEq(
            keccak256(""),
            0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470,
            "wrong keccak variant"
        );
    }

    function testEverySlotWeightSumsTo10000() public view {
        for (uint8 slot; slot < 7; ++slot) {
            uint256 sum;
            for (uint8 option; option < harness.optionCount(slot); ++option) {
                sum += harness.weight(slot, option);
            }
            _assertEq(sum, 10_000, "weight sum");
        }
    }

    function testTierRange() public view {
        (bool zeroOk,) = address(harness).staticcall(abi.encodeCall(harness.seedFor, (uint32(0))));
        (bool highOk,) = address(harness).staticcall(abi.encodeCall(harness.seedFor, (uint32(5001))));
        require(!zeroOk, "tier zero must revert");
        require(!highOk, "tier 5001 must revert");
        require(harness.seedFor(1) != bytes32(0), "tier one failed");
        require(harness.seedFor(5000) != bytes32(0), "tier 5000 failed");
    }

    function testAllCanonicalVectors() public view {
        _vector(1, 0x7b16508aafbb1aba3ad5f345a83d20c8d0b79ada9e01bc0d0f33c63b884e0e38, hex"0000000109010803010100");
        _vector(2, 0xad9fc6fb2292cc3f08a15b7dcb893988e8b87fdb9548858e1fb32df4d50231c3, hex"0000000207020003010302");
        _vector(3, 0x867134e729c626a74ee3767f1b40b681fab7286ae0cfa8563b9c421071a245ef, hex"0000000302000702020102");
        _vector(42, 0x194d278718290a5dc291d2e30b8789949ca600f63995b3a9091a30070c36b51d, hex"0000002a03000200010000");
        _vector(100, 0x1ba51000e619bef5a46737ea7e7d38feca0721daf6cc4d991d7d7a157455e4f5, hex"0000006400030302010100");
        _vector(777, 0xe74f7e8405050a4372cbd63160a62a0d50ff7f1d119703c4f82510f517c9aaaf, hex"0000030903020000000505");
        _vector(1234, 0xb4de6f6adc7e17340c914355d322e2a01dcaa7fdf4cf093982717a4f73d5511e, hex"000004d203000204000401");
        _vector(2500, 0xad470c7026dfc8985f1253d205cd8a095be2bf91ddb2210b17adaca8520561ac, hex"000009c402000202020404");
        _vector(3333, 0xa1be23cd6e11c6186124646b8568b1794148b215ec851537ee92e5a60474df6c, hex"00000d0501040100000101");
        _vector(4271, 0x552488e0afa3f783f0ffd3e376090929b40ee50e561bc2fed22d110360e9a223, hex"000010af04040301010705");
        _vector(4999, 0x83545ffed28cf6c51fe948b2bf64ffaaf1d331dca8ecc5d93a7f968ccd4d1fc4, hex"0000138702010002060500");
        _vector(5000, 0xf09db8666cd51ea1a795eb2b02f2aaef63fa7619ac34650376590b2455ec3070, hex"0000138804020003040103");
    }

    function testCollectionDigest() public view {
        _assertEq(
            harness.digest(),
            0x0beebbb2d7f6cee419091692001ec6c15ae46070f7bd5459d761407964aee33b,
            "collection digest"
        );
    }

    function testDistributionTracksWeights() public view {
        uint16[10][7] memory counts;
        for (uint32 tier = 1; tier <= 5_000; ++tier) {
            for (uint8 slot; slot < 7; ++slot) {
                ++counts[slot][harness.traitAt(tier, slot)];
            }
        }

        for (uint8 slot; slot < 7; ++slot) {
            for (uint8 option; option < harness.optionCount(slot); ++option) {
                uint256 expected = harness.weight(slot, option) / 2;
                uint256 tolerance = 4 * _sqrt(expected);
                if (tolerance < 5) tolerance = 5;
                uint256 observed = counts[slot][option];
                uint256 difference = observed > expected ? observed - expected : expected - observed;
                require(difference <= tolerance, "distribution outside tolerance");
            }
        }
    }

    function testGoldAmendments() public view {
        _assertEq(harness.weight(6, 7), 240, "ground/gold amendment");
        _assertEq(harness.weight(6, 1), 2360, "ground/tomb amendment");
    }

    function _vector(uint32 tier, bytes32 expectedSeed, bytes memory expectedSerialized) private view {
        _assertEq(harness.seedFor(tier), expectedSeed, "vector seed");
        _assertEq(keccak256(harness.serialize(tier)), keccak256(expectedSerialized), "vector traits");
    }

    function _sqrt(uint256 value) private pure returns (uint256 result) {
        if (value == 0) return 0;
        result = value;
        uint256 candidate = (value + 1) / 2;
        while (candidate < result) {
            result = candidate;
            candidate = (value / candidate + candidate) / 2;
        }
    }

    function _assertEq(bytes32 actual, bytes32 expected, string memory message) private pure {
        require(actual == expected, message);
    }

    function _assertEq(uint256 actual, uint256 expected, string memory message) private pure {
        require(actual == expected, message);
    }
}
