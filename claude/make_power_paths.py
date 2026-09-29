"""SICAS HW Design p.188 (S51 Level N 전원)의 벡터 선을 net으로 묶어 power-paths.json 생성.
T자 접점(끝점이 다른 선 위)도 연결로 본다. 좌표는 페이지 크기 대비 0~1 비율."""
import pymupdf, json, sys, os
STN = os.environ.get("STN", "SIN1")  # SIN2: STN=SIN2 (N레벨 = p.107, 기존 json 에 id 기준 추가)
PDF = r"C:/Users/김영추/Desktop/2호선 PDF 자료/SICAS HW Design White_%s.pdf" % STN
PAGE = 188 if STN == "SIN1" else 107
pg = pymupdf.open(PDF)[PAGE - 1]
W, H = pg.rect.width, pg.rect.height
segs = []
for dr in pg.get_drawings():
    for it in dr['items']:
        if it[0] == 'l': segs.append((it[1], it[2]))
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
            if any(on(p, x, y) for p, x, y in ((a, c, d), (b, c, d), (c, a, b), (d, a, b))):
                par[f(i)] = f(j)
# 교차 점프: 같은 높이 가로선 끝점 사이(<=30pt)를 세로선이 가로지르면 선이 이어진 것으로 본다
hz = [(i, s_) for i, s_ in enumerate(segs) if abs(s_[0].y - s_[1].y) < .3]
vt = [s_ for s_ in segs if abs(s_[0].x - s_[1].x) < .3]
for i, a in hz:
    for j, b in hz:
        if i >= j or abs(a[0].y - b[0].y) > .3: continue
        for p in a:
            for q in b:
                g = sorted((p.x, q.x))
                if 0 < g[1] - g[0] <= 30 and any(g[0] < v[0].x < g[1] and min(v[0].y, v[1].y) < p.y < max(v[0].y, v[1].y) for v in vt):
                    segs.append((p, q)); par.append(len(par)); n += 1; par[f(i)] = f(n - 1); par[f(j)] = f(n - 1)
def orient(q):  # 흐름 방향: 세로선은 위쪽, 가로선은 왼쪽 (인입 → 단자)
    x1, y1, x2, y2 = q
    return [x2, y2, x1, y1] if (abs(x1 - x2) < 1e-4 and y1 < y2) or (abs(y1 - y2) < 1e-4 and x1 < x2) else q
def net(x, y):  # 페이지 이미지 좌표(110dpi px) 근처 선 -> 같은 net의 선 전부
    s = 110 / 72; x, y = x / s, y / s
    hit = [i for i, (a, b) in enumerate(segs) if min(a.x, b.x) - 3 <= x <= max(a.x, b.x) + 3 and min(a.y, b.y) - 3 <= y <= max(a.y, b.y) + 3]
    r = {f(i) for i in hit}
    return [orient([round(segs[i][0].x / W, 4), round(segs[i][0].y / H, 4), round(segs[i][1].x / W, 4), round(segs[i][1].y / H, 4)])
            for i in range(n) if f(i) in r]
# 시작점: 도면 하단 60V DC 인입 케이블 4가닥 (px @110dpi)
starts = [("60V DC 인입 1 (−) → 단자 1~3 블록", 216, 1030), ("60V DC 인입 1 (+) → 단자 5~7 블록", 296, 1030),
          ("60V DC 인입 2 (−) → 단자 1~3 블록", 519, 1030), ("60V DC 인입 2 (+) → 단자 5~7 블록", 601, 1030)]
steps = []
for lab, x, y in starts:
    sg = net(x, y); steps.append({"doc": "SICAS_HW_Design_" + STN, "page": PAGE, "segments": sg, "label": lab,
        "continues": "SV2602(T52) 연결 도면은 미확인"})
    print(lab, len(sg), 'segs', file=sys.stderr)
out = [{"id": "PWR_SICAS_N_60V" + ("" if STN == "SIN1" else "_" + STN), "title": "SICAS 캐비닛 S51 N레벨 60V DC 인입 → 채널 A/B/C 단자", "station": STN,
        "verified": False, "steps": steps}]
if STN != "SIN1":  # 다른 역은 기존 json 을 덮어쓰지 않고 id 기준 추가/교체
    old = json.load(open("power-paths.json", encoding="utf-8")); out = [x for x in old if x["id"] != out[0]["id"]] + out
json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "power-paths.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(',', ':'))
