#!/usr/bin/env python3
"""Build index.html — a Morrowind-themed SPA wrapping tarvis79's guide,
with all guide text preserved verbatim."""
import json, html as H
import re

sections = json.load(open('/home/scott/morrowind-guide/sections.json'))
groups = json.load(open('/home/scott/morrowind-guide/groups.json'))

# Prepend the header/TOC block to Introduction group for nav purposes
nav_groups = [('Preamble', ['PRE'])] + groups
have = {s['id'] for s in sections}
nav_groups = [(g, [c for c in cs if c in have]) for g, cs in nav_groups]

titles = {s['id']: s['title'] for s in sections}

toc_html = []
for gname, codes in nav_groups:
    toc_html.append(f'<li class="toc-group">{H.escape(gname)}<ul>')
    for c in codes:
        t = titles[c]
        if c == 'PRE':
            label = 'Header &amp; Table of Contents'
        else:
            label = H.escape(t)
        toc_html.append(f'<li><a href="#sec-{c}" data-target="sec-{c}"><span class="toc-code">{c}</span>{label}</a></li>')
    toc_html.append('</ul></li>')
toc = '\n'.join(toc_html)

# Sections HTML: keep text VERBATIM inside <pre>
secs_html = []
def is_prose_line(line):
    s = line
    if not s.strip(): return False
    if s[:1] in (' ', chr(9)): return False
    if re.match(r'^\*{3}.+\*{3}$', s.strip()): return False
    if re.match(r'^\d+[\)\.]', s.strip()): return False
    if re.match(r'^[ivxIVX]+[\.\)]', s.strip()): return False
    if re.search(r'\S {2,}\S', s): return False
    if len(s.rstrip()) < 45: return False
    if s.rstrip().endswith((':', '-', '*')): return False
    if re.match(r'^Version \d', s.strip()): return False
    return True


def render_blocks(raw):
    out = []
    for block in re.split(r'\n\s*\n', raw):
        lines = block.split('\n')
        prose_ct = sum(is_prose_line(l) for l in lines)
        if prose_ct >= max(1, len(lines) - 1) and prose_ct > 0:
            para = ' '.join(l.strip() for l in lines)
            out.append('<p class="doc-para">' + H.escape(para) + '</p>')
        else:
            out.append('<pre class="doc-text">' + H.escape(block) + '</pre>')
    return '\n'.join(out)


for i, s in enumerate(sections):
    cid = H.escape(s['id'], quote=True)
    title = 'Header & Table of Contents' if s['id'] == 'PRE' else H.escape(s['title'])
    text = render_blocks(s['text'])
    secs_html.append(
f'''<section class="doc-section" id="sec-{cid}" data-anchor="{s['id']}">
  <header class="sec-header">
    <span class="sec-num">{s['id']}</span>
    <h2>{title}</h2>
  </header>
<pre class="doc-text">{text}</pre>
</section>''')
body = '\n'.join(secs_html)

