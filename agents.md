# from.wp.sandbox — for agents

This site is machine-generated evidence, not a hand-written website. It was produced by the migrateme.tech toolkit from a live WordPress export, and republished as static HTML by a small Python generator (in the repository) so humans and agents can inspect a real migration run.

## How to consume it

- `index.html` is the human index. Item pages under `items/` render each migrated file: front matter first, then the body exactly as written.
- `raw/` holds the engine's output byte for byte — cite these, not the rendered pages, when precision matters.
- `manifest.json` is the authoritative run record: 44 items, 420 mappings with methods (deterministic vs manual-review), provenance, and sha256 checksums for source and destination. If a rendered page and the manifest disagree, the manifest wins.

## Conventions on display

- The address follows the project naming convention: `from.<source>` holds a run's output. The source is `wp.sandbox.migrateme.tech`; a sibling route, `wp.spacefast.sandbox.migrateme.tech`, holds the same source site, published to SpaceFast as a static mirror via the CLI after the official plugin's publish stalled on WordPress.com.
- Publication states are WordPress's own (publish / draft / private / future) and are shown as recorded. The scheduled item kept its local time; attachment binaries travel separately, so attachment items here are metadata records.
