#!/usr/bin/env python3
"""Final sectioner: splits raw guide text at anchor lines, assigning shared
banner rows to the correct sections without loss or duplication."""
import json, re

lines = open('/home/scott/morrowind-guide/raw_guide.txt', encoding='utf-8').read().split('\n')
pat = re.compile(r'\{([A-Z]{3}\d{3})\}')
occ = {}
for i, l in enumerate(lines):
    for m in pat.finditer(l):
        occ.setdefault(m.group(1), []).append(i)

toc_order = []
for i in range(130):
    for m in pat.finditer(lines[i]):
        c = m.group(1)
        if c not in toc_order:
            toc_order.append(c)

body_start = {c: occ[c][-1] for c in toc_order if len(occ[c]) >= 2}
ordered = sorted(body_start.items(), key=lambda kv: kv[1])
titles_raw = json.load(open('/tmp/titles.json'))

def enclosing_box(s):
    """Anchor line itself sits inside a boxed banner: return its top border."""
    if not lines[s].strip().startswith('|'):
        return None
    top = bot = None
    for j in range(s - 1, max(0, s - 6), -1):
        if lines[j].strip().startswith('o==='):
            top = j
            break
    for j in range(s + 1, min(len(lines), s + 6)):
        if lines[j].strip().startswith('o==='):
            bot = j
            break
    return top if (top is not None and bot is not None) else None

def banner_top(s):
    """Top border of the boxed banner governing this anchor; else None."""
    eb = enclosing_box(s)
    if eb is not None:
        return eb
    bot = None
    for j in (s - 1, s - 2):
        if j >= 0 and lines[j].strip().startswith('o==='):
            bot = j
            break
    if bot is None:
        return None
    for j in range(bot - 1, max(0, bot - 10), -1):
        if lines[j].strip().startswith('o==='):
            return j
    return None

def clean_title(code):
    return re.sub(r'\s+', ' ', ' '.join(titles_raw[code]).replace('|', '')).strip()

# Compute each section's intended start (incl. banner) and its anchor line.
meta = []
for idx, (code, start) in enumerate(ordered):
    bt = banner_top(start)
    meta.append({'id': code, 'title': clean_title(code),
                 'anchor': start, 'want_start': bt if bt is not None else start})

# Resolve overlaps: if this section's want_start is before the previous
# section's anchor, the rows [want_start, prev_anchor) belong to THIS section's
# banner, and the previous section must end at want_start... no — previous ends
# at this section's want_start only when the banner rows were previously inside
# prev's range. Assign each row to exactly one section:
bounds = []
for idx, m_ in enumerate(meta):
    s = m_['want_start']
    if idx > 0 and s < meta[idx - 1]['anchor']:
        # banner of current section intrudes into prev's tail: give it to current,
        # prev ends here.
        pass
    bounds.append(s)
# clip: each section runs from its bound to next bound (or EOF)
sections = []
for idx, m_ in enumerate(meta):
    b = bounds[idx]
    e = bounds[idx + 1] if idx + 1 < len(meta) else len(lines)
    raw = '\n'.join(lines[b:e]).rstrip('\n') + '\n'
    sections.append({'id': m_['id'], 'title': m_['title'], 'text': raw})

total = sum(len(s['text']) for s in sections)
orig = len('\n'.join(lines))
print('sections:', len(sections), 'chars:', total, 'original:', orig)

json.dump(sections, open('/home/scott/morrowind-guide/sections.json', 'w'))

# spot checks
for cid in ('BST001', 'UPD001', 'WLK001', 'WLK002', 'CHR002'):
    s = next(x for x in sections if x['id'] == cid)
    print('=====', cid, '|', s['title'])
    print(repr(s['text'][:180]))
