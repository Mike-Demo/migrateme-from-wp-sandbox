# Security audit remediation backlog

Parent issue: [Security audit 2026-10-21 — prioritize findings and create remediation issues](https://github.com/Mike-Demo/migrateme-from-wp-sandbox/issues/1)

Issue creation is not available in this session, so this document contains the prioritized issues ready to file.

## Priority

1. **Low — public manifest metadata disclosure.** This is the only confirmed finding. The manifest is publicly linked and directly exposes operator-local and WordPress.com hosting details to unauthenticated readers. Its fix is small and can be limited to redacting the published copy. There are no other confirmed findings to group with it.
2. **Needs validation — stored script injection.** Not confirmed; validate the stated missing fact before assigning severity or planning a remediation.
3. **Needs validation — publication of private, draft, and future items.** Not confirmed; validate the stated missing fact before assigning severity or planning a remediation.

## Remediation issue

### `[security][low] Redact internal metadata from the published manifest`

**Finding:** The published `manifest.json` discloses the source WXR's operator-local absolute path as `source.file`, WordPress.com internal attachment paths including blog ID `257947551`, and author username `mdemop` across all 44 items. The manifest is linked from `index.html`, making these details available to unauthenticated readers.

**Evidence:** `manifest.json` contains `/home/hatch/workspace/user/files/dxs.WordPress.2026-10-14.xml`, attachment paths under `/home/wpcom/public_html/wp-content/blogs.dir/4ff/257947551/`, and `"author": "mdemop"`. `generate.py` line 153 copies the run manifest verbatim into the published output.

**Root cause:** The generator publishes the local run manifest without a redaction step.

**Smallest fix:** Redact only the published manifest: reduce `source.file` and each `_wp_attached_file` value to its bare filename, remove the `file` member from `_wp_attachment_metadata`, and drop author usernames. Preserve item IDs, mappings, and SHA-256 checksums.

**Parent:** Closes/relates to [#1](https://github.com/Mike-Demo/migrateme-from-wp-sandbox/issues/1).

## Needs-validation checklist issue

### `[security][needs-validation] Audit leads to validate`

Validate each lead before treating it as a confirmed finding. Do not assign severity to these leads.

- [ ] **Stored script injection: migrated WordPress body is inserted into generated pages without sanitisation, bypassing WordPress unfiltered-HTML restrictions**
  - Fingerprint: `generate.py:unsanitized-migrated-body-stored-xss`
  - Claimed root cause: `generate.py` lines 104–112 pass the body verbatim or through Python-Markdown (which passes raw HTML) and interpolate `{rendered}` unescaped into the page body, with no allowlist sanitiser and no CSP, unlike the `html.escape` applied to titles and front matter at lines 75 and 101.
  - Missing fact (verbatim as available in the parent issue): “Whether generate.py is ever run on a WXR/run-output set containing active markup (script/event-handler/javascript: URL) authored by a principal below WordPress's unfiltered_html capability — e.g. a multi-author or non-operator site export — rather than only the operator's own single-author testbed inputs hardcoded at generate.py lines 9-11; the sh…”

- [ ] **Private, draft and future WordPress items are published world-readable: generator displays WP status but never uses it to exclude or gate items**
  - Fingerprint: `publication:wp-private-draft-future-status-not-enforced`
  - Claimed root cause: `generate.py` parses WP status from the WXR (lines 14–27, 97–103) but never uses it to exclude or gate publication: lines 86–95 copy every raw file, lines 96–115 write a page for every item, and the index (lines 118–125) groups by type only.
  - Missing fact (verbatim as available in the parent issue): “Whether this generator/publication path is applied to any non-testbed WordPress export containing genuinely confidential private, draft or future content without the operator explicitly re-authorising wider release; in this repository the only affected items are the operator's own documented synthetic fixtures, so no cross-boundary disclosure of r…”

**Parent:** [#1](https://github.com/Mike-Demo/migrateme-from-wp-sandbox/issues/1).

> The parent issue text available in this session ends both missing-fact statements with ellipses. They are preserved above as provided rather than completing the omitted wording by inference; verify against the original full text before filing if the omitted wording is available.