payload = json.dumps({'sections': [{'id': s['id'], 'title': ('Header & Table of Contents' if s['id']=='PRE' else s['title'])} for s in sections]}).replace('</', '<\\/')

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Elder Scrolls III: Morrowind — "Beating Morrowind in Easy Steps" by tarvis79</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Public+Sans:wght@400;600&family=Source+Code+Pro:wght@400;600&display=swap" rel="stylesheet">
<style>
:root {{
  --bg0:#100c08; --bg1:#1a140d; --bg2:#241b11;
  --ink:#d8c9a3; --ink-dim:#9a8a67;
  --gold:#c9a35a; --gold-bright:#e8c87e;
  --red:#8a2f23; --ash:#4a423a;
  --line:#5c4a2e;
}}
* {{ box-sizing:border-box }}
html {{ scroll-behavior:smooth }}
body {{
  margin:0; background:
    radial-gradient(1200px 600px at 70% -10%, #2a2013 0%, transparent 60%),
    radial-gradient(900px 500px at 10% 110%, #241407 0%, transparent 55%),
    var(--bg0);
  color:var(--ink);
  font-family:"Public Sans", "Segoe UI", sans-serif;
  font-size:17px; line-height:1.6;
}}
/* ---- progress bar ---- */
#progress {{ position:fixed;top:0;left:0;height:3px;width:0;background:linear-gradient(90deg,var(--gold),var(--gold-bright));z-index:60 }}
/* ---- layout ---- */
.layout {{ display:flex; min-height:100vh }}
/* ---- sidebar ---- */
#sidebar {{
  width:300px; flex-shrink:0; position:sticky; top:0; height:100vh; overflow-y:auto;
  background:linear-gradient(180deg,var(--bg1),var(--bg0));
  border-right:1px solid var(--line); padding:20px 14px 40px;
}}
#sidebar::-webkit-scrollbar{{width:8px}} #sidebar::-webkit-scrollbar-thumb{{background:var(--line);border-radius:4px}}
.brand {{ text-align:center; padding:10px 6px 18px; border-bottom:1px solid var(--line); margin-bottom:12px }}
.brand .rune {{ font-family:Cinzel,serif;color:var(--gold-bright);font-size:30px;line-height:1 }}
.brand h1 {{ font-family:Cinzel,serif;font-weight:700;font-size:17px;letter-spacing:.06em;color:var(--gold);margin:8px 0 2px }}
.brand p {{ margin:0;font-size:12.5px;color:var(--ink-dim);font-style:italic }}
#toc-search {{
  width:100%;margin:10px 0 6px;padding:8px 10px;border-radius:4px;
  background:var(--bg2);border:1px solid var(--line);color:var(--ink);
  font-family:inherit;font-size:15px;
}}
#toc-search:focus{{outline:none;border-color:var(--gold)}}
.toc-group {{ list-style:none;margin:10px 0 2px }}
.toc-group > b {{ display:block; font-family:Cinzel,serif;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);padding:6px 4px 2px }}
#toc ul {{ list-style:none;margin:0;padding:0 }}
#toc li a {{
  display:flex;gap:8px;align-items:baseline;padding:5px 8px;border-radius:4px;
  color:var(--ink-dim);text-decoration:none;font-size:14.5px;line-height:1.35;
  border-left:2px solid transparent;
}}
#toc li a:hover {{ background:var(--bg2);color:var(--ink) }}
#toc li a.active {{ color:var(--gold-bright);background:var(--bg2);border-left-color:var(--gold) }}
.toc-code {{ font-size:10.5px;color:var(--red);filter:brightness(1.6);font-family:monospace;flex-shrink:0;min-width:52px }}
/* ---- main ---- */
main {{ flex:1;min-width:0;padding:36px clamp(16px,4vw,64px) 120px }}
.hero {{
  max-width:900px;margin:0 auto 42px;text-align:center;
  border:1px solid var(--line);border-radius:6px;padding:38px 22px 30px;
  background:
    radial-gradient(600px 200px at 50% 0%, rgba(201,163,90,.08), transparent),
    var(--bg1);
  position:relative;
}}
.hero::before,.hero::after{{
  content:"";position:absolute;left:14px;right:14px;height:1px;
  background:linear-gradient(90deg,transparent,var(--gold),transparent)
}}
.hero::before{{top:8px}} .hero::after{{bottom:8px}}
.hero .daedric {{ font-family:Cinzel,serif;color:var(--red);filter:brightness(1.5);letter-spacing:.35em;font-size:13px }}
.hero h1 {{ font-family:Cinzel,serif;font-weight:700;font-size:clamp(26px,4.5vw,44px);color:var(--gold-bright);margin:10px 0 6px }}
.hero h2 {{ font-family:Cinzel,serif;font-weight:500;font-size:clamp(14px,2vw,19px);color:var(--gold);margin:0 0 14px }}
.hero p {{ max-width:640px;margin:0 auto 4px;color:var(--ink-dim);font-size:15.5px }}
.hero .meta {{ margin-top:14px;font-size:13px;color:var(--ink-dim) }}
.hero .meta b {{ color:var(--ink) }}
.doc-section {{ max-width:900px;margin:0 auto 34px }}
.sec-header {{
  display:flex;align-items:center;gap:14px;
  border-bottom:2px solid var(--line);padding:26px 0 10px;margin-bottom:14px;
  scroll-margin-top:20px;
}}
.sec-num {{
  font-family:monospace;font-size:11px;color:#0e0a06;background:linear-gradient(180deg,var(--gold),#a07c3c);
  padding:3px 7px;border-radius:3px;font-weight:bold;letter-spacing:.05em
}}
.sec-header h2 {{ font-family:Cinzel,serif;font-weight:700;font-size:clamp(19px,2.6vw,27px);color:var(--gold-bright);margin:0 }}
pre.doc-text {{
  white-space:pre-wrap;word-break:normal;overflow-wrap:anywhere;
  font-family:"Source Code Pro", ui-monospace, monospace;
  font-size:14px;line-height:1.45;
  background:rgba(20,15,9,.72);
  border:1px solid var(--line);border-left:3px solid var(--gold);
  border-radius:4px;padding:18px 20px;margin:0;
  tab-size:4;
}}
/* reflowed prose paragraphs fill the full box width */
p.doc-para {{
  margin:0 0 .9em;font-size:16.5px;line-height:1.65;
  font-family:"Public Sans","Segoe UI",sans-serif;color:var(--ink);
}}
pre.doc-text::selection, pre.doc-text *::selection {{ background:#5a4322;color:#fff }}
/* ---- mobile ---- */
#menu-btn {{
  display:none;position:fixed;top:12px;left:12px;z-index:50;
  background:var(--bg2);border:1px solid var(--gold);color:var(--gold-bright);
  font-family:Cinzel,serif;font-size:14px;padding:8px 14px;border-radius:4px;cursor:pointer
}}
#scrim {{ display:none;position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:40 }}
#top-btn {{
  position:fixed;bottom:22px;right:22px;z-index:45;display:none;
  width:44px;height:44px;border-radius:50%;border:1px solid var(--gold);
  background:var(--bg2);color:var(--gold-bright);font-size:19px;cursor:pointer
}}
@media (max-width:900px){{
  #menu-btn{{display:block}}
  #sidebar{{
    position:fixed;left:0;top:0;z-index:45;transform:translateX(-105%);
    transition:transform .28s ease;box-shadow:6px 0 30px rgba(0,0,0,.6)
  }}
  body.nav-open #sidebar{{transform:none}}
  body.nav-open #scrim{{display:block}}
  main{{padding-top:64px}}
}}
footer.site {{ max-width:900px;margin:60px auto 0;padding-top:18px;border-top:1px solid var(--line);text-align:center;color:var(--ink-dim);font-size:13.5px }}
footer.site a {{ color:var(--gold) }}
</style>
</head>
<body>
<div id="progress"></div>
<button id="menu-btn" aria-label="Toggle navigation">☰ Index</button>
<div id="scrim"></div>
<div class="layout">
<nav id="sidebar" aria-label="Table of contents">
  <div class="brand">
    <div class="rune">✶</div>
    <h1>MORROWIND</h1>
    <p>&ldquo;Beating Morrowind in ______ Easy Steps!&rdquo;</p>
  </div>
  <input id="toc-search" type="search" placeholder="Search the index…" autocomplete="off">
  <ul id="toc" style="list-style:none;margin:0;padding:0">
{toc}
  </ul>
