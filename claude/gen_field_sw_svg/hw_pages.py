import os, sys, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
BASE = r'C:\Users\김영추\Desktop\2호선 PDF 자료'
stn, pages = sys.argv[1], [int(x) for x in sys.argv[2:]]
f = [x for x in os.listdir(BASE) if x.startswith('SICAS HW Design White_' + stn)][0]
d = pymupdf.open(os.path.join(BASE, f))
for p in pages:
    t = d[p - 1].get_text().replace('\n', ' | ')
    print('=== ', f, 'p', p, len(t))
    print(t[:1800])
