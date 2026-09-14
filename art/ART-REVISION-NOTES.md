# BOUND / Wrapped Mummies — artwork revision 1

Complete editable art candidate, prepared from the supplied prototype. This is an art delivery for review, not a certification that an NFT launch or its contracts are production ready.

## Start here

- `preview/collection.png`: 24 curated algorithmic studies, not assigned NFT IDs and not a rarity-weighted sample.
- `preview/avatar_48px.png`: actual 48px circular crops. Tall crowns lose their outermost tips in some circular crops; square originals retain the full art.
- `preview/<slot>.png`: every option shown on a neutral reference character.
- `preview/pairs/`: all 21 slot-pair sheets, comprising 1,644 combinations with remaining slots held at a reference configuration.
- `layers/`: 62 full-canvas PNG layers, including three transparent None options and the intentionally transparent Wrapped jaw.
- `layers/manifest.json`: ordered option lists, original weights, palette, stack order, paths, and SHA-256 checksums for PNG bytes and raw RGBA pixels.
- `validation.json`: automated check results.
- `build.py`: editable artwork generator. `prototype.py` supplies the original palette, geometry and validation function; its original drawing functions are not used by the revision.

## Changes

Separated sockets replace the continuous black eye bar. A wrapped nose bridge and shaped socket edges create depth. Eyes and jaws have distinct shapes; common headwear uses stone, linen and lapis. All 7 slots are complete. Dark body contours separate light wraps from light backgrounds; unraveling adds trailing cloth. Background details stay sparse to preserve face legibility.

Artwork remains 32×32 RGBA using the original 22-color palette with binary alpha. Enlargements use nearest-neighbor scaling. No AI raster generation or resampling was used to replace the editable pixel geometry. No trait-selection algorithm or contract was implemented or changed.

## Resolved provisionally for this candidate

The input documents conflict. These are explicit design assumptions, not approved changes to a deployed contract:

1. The strict prototype rule permits gold and gold_sh only at weights below 350. It conflicts with Gold eyes (350), Gold-threaded wrap (350), Gilded teeth (800), Gold wire (450), and Gold leaf background (500). This candidate preserves weights and the strict rule, using linen/sand highlights in those options. Before release, approve these substitutes or revise the gold policy and regenerate. Their names currently overpromise their appearance.
2. Verdigris uses the existing cool gray/blue colors. Authentic green patina would require a palette revision, which this candidate does not make.
3. Original filenames are retained where a valid trait exists: wrap/lapis, head/crown, jaw/gilded, ground/tomb, ground/lapis, ground/gold. These correspond to Lapis-dyed, Pharaoh crown, Gilded teeth, Tomb wall, Lapis field, Gold leaf. The old extra wrap/gold is excluded because it is absent from the 10-option specification. Gold-threaded is a new option with its specified position. Confirm the manifest against any downstream renderer before integrating.
4. The supplied palette already has 22 colors, despite the prose asking for 16–20. The actual supplied palette takes precedence in this candidate.

## Build and validation

Requires Python 3 and Pillow. Run `python build.py` from any directory. Rebuild into a clean copy when changing option names so obsolete assets cannot remain in the release directory.

The build fails on invalid layer size, palette, alpha or gold usage. It also checks weight totals, required layer count, unexpected empty layers, background opacity, and repeated rendering equality. This validates file and generator properties, not artistic quality or blockchain execution.

## Release work still required

- Approve the visual direction, provisional gold substitutions, blue-gray verdigris, naming map, and circular crop tradeoffs.
- Review the pair sheets and final assigned collection. Pairwise coverage does not prove absence of three-way occlusion or other higher-order interactions.
- Enumerate actual tier assignments with the canonical selector and review the complete collection, including duplicate traits and actual rarity. Weight / 2 is an expected count, not a guaranteed count. Nonuniform trait weights invalidate the brief's simple uniform estimate of about three duplicate pairs.
- Bind this versioned manifest and pixel assets to the production renderer; freeze asset hashes and storage references. Supply NFT metadata and durable image/metadata hosting or on-chain encoding appropriate to the implementation.
- Verify both chain implementations across all 5,000 tiers and compare final rendered pixels. Identical trait tuples alone prove trait parity, not identical artwork or rendering. No live chains, launchpads, ownership rights, or deployment configuration were checked in this art task.

The original source documents were treated as project reference material. Their embedded instructions were not treated as independent user authorization for deployment, publishing, or changes outside this artwork package.
