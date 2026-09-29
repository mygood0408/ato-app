"""FTGS 궤도회로 전원 대표 경로(첫 회로) 생성 후 power-paths.json 에 추가/교체.
p.109/113/117/121/125 는 선 구조 동일(sameStructure 로 검증) → 같은 좌표 재사용.
페이지별: 캐비닛, 회로 5개(회로명·퓨즈·ID단자쌍) 를 텍스트에서 추출. 좌표 px = 100dpi 이미지 기준."""
import pymupdf, json, re, sys
from stn import STN as _S, ST, PDF as _P, CAB, DCAB, pid, page
# 사용: python make_power_paths_ftgs.py [역접미사 | --station 역]  (쪽 목록은 stations.json paths.FTGS)
STN = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ST else _S
PDF = _P if STN == _S else "C:/Users/김영추/Desktop/2호선 PDF 자료/" + ST[STN]['sicas']
PAGES = ST[STN]['paths'].get('FTGS') or (print('확인필요: %s FTGS 쪽 미지정' % STN, file=sys.stderr) or sys.exit(0))
pg = pymupdf.open(PDF); s = 72 / 100
X24, X0, PITCH = 316, 433, 236  # 첫 회로 +24V/0V 세로선 px, 회로 간격 px
def vlines(p):
    return [(a.x, min(a.y, b.y), max(a.y, b.y)) for x in p.get_drawings() for it in x['items'] if it[0] == 'l'
            for a, b in [(it[1], it[2])] if abs(a.x - b.x) < .3 and abs(a.y - b.y) > 5]
def hline_y(p, x0, x1):
    for x in p.get_drawings():
        for it in x['items']:
            if it[0] == 'l' and abs(it[1].y - it[2].y) < .3 and min(it[1].x, it[2].x) <= x0 * s + 1 and max(it[1].x, it[2].x) >= x1 * s - 1 and it[1].y > 700:
                return it[1].y
base = pg[PAGES[0] - 1]; W, H = base.rect.width, base.rect.height
def snap(vs, px):
    c = [v for v in vs if abs(v[0] - px * s) < 4]; L = {}
    for v in c: L[round(v[0], 1)] = L.get(round(v[0], 1), 0) + v[2] - v[1]
    x = max(L, key=L.get); return x
def words(p, x0, y0, x1, y1):
    return [q for q in p.get_text('words') if x0 * s <= q[0] <= x1 * s and y0 * s <= q[1] <= y1 * s]
vs = vlines(base); xp = snap(vs, X24); xn = snap(vs, X0); yb = hline_y(base, X24, X0)
n = lambda x, y: [round(x / W, 4), round(y / H, 4)]
seg = lambda a, b: n(*a) + n(*b)
seg24 = [seg((xp, 70 * s), (xp, yb)), seg((xp, yb), (xn, yb))]  # +24V 아래로 → TR → 바닥에서 0V 열로
seg0 = [seg((xn, yb), (xn, 60 * s))]                              # 0V 위로 복귀
# 경로 위 부품 이름표(대표 페이지 단어 위치): (표시글, 단어검색 bbox px)
parts = []
for txt, pat, box in (("퓨즈 {fuse} 0.125A", r'F2\d', (X24 - 45, 235, X24, 255)), ("릴레이접점 AR1.2", r'AR1\.2', (X24 - 40, 385, X24 + 5, 410)),
                      ("릴레이접점 AR1.1", r'AR1\.1', (X24 - 40, 590, X24 + 5, 615)), ("TR (릴레이연동)", r'TR', (X24 - 40, 955, X24 - 5, 985))):
    for q in words(base, *box):
        if re.fullmatch(pat, q[4]):
            parts.append([txt.replace('{fuse}', q[4]), round(q[0] / W, 4), round(q[1] / H, 4)]); break
def inst_of(pn):
    p = pg[pn - 1]; v = vlines(p)
    def cov(x, y0, y1):
        c = sorted((q[1], q[2]) for q in v if abs(q[0] - x) < .5); y = y0
        for a, b in c:
            if a <= y + 40: y = max(y, b)
        return y >= y1 - 1
    ok = cov(xp, 100 * s, yb - 5) and cov(xn, 165 * s, yb - 5)
    cab = re.findall(r'\+F\d+', ' '.join(q[4] for q in words(p, 80, 230, 400, 300)))
    ckts = []
    for k in range(5):
        a, b = X24 + PITCH * k, X0 + PITCH * k
        ck = [q[4] for q in words(p, a, 385, a + 95, 415) if re.fullmatch(r'[A-Z]?\d{3}-[\w-]+', q[4])]
        fu = [q[4] for q in words(p, a - 45, 235, a, 255) if re.fullmatch(r'F2\d', q[4])]
        tm = [q[4] for q in words(p, a - 4, 795, a + 30, 825) + words(p, b - 4, 795, b + 30, 825) if q[4].isdigit()]
        ckts.append({"ckt": (ck or ['?'])[0], "fuse": (fu or ['?'])[0], "term": tm})
    return {"cab": (cab or ['?'])[0][1:], "circuits": ckts, "sameStructure": ok}
inst = {str(pn): inst_of(pn) for pn in PAGES}
for k, v in inst.items(): print(k, v['cab'], v['sameStructure'], [c['ckt'] + ':' + '/'.join(c['term']) for c in v['circuits']])
path = {"id": pid("PWR_FTGS_TRACK_C1", STN), "title": "FTGS 궤도회로 전원 (ID캐비닛 24V → 퓨즈 → 릴레이접점 → 단자 → TR → 0V), 첫 회로 대표", "station": STN,
        "verified": False, "steps": [{"doc": "SICAS_HW_Design_" + STN, "page": PAGES[0], "pages": PAGES, "segments": seg24, "segments0": seg0, "parts": parts,
        "label": "+24V DC → 퓨즈 → 릴레이접점 → ID단자 → TR → 0V DC 복귀", "instances": inst,
        "continues": "ID캐비닛 D51 24V 공급원·TR 이후 릴레이연동 쪽은 미확인"}]}
P = json.load(open('power-paths.json', encoding='utf-8')); P = [x for x in P if x['id'] != path['id']] + [path]
json.dump(P, open('power-paths.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('parts', [p[0] for p in parts])
