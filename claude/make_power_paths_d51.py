"""C3: SIN1 p.127(+24V)/p.128(0V) D51 ID캐비닛 24V 급전(S51 SDS 파트 → ID_T 단자대 → MELDE2 보드)을 power-paths.json 에 추가/교체.
id 기준 추가/교체. 시드 px = 80dpi 이미지 기준. --preview 이면 색입힌 png 저장."""
import pymupdf, json, sys, os
PDF = r"C:/Users/김영추/Desktop/2호선 PDF 자료/SICAS HW Design White_SIN1.pdf"
doc = pymupdf.open(PDF)
s = 80 / 72
def build(pageno, seeds, supply):
    pg = doc[pageno - 1]; W, H = pg.rect.width, pg.rect.height
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
    r = set()
    for x, y in seeds:
        x, y = x / s, y / s
        r |= {f(i) for i, (a, b) in enumerate(segs) if min(a.x, b.x) - 3 <= x <= max(a.x, b.x) + 3 and min(a.y, b.y) - 3 <= y <= max(a.y, b.y) + 3}
    ybus = 256 / s
    out = []
    for i in range(n):
        if f(i) not in r: continue
        a, b = segs[i]
        if abs(a - b) < 8 or (abs(a.y - b.y) < .3 and a.y > ybus + 5): continue  # 문자 획·케이블명 밑줄 제외
        if abs(a.x - b.x) < .3:   # 세로: 인입선(x<400px)은 위로, 가지는 버스 위=위 / 아래=아래
            mid = (a.y + b.y) / 2
            up = a.x < 400 / s or mid < ybus
            q = (a, b) if (a.y > b.y) == up else (b, a)   # up: 시작=아래
        elif abs(a.y - b.y) < .3:  # 가로: 24V=오른쪽(버스 바깥으로)
            q = (a, b) if (a.x < b.x) else (b, a)
        else: continue
        if not supply: q = (q[1], q[0])
        out.append([round(q[0].x / W, 4), round(q[0].y / H, 4), round(q[1].x / W, 4), round(q[1].y / H, 4)])
    return pg, W, H, out
def pt(txt, x, y, W, H): return [txt, round(x / s / W, 4), round(y / s / H, 4)]
seeds = [(316, 600), (390, 700), (700, 256)]
pg1, W, H, a = build(127, seeds, True)
pg2, _, _, b = build(128, seeds, False)
print('p127', len(a), 'p128', len(b), file=sys.stderr)
D = "SICAS_HW_Design_SIN1"
parts = lambda: [pt("SDS 파트 전원 인입 D51.101 (24V DC_1)", 250, 640, W, H), pt("SDS 파트 전원 인입 D51.102 (24V DC_2)", 420, 700, W, H),
                 pt("ID_T 단자대 (MELDE2 급전 버스)", 720, 235, W, H)]
cont = "인입 케이블 D51.101/102(X* 51_S1+/S2+, S51 캐비닛 쪽)의 원천 단자는 이 도면에 없음(확인필요). MELDE2 이후 각 보드 전원은 03.13.01(p.129~)·03.13.02(p.177~)"
new = [{"id": "PWR_SICAS_D51_24V", "title": "SICAS D51 ID캐비닛 24V DC 급전 (SDS 전원 파트 → ID_T 단자대 → MELDE2 X2/X4 보드, SIN1+SIN2)", "station": "SIN1", "verified": False,
        "steps": [{"doc": D, "page": 127, "segments": a, "parts": parts(), "label": "24V DC_1/2 인입(붉은선) → ID_T 버스 → MELDE2 (0V는 다음 쪽)", "continues": cont},
                  {"doc": D, "page": 128, "segments0": b, "segments": [], "parts": parts(), "label": "0V 복귀(파랑) ← MELDE2 ← ID_T 버스 ← 24V DC_1/2 RL", "continues": cont}]}]
ids = {x['id'] for x in new}
fp = os.path.join(os.path.dirname(__file__), '..', 'power-paths.json')
P = json.load(open(fp, encoding='utf-8'))
P = [x for x in P if x['id'] not in ids] + new
json.dump(P, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
if '--preview' in sys.argv:
    for pg, L, col, nm in ((pg1, a, (1, 0, 0), 'p127'), (pg2, b, (0, 0, 1), 'p128')):
        sh = pg.new_shape()
        for x1, y1, x2, y2 in L: sh.draw_line((x1 * W, y1 * H), (x2 * W, y2 * H)); sh.finish(color=col, width=2)
        sh.commit(); pg.get_pixmap(dpi=70).save(os.path.join(os.environ.get('TEMP', '.'), f'c3_{nm}.png'))