</nav>
<main>
  <div class="hero">
    <div class="daedric">✦ NEREVAR ✦ MOON-AND-STAR ✦</div>
    <h1>Morrowind</h1>
    <h2>Game of the Year Edition &mdash; Complete Walkthrough</h2>
    <p>The complete text of tarvis79&rsquo;s GameFAQs guide, from the Imperial Prison Ship to the heart of Red Mountain &mdash; and through Tribunal and Bloodmoon beyond.</p>
    <p class="meta">Written by <b>Travis Whitsitt (tarvis79)</b> &middot; Version 1.00 &middot; Source: <a style="color:var(--gold)" href="https://gamefaqs.gamespot.com/pc/913818-the-elder-scrolls-iii-morrowind/faqs/71172">GameFAQs</a></p>
  </div>
{body}
  <footer class="site">
    <p>Guide text © Travis Whitsitt (tarvis79), reproduced verbatim per the guide&rsquo;s distribution policy. Page styling only &mdash; no wording altered.<br>
    The Elder Scrolls and Morrowind are trademarks of Bethesda Softworks.</p>
  </footer>
</main>
</div>
<button id="top-btn" aria-label="Back to top">▲</button>
<script id="section-index" type="application/json">{payload}</script>
<script>
(function() {{
  const links = Array.from(document.querySelectorAll('#toc li a'));
  const sections = links.map(a => document.getElementById(a.dataset.target)).filter(Boolean);
  // scroll spy
  let active = null;
  function spy() {{
    const y = window.scrollY + 120;
    let cur = sections[0];
    for (const s of sections) {{ if (s.offsetTop <= y) cur = s; }}
    if (cur !== active) {{
      active = cur;
      links.forEach(a => a.classList.toggle('active', a.dataset.target === cur.id));
      const al = links.find(a => a.dataset.target === cur.id);
      if (al) al.scrollIntoView({{block:'nearest'}});
      history.replaceState(null,'','#'+cur.id);
    }}
  }}
  document.addEventListener('scroll', () => {{
    requestAnimationFrame(spy);
    const d = document.documentElement;
    const p = d.scrollTop / (d.scrollHeight - d.clientHeight || 1);
    document.getElementById('progress').style.width = (p*100).toFixed(2)+'%';
  }}, {{passive:true}});
  spy();
  // search filter
  const inp = document.getElementById('toc-search');
  inp.addEventListener('input', () => {{
    const q = inp.value.trim().toLowerCase();
    links.forEach(a => {{
      const hit = !q || a.textContent.toLowerCase().includes(q);
      a.parentElement.style.display = hit ? '' : 'none';
    }});
    document.querySelectorAll('.toc-group').forEach(g => {{
      const anyVisible = Array.from(g.querySelectorAll('li')).some(li => li.style.display !== 'none');
      g.style.display = anyVisible ? '' : 'none';
    }});
  }});
  // mobile drawer
  const btn = document.getElementById('menu-btn'), scrim = document.getElementById('scrim');
  function toggle(open) {{ document.body.classList.toggle('nav-open', open); }}
  btn.addEventListener('click', () => toggle(!document.body.classList.contains('nav-open')));
  scrim.addEventListener('click', () => toggle(false));
  links.forEach(a => a.addEventListener('click', () => toggle(false)));
  // back to top
  const topBtn = document.getElementById('top-btn');
  window.addEventListener('scroll', () => {{ topBtn.style.display = window.scrollY > 800 ? 'block' : 'none'; }}, {{passive:true}});
  topBtn.addEventListener('click', () => window.scrollTo({{top:0,behavior:'smooth'}}));
}})();
</script>
</body>
</html>'''

open('/home/scott/morrowind-guide/index.html', 'w', encoding='utf-8').write(page)
print('index.html written:', len(page), 'bytes')
