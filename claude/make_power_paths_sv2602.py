"""C1: T52 G단자(SIN1 p.230) 60V DC 인입 → 단자 8/7 → 퓨즈 4A → Filter Z1~Z4 경로를 power-paths.json 에 추가/교체.
p.188 스크립트와 같은 net 묶기(T접점) 사용. 시드 px = 100dpi 이미지 기준. 인자: --preview 이면 색입힌 png 저장."""
import pymupdf, json, sys, os
PDF = r"C:/Users/김영추/Desktop/2호선 PDF 자료/SICAS HW Design White_SIN1.pdf"
PAGE = 230
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
def br(x1, y1, x2, y2): return [round(x1 / s / W, 4), round(y1 / s / H, 4), round(x2 / s / W, 4), round(y2 / s / H, 4)]
seg60 = net([(1200, 795), (1200, 883)], True)      # +60V1, +60V2 (인입선, 단자 8/7까지)
seg60 += [br(392, 795, 258, 795), br(392, 819, 258, 819)]   # 단자 8/7 통과(도면상 단자 기호로 끊긴 구간을 이음)
seg60 += net([(200, 760), (215, 805)], True, True)          # 단자 8/7 → 퓨즈 9~12 점퍼(왼쪽)
seg60 += [br(240, y, 410, y) for y in (704, 726, 749, 772)] # 퓨즈 4A ×4 통과(기호로 끊긴 구간)
seg60 += net([(440, 704), (500, 726), (560, 749), (630, 772)], True, True)   # 퓨즈 출력 → Filter Z1~Z4 화살표
seg0 = net([(1200, 827), (1200, 918)], False)      # 0V1, 0V2 (단자 4/3까지)
seg0 += [br(392, 892, 258, 892), br(392, 918, 258, 918)]
seg0 += net([(487, 760), (555, 760), (625, 760), (693, 760)], False)  # Filter 0V 선 → 단자 5~1 쪽
def pt(txt, x, y): return [txt, round(x / s / W, 4), round(y / s / H, 4)]
parts = [pt("60V 인입 (P51 전원반)", 1240, 806), pt("단자 8/7 (+60V1/2)", 262, 800), pt("퓨즈 4A ×4", 330, 703), pt("Filter Z1~Z4 →", 440, 625)]
print('60V segs', len(seg60), '0V segs', len(seg0), file=sys.stderr)
path = {"id": "PWR_SICAS_T52_60V", "title": "SICAS 캐비닛 T52 G단자 60V DC (P51 전원반 → 단자 → 퓨즈 4A → Filter Z1~Z4 → SV2602)", "station": "SIN1",
        "verified": False, "steps": [{"doc": "SICAS_HW_Design_SIN1", "page": PAGE, "segments": seg60, "segments0": seg0, "parts": parts,
        "label": "+60V DC 인입 → 단자 8/7 → 퓨즈 4A → Filter Z1~Z4 (0V 복귀 파랑)",
        "continues": "Filter Z1~Z4 이후 SV2602(p.224 랙 배치, 채널1·1·2·2)로의 배선은 도면에 없음(확인필요). T51(p.206)과는 X200/X203 플러그 8V 분배 주석만 있고 배선 없음"}]}
P = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'power-paths.json'), encoding='utf-8'))
P = [x for x in P if x['id'] != path['id']] + [path]
json.dump(P, open(os.path.join(os.path.dirname(__file__), '..', 'power-paths.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
if '--preview' in sys.argv:
    sh = pg.new_shape()
    for col, L in (((1, 0, 0), seg60), ((0, 0, 1), seg0)):
        for x1, y1, x2, y2 in L: sh.draw_line((x1 * W, y1 * H), (x2 * W, y2 * H)); sh.finish(color=col, width=2)
    sh.commit()
    pg.get_pixmap(dpi=100, clip=pymupdf.Rect(0, 0, W, H)).save(os.path.join(os.environ.get('TEMP', '.'), 'sv2602_preview.png'))
