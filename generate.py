#!/usr/bin/env python3
"""Generate the from.wp.sandbox.migrateme.tech static site from the real migration run output."""
import html, json, os, re, shutil, sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.expanduser("~/workspace/.pip-packages"))
import markdown as mdlib

RUN = os.path.expanduser("~/workspace/migrateme-wp-testbed/run-output")
WXR = os.path.expanduser("~/workspace/user/files/dxs.WordPress.2026-10-14.xml")
OUT = os.path.expanduser("~/workspace/migrateme-from-site")

NS = {'wp': 'http://wordpress.org/export/1.2/'}

# --- authoritative type/status per slug from the WXR itself ---
wxr_info = {}
wxr_by_title = {}
tree = ET.parse(WXR)
for it in tree.getroot().find('channel').findall('item'):
    slug = it.findtext('wp:post_name', namespaces=NS) or ''
    entry = (it.findtext('wp:post_type', namespaces=NS),
             it.findtext('wp:status', namespaces=NS))
    wxr_info[slug] = entry
    if not slug:
        wxr_by_title[it.findtext('title') or ''] = entry

CSS = """
:root{--paper:#FBF9F3;--ink:#1F1B16;--accent:#D9431F;--muted:#6b6257;--rule:#e3dccd}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);
font-family:ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif;line-height:1.55}
.wrap{max-width:920px;margin:0 auto;padding:32px 20px 64px}
h1,h2{font-family:Georgia,'Times New Roman',serif;font-weight:600}
.eyebrow{font-family:ui-monospace,Menlo,monospace;font-size:12px;letter-spacing:.14em;
text-transform:uppercase;color:var(--accent)}
a{color:var(--accent)}
table{border-collapse:collapse;width:100%;margin:12px 0 28px;font-size:14px}
th,td{border-bottom:1px solid var(--rule);text-align:left;padding:6px 8px;vertical-align:top}
th{font-family:ui-monospace,Menlo,monospace;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:20px 0}
.stat{border:1px solid var(--rule);border-radius:8px;padding:12px 14px;background:#fff}
.stat b{display:block;font-size:22px;font-family:Georgia,serif}
.stat span{font-size:12px;color:var(--muted)}
.fm{background:#fff;border:1px solid var(--rule);border-radius:8px;padding:4px 14px;margin:16px 0}
.body{background:#fff;border:1px solid var(--rule);border-radius:8px;padding:18px 22px;margin:16px 0}
.body img{max-width:100%}
footer{border-top:1px solid var(--rule);margin-top:40px;padding-top:16px;font-size:13px;color:var(--muted)}
code{font-family:ui-monospace,Menlo,monospace;font-size:13px}
"""

def parse_fm(text):
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', text, re.S)
    if not m:
        return {}, text
    fm, body = {}, m.group(2)
    key = None
    for line in m.group(1).splitlines():
        if line.startswith('  - '):
            cur = fm.get(key)
            if not isinstance(cur, list):
                fm[key] = [cur] if cur else []
            fm[key].append(line[4:].strip().strip('"'))
        elif ':' in line:
            k, v = line.split(':', 1)
            key = k.strip()
            fm[key] = v.strip().strip('"')
    return fm, body

