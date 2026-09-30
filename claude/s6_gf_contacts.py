"""GF 계전기(Relay module S25533-B36-A7) 접점 → 플러그 → ID랙 단자 배선을 SICAS FTGS 캐비닛 후면 도면(FTGS 쪽 P-2, P-1)에서 회로별로 추출.
사용: python s6_gf_contacts.py 역... (기본 전체) -> ../gf-contacts.json. 출력=역별 한 줄(쪽 수/회로 수/검증 실패)."""
import pymupdf, re, json, sys, os
from stn import ST
R = "C:/Users/김영추/Desktop/2호선 PDF 자료/"
CK = re.compile(r'^[A-Z]{0,2}\d{3}-\d+[A-Z]{0,2}$'); ID = re.compile(r'^[A-Z]{1,2}\d{1,3}[a-z]\d{1,2}$'); KC = re.compile(r'^K1[12]-\d$'); PIN = re.compile(r'^[AB]\d{1,2}$')
def extract(pg, known=()):
    ws = pg.get_text('words'); ctr = lambda w: ((w[0] + w[2]) / 2, (w[1] + w[3]) / 2)
    labels = [(ctr(w), w[4]) for w in ws if re.fullmatch(r'M\d\d', w[4]) and ctr(w)[0] < 260]
    ck = [w for w in ws if CK.match(w[4]) or w[4] in known]
    xs = []
    for w in sorted(ck, key=lambda w: ctr(w)[0]):
        if not xs or ctr(w)[0] - xs[-1] > 30: xs.append(ctr(w)[0])
    out = []
    for cx in xs:
        col = sorted([w for w in ws if abs(ctr(w)[0] - cx) < 22 and w[1] > 60], key=lambda w: ctr(w)[1]); chain = []; name = None
        for w in col:
            t = w[4]
            if CK.match(t) or t in known: name = name or t
            elif KC.match(t): chain.append(t)
            elif ID.match(t): chain.append(t)
            elif PIN.match(t):
                l = [lb for lb in labels if abs(lb[0][1] - ctr(w)[1]) < 12]
                chain.append((l[0][1] + ' ' if l else '') + t)
        if name: out.append({'ckt': name, 'chain': chain})
    return out
PP = {x['id']: x for x in json.load(open('../power-paths.json', encoding='utf-8'))}
def known_ckts(stn):
    p = PP.get('PWR_FTGS_TRACK_C1' + ('' if stn == 'SIN1' else '_' + stn))
    return {c['ckt'] for I in p['steps'][0]['instances'].values() for c in I['circuits']} if p else set()
res = {}
for stn in (sys.argv[1:] or list(ST)):
    c = ST[stn]
    if not c['paths'].get('FTGS'): continue
    d = pymupdf.open(R + c['sicas']); sets = []; kn = known_ckts(stn)
    for pn in range(1, len(d) + 1):
        tx = d[pn - 1].get_text()
        if 'Relay module' in tx and 'S25533-B36-A7' in tx:
            cs = extract(d[pn - 1], kn)
            if cs: sets.append({'page': pn, 'circuits': cs})
    res[stn] = sets; u = {x['ckt'] for s in sets for x in s['circuits']}
    print(stn, 'pages', [s['page'] for s in sets][:20], 'circuits', len(u), 'known(power-path)', len(kn), 'known-not-found', len(kn - u), flush=True)
json.dump(res, open('../gf-contacts.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
