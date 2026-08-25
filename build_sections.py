#!/usr/bin/env python3
"""Parse tarvis79's Morrowind FAQ raw text into sections and build index.html."""
import re, html, json

SRC = '/home/scott/morrowind-guide/raw_guide.txt'
OUT = '/home/scott/morrowind-guide/index.html'

text = open(SRC, encoding='utf-8').read()
lines = text.split('\n')
pat = re.compile(r'\{([A-Z]{3}\d{3})\}')

# --- collect anchor occurrences ---
occ = {}
for i, l in enumerate(lines):
    for m in pat.finditer(l):
        occ.setdefault(m.group(1), []).append(i)

# TOC order = first-occurrence order of codes in the table of contents region (lines 0..130)
toc_order = []
for i in range(0, 130):
    for m in pat.finditer(lines[i]):
        c = m.group(1)
        if c not in toc_order:
            toc_order.append(c)

# Body start line for each code = LAST occurrence (except ITM001 which has no body)
body_start = {c: occ[c][-1] for c in toc_order if len(occ[c]) >= 2}

# Sort sections by body line number
ordered = sorted(body_start.items(), key=lambda kv: kv[1])

def extract_title(start):
    """Find the boxed banner above the anchor line and take its center text."""
    # locate the banner: nearest 'o===' line above start
    top = None
    for j in range(start - 1, max(0, start - 15), -1):
        if lines[j].strip().startswith('o==='):
            top = j
            break
    if top is None or top + 3 > start:
        return None
    # collect the lines between the two border rows, strip pipes/tabs
    inner = []
    for j in range(top + 1, start):
        l = lines[j].strip()
        if set(l) <= set('=o| \t'):
            continue
        clean = re.sub(r'\{[A-Z]{3}\d{3}\}', '', l.strip('|')).strip()
        if clean:
            inner.append(clean)
    if not inner:
        return None
    # skip pure blank-box rows; join meaningful rows (banner usually has a
    # filler row of spaces then the title)
    title_rows = [r for r in inner if r]
    return ' '.join(title_rows) if title_rows else None

sections = []
for idx, (code, start) in enumerate(ordered):
    end = ordered[idx + 1][1] if idx + 1 < len(ordered) else len(lines)
    # back up to include the banner box above the anchor line
    bstart = start
    for j in range(start - 1, max(0, start - 15), -1):
        if lines[j].strip().startswith('o==='):
            bstart = j
            break
    raw = '\n'.join(lines[bstart:end]).rstrip() + '\n'
    title = extract_title(start) or code
    sections.append({'code': code, 'title': title.strip(), 'start': bstart, 'raw': raw})

# Grouping for TOC
groups = [
    ('Introduction', ['INT001', 'INT002', 'INT003', 'INT004', 'INT005', 'INT006', 'INT007', 'INT008', 'INT009']),
    ('Character Creation', ['CHR001','CHR002','CHR003','CHR004','CHR005','CHR006','CHR007','CHR008','CHR009','CHR010']),
    ('Spells', ['SPL001','SPL002','SPL003','SPL004','SPL005','SPL006','SPL007']),
    ('General Tips', ['TIP001']),
]
wlk = [c for c, _ in ordered if c.startswith('WLK')]
groups.append(('Main Walkthrough', wlk))
tail = [c for c, _ in ordered if c.startswith(('BST', 'UPD'))]
if tail:
    groups.append(('Appendices', tail))

grouped_codes = [c for _, cs in groups for c in cs]
assert grouped_codes == [c for c, _ in ordered], (set(grouped_codes) ^ set(c for c,_ in ordered))

# Titles for WLK subsections come out of banners; sanity print
for s in sections[:12]:
    print(s['code'], '|', s['title'][:60], '| lines:', s['raw'].count('\n'))
print('...')
print('TOTAL sections:', len(sections))

json.dump(sections, open('/home/scott/morrowind-guide/sections.json', 'w'), indent=0)
