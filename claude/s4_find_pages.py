"""기준 역(SIN1) 쪽 <-> 대상 역 쪽 후보 탐색. 텍스트(숫자->#, 역명 제거) Jaccard + 선 좌표 일치율.
사용: python s4_find_pages.py EUL GCD GYO -> s4_pages_<역>.json (쪽 후보 3개씩) + 한 줄 요약."""
import pymupdf, json, re, sys, os
from stn import ST
D = os.path.dirname(os.path.abspath(__file__))
REF = {"N": [188], "FTGS": [109, 113, 117, 121, 125]}
def norm(t, stn):
    t = re.sub(r'[A-Z]{3}\d?', lambda m: '' if m.group(0)[:3] in ('EUL','GCD','GYO','SIN','SON','SNU','SPO','SOL','HON','SCD','YAN') else m.group(0), t)
    return set(re.sub(r'\d+', '#', w) for w in re.findall(r'\S+', t))
def lines(p):
    return {(round(it[1].x), round(it[1].y), round(it[2].x), round(it[2].y)) for d in p.get_drawings() for it in d['items'] if it[0] == 'l'}
def info(pdf):
    doc = pymupdf.open(pdf); return [(norm(p.get_text(), ''), lines(p), p.rect.width, p.rect.height) for p in doc]
def jac(a, b): return len(a & b) / max(1, len(a | b))
def run(stn):
    ref = info("C:/Users/김영추/Desktop/2호선 PDF 자료/" + ST['SIN1']['sicas'])
    tgt = info("C:/Users/김영추/Desktop/2호선 PDF 자료/" + ST[stn]['sicas'])
    out = {}
    for key, pages in REF.items():
        for rp in pages:
            r = ref[rp - 1]; c = []
            for i, t in enumerate(tgt):
                j = jac(r[0], t[0])
                if j < .3: continue
                L = len(r[1] & t[1]) / max(1, len(r[1] | t[1]))
                c.append((round(j, 2), round(L, 2), i + 1))
            out['%s:%d' % (key, rp)] = sorted(c, reverse=True)[:3]
    json.dump(out, open(os.path.join(D, 's4_pages_%s.json' % stn), 'w'), ensure_ascii=False)
    for k, v in out.items(): print(stn, k, v)
if __name__=="__main__":
    for s in sys.argv[1:]: run(s)
