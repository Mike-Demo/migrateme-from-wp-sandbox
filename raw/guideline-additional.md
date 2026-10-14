---
title: "Additional"
slug: "guideline-additional"
type: "other"
date: "2026-10-13 21:01:58"
---

Migration integrity rules (highest priority):
- Content must stay exportable through the standard WordPress export (WXR). Prefer core blocks and standard patterns; avoid exotic blocks whose markup or data will not survive an export.
- Do not rename, retitle, or delete existing fixture posts, pages, categories, or tags once created — migrations and their verification compare against them. Add new fixtures instead of editing old ones, unless explicitly instructed.
- Keep page hierarchy and taxonomy hierarchy intact (for example, the child page under "About This Testbed" and the child category under "Field Notes").

Family links to keep wherever links are listed (footer, About page): migrateme.tech, lovable.sandbox.migrateme.tech, lovable.cloud.sandbox.migrateme.tech.

Accessibility: one H1 per page, headings in order, meaningful link text (never "click here"), sufficient color contrast — the burnt-orange accent is for large text, stats, and graphic accents, not small body text.

Content that should never appear on this site: real personal data; real customer or patient information; prices or purchase calls to action; placeholder lorem ipsum; the default WordPress sample text ("123 Example Street", "hi@example.com") anywhere visible.