def page(title, eyebrow, content):
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" type="image/svg+xml" href="/logo.svg">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<title>{html.escape(title)} — from.wp.sandbox · migrateme.tech</title>
<style>{CSS}</style></head>
<body><div class="wrap">
<p class="eyebrow"><img src="/logo.svg" alt="" width="22" height="22" style="vertical-align:-5px;margin-right:8px">{html.escape(eyebrow)}</p>
{content}
<footer>MIT licensed. Built by <a href="https://mikedemo.dev">Mike "Demo" Demopoulos</a> ·
<a href="https://github.com/Mike-Demo/migrateme.tech">migrateme.tech</a> ·
Source: <a href="https://wp.sandbox.migrateme.tech">wp.sandbox.migrateme.tech</a></footer>
</div></body></html>"""

items = []
for fname in sorted(os.listdir(RUN)):
    if not fname.endswith('.md'):
        continue
    text = open(os.path.join(RUN, fname), encoding='utf-8').read()
    fm, body = parse_fm(text)
    items.append({'file': fname, 'fm': fm, 'body': body, 'text': text})
    shutil.copy(os.path.join(RUN, fname), os.path.join(OUT, 'raw', fname))

for it in items:
    fm = it['fm']
    slug = fm.get('slug', '')
    wtype, wstatus = wxr_info.get(slug, ('', ''))
    if not wtype:
        import html as _h
        wtype, wstatus = wxr_by_title.get(_h.unescape(fm.get('title', '')), ('', ''))
    rows = ''.join(f"<tr><th>{html.escape(str(k))}</th><td>{html.escape(', '.join(v) if isinstance(v, list) else str(v))}</td></tr>" for k, v in fm.items())
    if wtype:
        rows += f"<tr><th>wp type / status</th><td>{html.escape(wtype)} / {html.escape(wstatus or '')}</td></tr>"
    body = it['body'].strip()
    if '<p>' in body or '<!-- wp:' in body:
        rendered = body  # already HTML (Gutenberg block markup, comments invisible in browser)
    else:
        rendered = mdlib.markdown(body)
    content = f"""<h1>{html.escape(fm.get('title', it['file']))}</h1>
<p><a href="../index.html">← All migrated items</a> · <a href="../raw/{it['file']}">Raw engine output (.md)</a></p>
<div class="fm"><table>{rows}</table></div>
<div class="body">{rendered if rendered else '<p><em>No body content — metadata-only item.</em></p>'}</div>"""
    with open(os.path.join(OUT, 'items', it['file'].replace('.md', '.html')), 'w', encoding='utf-8') as f:
        f.write(page(fm.get('title', it['file']), 'Migrated item · migrateme.tech run, Oct 14 2026', content))
    it['wtype'], it['wstatus'] = wtype, wstatus

groups = [('post', 'Posts'), ('page', 'Pages'), ('attachment', 'Attachments'), ('other', 'Everything else WordPress sent')]
sections = ''
for gtype, gname in groups:
    rows = ''
    for it in [i for i in items if i['fm'].get('type') == gtype]:
        fm = it['fm']
        rows += (f"<tr><td><a href=\"items/{it['file'].replace('.md', '.html')}\">{html.escape(fm.get('title', ''))}</a></td>"
                 f"<td><code>{html.escape(fm.get('slug', ''))}</code></td>"
                 f"<td>{html.escape(it.get('wstatus') or '')}</td><td>{html.escape(fm.get('date', ''))}</td></tr>")
    if rows:
        sections += f"<h2 id=\"{gtype}\">{gname}</h2><table><tr><th>Title</th><th>Slug</th><th>WP status</th><th>Date</th></tr>{rows}</table>"

index_content = """<h1>From WordPress: a real migration, published</h1>
<p><strong>On this page:</strong> <a href="#run">The run</a> · <a href="#post">Posts</a> · <a href="#page">Pages</a> · <a href="#attachment">Attachments</a> · <a href="#other">Everything else</a> · <a href="manifest.json">Manifest</a> · <a href="llms.txt">llms.txt</a> · <a href="agents.md">For agents</a></p>
<p><strong>Start with the address:</strong> <code>from.wp.sandbox.migrateme.tech</code> follows this project's naming convention — every address declares what it is. This one holds everything that came <em>from</em> the <code>wp.sandbox</code> source. Its sibling <code>wp.spacefast.sandbox</code> is the same site after a different route, and the destination-form routes (<code>lovable-to-wordpress.migrateme.tech</code>) are the convention's next step.</p>
<h2 id="run">The run</h2>
<p>This site is the <strong>output</strong> of the migrateme.tech toolkit's first real-world run — not a mockup.
The source is the live WordPress testbed at <a href="https://wp.sandbox.migrateme.tech">wp.sandbox.migrateme.tech</a> (DXS, the Digital Experience
Showcase). Its WXR export was run through the toolkit on October 14, 2026: plan, dry run, approved migration, validation.
Every page below is one migrated item, rendered from the exact file the engine wrote; the raw Markdown is one click away on each page,
and the full run manifest is <a href="manifest.json">here</a>.</p>
<div class="stats">
<div class="stat"><b>44</b><span>items migrated — 44 expected, 44 validated, 0 exceptions</span></div>
<div class="stat"><b>420</b><span>field mappings — 287 deterministic, 133 held for manual review</span></div>
<div class="stat"><b>310</b><span>risks flagged in the plan, before anything was written</span></div>
<div class="stat"><b>0</b><span>files written by the dry run — the engine refuses to migrate unapproved</span></div>
</div>
<p>The honest wrinkles are preserved, not polished away: post bodies keep their Gutenberg block comments (visible in the raw files),
attachment binaries travel separately (these are their metadata records), colliding slugs were disambiguated deterministically,
and the scheduled post kept its 14:00 local date. The export also contained things no fixture anticipated — the site's global styles,
navigation, templates, and its AI Guidelines — all migrated as documents, under "Everything else" below.</p>
""" + sections

with open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(page('From WordPress — migration output', 'migrateme.tech · real-world run output', index_content))

shutil.copy(os.path.join(RUN, 'manifest.json'), os.path.join(OUT, 'manifest.json'))
with open(os.path.join(OUT, 'CNAME'), 'w') as f:
    f.write('from.wp.sandbox.migrateme.tech\n')
print('generated:', len(items), 'item pages + index')


LLMS = """# from.wp.sandbox.migrateme.tech

