"""FTGS 궤도회로 전원 대표 경로(F51 첫 회로) 생성 후 power-paths.json 에 추가/교체.
p.109/113/117/121/125 는 선 구조 동일(세션 C 비교) → 같은 좌표 재사용, 캐비닛·회로명·단자번호만 페이지에서 추출."""
import pymupdf, json, re
PDF = r"C:/Users/김영추/Desktop/2호선 PDF 자료/SICAS HW Design White_SIN1.pdf"
PAGES = [109, 113, 117, 121, 125]
pg = pymupdf.open(PDF); s = 72 / 100  # 100dpi px -> pt
def vlines(p):
    return [(a.x, min(a.y, b.y), max(a.y, b.y)) for x in p.get_drawings() for it in x['items'] if it[0] == 'l'
            for a, b in [(it[1], it[2])] if abs(a.x - b.x) < .3 and abs(a.y - b.y) > 5]
def hline_y(p, x0, x1):
    for x in p.get_drawings():
        for it in x['items']:
            if it[0] == 'l' and abs(it[1].y - it[2].y) < .3 and min(it[1].x, it[2].x) <= x0 * s + 1 and max(it[1].x, it[2].x) >= x1 * s - 1 and it[1].y > 700:
                return it[1].y
base = pg[PAGES[0] - 1]; W, H = base.rect.width, base.rect.height
def snap(vs, px):  # px 근처 세로선의 x, 위/아래 끝
    c = [v for v in vs if abs(v[0] - px * s) < 4]; L = {}
    for v in c: L[round(v[0], 1)] = L.get(round(v[0], 1), 0) + v[2] - v[1]
    x = max(L, key=L.get); c = [v for v in c if round(v[0], 1) == x]; return c[0][0], min(v[1] for v in c), max(v[2] for v in c)
vs = vlines(base); xp, yp0, yp1 = snap(vs, 316); xn, yn0, yn1 = snap(vs, 433); yb = hline_y(base, 316, 433)
n = lambda x, y: [round(x / W, 4), round(y / H, 4)]
seg = lambda a, b: n(*a) + n(*b)
segs = [seg((xp, 70 * s), (xp, yb)), seg((xp, yb), (xn, yb)), seg((xn, yb), (xn, 60 * s))]  # +24V 아래로 → TR → 0V 위로
# 페이지별 인스턴스: 같은 구조인지 검증 + 캐비닛/회로명/단자번호 추출
inst = {}
for pn in PAGES:
    p = pg[pn - 1]; v = vlines(p)
    def cov(x, y0, y1):  # 세로선 조각들이 [y0,y1] 를 (부품 틈 <=40pt 허용) 덮는가
        c = sorted((q[1], q[2]) for q in v if abs(q[0] - x) < .5); y = y0
        for a, b in c:
            if a <= y + 40: y = max(y, b)
        return y >= y1 - 1
    ok = cov(xp, 100 * s, yb - 5) and cov(xn, 165 * s, yb - 5)
    w = p.get_text('words'); pick = lambda x0, y0, x1, y1: [q[4] for q in w if x0 * s <= q[0] <= x1 * s and y0 * s <= q[1] <= y1 * s]
    cab = re.findall(r'\+F\d+', ' '.join(pick(80, 230, 400, 300)))
    ckt = [t for t in pick(316, 385, 410, 415) if '234' in t]
    term = [t for t in pick(312, 795, 340, 825) + pick(430, 795, 460, 825) if t.isdigit()]
    inst[str(pn)] = {"cab": (cab or ['?'])[0][1:], "ckt": (ckt or ['?'])[0], "term": term, "sameStructure": ok}
print(inst)
path = {"id": "PWR_FTGS_TRACK_C1", "title": "FTGS 궤도회로 전원 (ID캐비닛 24V → 퓨즈 → 릴레이접점 → 단자 → TR → 0V), 첫 회로 대표", "station": "SIN1",
        "verified": False, "steps": [{"doc": "SICAS_HW_Design_SIN1", "page": PAGES[0], "pages": PAGES, "segments": segs,
        "label": "+24V DC(F21 0.125A) → 릴레이접점 → ID단자 → TR → 0V DC 복귀", "instances": inst,
        "continues": "ID캐비닛 D51 24V 공급원·릴레이연동 TR 이후는 미확인"}]}
P = json.load(open('power-paths.json', encoding='utf-8')); P = [x for x in P if x['id'] != path['id']] + [path]
json.dump(P, open('power-paths.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
