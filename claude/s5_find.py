"""S5: 나머지 역 쪽 매핑. 기준(SIN1) N=188, FTGS=109,113,117,121,125 대비 Jaccard+선좌표. 결과 s5_pages.json, 역당 한 줄.
사용: python s5_find.py HON SCD SNU1 ..."""
import pymupdf, json, re, sys, collections
from stn import ST
from s4_find_pages import norm, lines, jac
P = "C:/Users/김영추/Desktop/2호선 PDF 자료/"
ref = pymupdf.open(P + ST['SIN1']['sicas'])
R = {k: (norm(ref[k - 1].get_text(), ''), lines(ref[k - 1])) for k in (188, 109, 113, 117, 121, 125)}
out = {}
for s in sys.argv[1:]:
    d = pymupdf.open(P + ST[s]['sicas']); cand = {'N': [], 'F': []}; cab = collections.Counter()
    for i, p in enumerate(d):
        t = p.get_text(); cab.update(re.findall(r'\+[SDP]\d{2}\b', t)); n = norm(t, '')
        if jac(n, R[188][0]) >= .6:
            l = lines(p); cand['N'].append((round(jac(n, R[188][0]), 2), round(len(l & R[188][1]) / max(1, len(l | R[188][1])), 2), i + 1))
        f = max(jac(n, R[k][0]) for k in (109, 113, 117, 121, 125))
        if f >= .75: cand['F'].append(i + 1)
    N = sorted(cand['N'], reverse=True)[:2]
    out[s] = {'N': N, 'F': cand['F'], 'cab': cab.most_common(5)}
    print(s, 'N', N, 'FTGS', cand['F'], 'cab', [c for c, _ in cab.most_common(3)], flush=True)
json.dump(out, open('s5_pages.json', 'w', encoding='utf-8'), ensure_ascii=False)