> The published output of the migrateme.tech toolkit's first real-world run: a live WordPress site (DXS, the Digital Experience Showcase) exported as WXR and migrated to Markdown on October 14, 2026 — plan, dry run, approved migration, validation. 44 items, 420 field mappings (287 deterministic, 133 manual review), 310 risks flagged, validation passed 44/44 with an empty exception queue.

## The run

- [Index of migrated items](https://from.wp.sandbox.migrateme.tech/): every item, grouped as WordPress sent it — posts, pages, attachments, and everything else (templates, navigation, global styles, AI Guidelines)
- [manifest.json](https://from.wp.sandbox.migrateme.tech/manifest.json): the full run manifest — items, mappings, provenance, sha256 checksums
- [Source site](https://wp.sandbox.migrateme.tech/): the WordPress testbed this output came from
- [Project home](https://migrateme.tech/): migrateme.tech, the toolkit
- [agents.md](https://from.wp.sandbox.migrateme.tech/agents.md): how this site was produced and how to consume it
"""

AGENTS = """# from.wp.sandbox — for agents

This site is machine-generated evidence, not a hand-written website. It was produced by the migrateme.tech toolkit from a live WordPress export, and republished as static HTML by a small Python generator (in the repository) so humans and agents can inspect a real migration run.

## How to consume it

- `index.html` is the human index. Item pages under `items/` render each migrated file: front matter first, then the body exactly as written.
- `raw/` holds the engine's output byte for byte — cite these, not the rendered pages, when precision matters.
- `manifest.json` is the authoritative run record: 44 items, 420 mappings with methods (deterministic vs manual-review), provenance, and sha256 checksums for source and destination. If a rendered page and the manifest disagree, the manifest wins.

## Conventions on display

- The address follows the project naming convention: `from.<source>` holds a run's output. The source is `wp.sandbox.migrateme.tech`; a sibling route, `wp.spacefast.sandbox.migrateme.tech`, holds the same source site moved by SpaceFast's official tooling instead.
- Publication states are WordPress's own (publish / draft / private / future) and are shown as recorded. The scheduled item kept its local time; attachment binaries travel separately, so attachment items here are metadata records.
"""

with open(os.path.join(OUT, 'llms.txt'), 'w', encoding='utf-8') as f: f.write(LLMS)
with open(os.path.join(OUT, 'agents.md'), 'w', encoding='utf-8') as f: f.write(AGENTS)
print('generator: llms/agents emitters added')
