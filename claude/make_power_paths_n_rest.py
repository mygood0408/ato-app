"""C2: SIN1 p.188 24V 주변기기(단자 40~49) 및 230V 팬(단자 66~81) 전원 경로를 power-paths.json 에 추가/교체.
p.188 스크립트와 같은 net 묶기(T접점) 사용. 시드 px = 100dpi 이미지 기준. 인자: --preview 이면 색입힌 png 저장."""
import pymupdf, json, sys, os
PDF = r"C:/Users/김영추/Desktop/2호선 PDF 자료/SICAS HW Design White_SIN1.pdf"
PAGE = 188
pg = pymupdf.open(PDF)[PAGE - 1]
W, H = pg.rect.width, pg.rect.height
s = 100 / 72
segs = [(it[1], it[2]) for dr in pg.get_drawings() for it in dr['items'] if it[0] == 'l']
n = len(segs); par = list(range(n))
def f(i):
    while par[i] != i: par[i] = par[par[i]]; i = par[i]
    return i
def on(pt, a, b, t=0.6):
    return (min(a.x, b.x) - t <= pt.x <= max(a.x, b.x) + t and min(a.y, b.y) - t <= pt.y <= max(a.y, b.y) + t
            and abs((b.x - a.x) * (pt.y - a.y) - (b.y - a.y) * (pt.x - a.x)) <= t * max(1, ((b.x-a.x)**2+(b.y-a.y)**2) ** .5))
grid = {}
for i, (a, b) in enumerate(segs):
    for cx in range(int(min(a.x, b.x) // 10), int(max(a.x, b.x) // 10) + 1):
        for cy in range(int(min(a.y, b.y) // 10), int(max(a.y, b.y) // 10) + 1):
            grid.setdefault((cx, cy), []).append(i)
for cell in grid.values():
    for k, i in enumerate(cell):
        for j in cell[k + 1:]:
            (a, b), (c, d) = segs[i], segs[j]
            if any(on(p, x, y) for p, x, y in ((a, c, d), (b, c, d), (c, a, b), (d, a, b))): par[f(i)] = f(j)
# 교차 점프(p.188과 동일): 같은 높이 가로선 끝점 사이 <=30pt를 세로선이 가로지르면 이어진 선
hz = [(i, q) for i, q in enumerate(segs) if abs(q[0].y - q[1].y) < .3]
vt = [q for q in segs if abs(q[0].x - q[1].x) < .3]
for i, a in hz:
    for j, b in hz:
        if i >= j or abs(a[0].y - b[0].y) > .3: continue
        for p in a:
            for q in b:
                g = sorted((p.x, q.x))
                if 0 < g[1] - g[0] <= 30 and any(g[0] < v[0].x < g[1] and min(v[0].y, v[1].y) < p.y < max(v[0].y, v[1].y) for v in vt):
                    segs.append((p, q)); par.append(len(par)); n += 1; par[f(i)] = f(n - 1); par[f(j)] = f(n - 1)
def orient(q, supply, right=False):  # 60V: 세로=위, 가로=왼쪽(인입) / 0V 복귀: 반대. right=True: 가로=오른쪽(퓨즈→필터 구간)
    x1, y1, x2, y2 = q
    v = abs(x1 - x2) < 1e-4
    flip = (y1 < y2) if v else (x1 < x2) != right
    return [x2, y2, x1, y1] if flip == supply else q
def net(seeds, supply, right=False):
    r = set()
    for x, y in seeds:
        x, y = x / s, y / s
        r |= {f(i) for i, (a, b) in enumerate(segs) if min(a.x, b.x) - 3 <= x <= max(a.x, b.x) + 3 and min(a.y, b.y) - 3 <= y <= max(a.y, b.y) + 3}
    return [orient([round(segs[i][0].x / W, 4), round(segs[i][0].y / H, 4), round(segs[i][1].x / W, 4), round(segs[i][1].y / H, 4)], supply, right)
            for i in range(n) if f(i) in r]
def pt(txt, x, y): return [txt, round(x / s / W, 4), round(y / s / H, 4)]
Y = 743  # 하단 케이블 선 위 (100dpi px)
def mk(pid, title, plus, minus, label, cont, parts):
    a, b = net([(x, Y) for x in plus], True), net([(x, Y) for x in minus], False)
    xs = [x / s / W for x in plus + minus]
    def clean(L):  # 하단 실드(타원)·구분 점선·PE선이 net에 붙으므로: 하단(>0.5H)은 시드 x의 세로선만 남김
        return [q for q in L if (q[1] + q[3]) / 2 < .5 or (abs(q[0] - q[2]) < 1e-4 and min(abs(q[0] - x) for x in xs) < .004)]
    a, b = clean(a), clean(b)
    print(pid, 'supply segs', len(a), 'return segs', len(b), file=sys.stderr)
    return {"id": pid, "title": title, "station": "SIN1", "verified": False, "steps": [{"doc": "SICAS_HW_Design_SIN1", "page": PAGE,
            "segments": a, "segments0": b, "parts": parts, "label": label, "continues": cont}]}
new = [mk("PWR_SICAS_N_24V", "SICAS 캐비닛 S51 N레벨 24V DC 주변기기 (P51 전원반 → 단자 40~49, 퓨즈 4A/1A/6.3A)", [871, 1160], [950, 1240],
          "24V DC 인입(+ 붉은선) → 단자 40~49 퓨즈 (0V 복귀 파랑)", "단자 40~49 이후 각 주변기기 배선은 이 도면에 없음(확인필요)",
          [pt("24V DC 인입 (P51 전원반)", 830, 950), pt("단자 40~49 (4A×4, 1A×3, 6.3A×3)", 650, 270)]),
       mk("PWR_SICAS_N_230V", "SICAS 캐비닛 S51 N레벨 230V AC 팬 (P51 전원반 → 단자 66~81, fan1/fan2)", [1340], [1394],
          "230V AC L(붉은선) / N(파랑) → 단자 66~81 → 팬 1·2", "팬 fan1/fan2 및 fan failure(ID캐비닛 D51) 신호는 이 도면 표기만 있고 배선 근거 확인필요",
          [pt("230V AC 인입 (L/N)", 1330, 950), pt("단자 66~81 (fan1/fan2)", 1330, 270)])]
ids = {x['id'] for x in new}
P = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'power-paths.json'), encoding='utf-8'))
P = [x for x in P if x['id'] not in ids] + new
json.dump(P, open(os.path.join(os.path.dirname(__file__), '..', 'power-paths.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
if '--preview' in sys.argv:
    sh = pg.new_shape()
    for p_ in new:
        for col, k in (((1, 0, 0), 'segments'), ((0, 0, 1), 'segments0')):
            for x1, y1, x2, y2 in p_['steps'][0][k]: sh.draw_line((x1 * W, y1 * H), (x2 * W, y2 * H)); sh.finish(color=col, width=2)
    sh.commit()
    pg.get_pixmap(dpi=70).save(os.path.join(os.environ.get('TEMP', '.'), 'c2_preview.png'))
