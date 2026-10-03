"""SICAS HW Design 전 역: DEWEMO-W 선로전환기 쪽 찾기 (쪽번호·선로전환기 이름·단동/쌍동). 출력은 요약만."""
import os, re, sys, json, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
BASE = r'C:\Users\김영추\Desktop\2호선 PDF 자료'
out = {}
for f in sorted(os.listdir(BASE)):
    if not f.startswith('SICAS HW Design White_'):
        continue
    stn = f[len('SICAS HW Design White_'):-4]
    d = pymupdf.open(os.path.join(BASE, f))
    pages = []
    for i, p in enumerate(d):
        t = p.get_text()
        if 'DEWEMO' not in t or 'Plug: X3' not in t.replace('Plug:X3', 'Plug: X3'):
            continue
        names = sorted(set(re.findall(r'Points\s+([A-Z0-9]+_P\d+[AB]?(?:/[A-Z0-9_P]+[AB])?)', t)))
        dbl = 'Point Machine B' in t
        pages.append((i + 1, names[:2], 'D' if dbl else 'S'))
    out[stn] = pages
    print(stn, len(d), len(pages), [(a, b[0] if b else '', c) for a, b, c in pages][:40])
json.dump(out, open('claude/_scan.json', 'w', encoding='utf-8'), ensure_ascii=False)
