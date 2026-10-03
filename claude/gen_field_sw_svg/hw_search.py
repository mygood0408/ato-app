import os, re, sys, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
BASE = r'C:\Users\김영추\Desktop\2호선 PDF 자료'
files = sorted(f for f in os.listdir(BASE) if f.startswith('SICAS HW Design White_'))
pat = re.compile(sys.argv[1])
for f in files:
    d = pymupdf.open(os.path.join(BASE, f))
    hits = []
    for i, p in enumerate(d):
        t = p.get_text()
        if pat.search(t):
            hits.append(i + 1)
    print(f, len(d), 'pages; hits:', hits[:30])
