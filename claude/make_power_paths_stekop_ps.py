"""C3: SIN1 p.106 T52 STEKOP 전원 조건(24V PS-ORD → 전원모듈 → 계전기 PSM-K91 'STEKOP-PS o.k.' → STEKOP-PLATTER X3 8V 확인 신호)을
power-paths.json 에 추가/교체(id 기준). 시드 px = 75dpi. --preview: 색입힌 png."""
import pymupdf, json, sys, os
from stn import STN, PDF, pid, page, CFG   # --station <접미사>(기본 SIN1); --dry 는 선 일치 개수만 출력
PAGE = page("STEKOP"); X = STN != "SIN1"
pg = pymupdf.open(PDF)[PAGE - 1]; W, H = pg.rect.width, pg.rect.height; s = 75 / 72
segs = [(it[1], it[2]) for dr in pg.get_drawings() for it in dr['items'] if it[0] == 'l']
n = len(segs); par = list(range(n))
def f(i):
    while par[i] != i: par[i] = par[par[i]]; i = par[i]
    return i
def on(p, a, b, t=0.6):
    return (min(a.x, b.x) - t <= p.x <= max(a.x, b.x) + t and min(a.y, b.y) - t <= p.y <= max(a.y, b.y) + t
            and abs((b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x)) <= t * max(1, ((b.x-a.x)**2+(b.y-a.y)**2) ** .5))
for i in range(n):
    for j in range(i + 1, n):
        (a, b), (c, d) = segs[i], segs[j]
        if any(on(p, x, y) for p, x, y in ((a, c, d), (b, c, d), (c, a, b), (d, a, b))): par[f(i)] = f(j)
def net(seeds, down, right):  # down: 세로 방향(True=아래), right: 가로 방향(True=오른쪽)
    r = set()
    for x, y in seeds:
        x, y = x / s, y / s
        r |= {f(i) for i, (a, b) in enumerate(segs) if min(a.x, b.x) - 3 <= x <= max(a.x, b.x) + 3 and min(a.y, b.y) - 3 <= y <= max(a.y, b.y) + 3}
    out = []
    for i in range(n):
        if f(i) not in r: continue
        a, b = segs[i]
        if abs(a - b) < 8: continue
        if abs(a.x - b.x) < .3: q = (a, b) if (a.y < b.y) == down else (b, a)
        elif abs(a.y - b.y) < .3: q = (a, b) if (a.x < b.x) == right else (b, a)
        else: continue
        out.append([round(q[0].x / W, 4), round(q[0].y / H, 4), round(q[1].x / W, 4), round(q[1].y / H, 4)])
    return out
def pt(t, x, y): return [t, round(x / s / W, 4), round(y / s / H, 4)]
def poly(*pts):  # px(75dpi) 꺾은선 → 정규화 선분(진행 방향 = 그린 순서). 박스 외곽선이 net에 붙어 net 대신 직접 지정
    return [[round(x1 / s / W, 4), round(y1 / s / H, 4), round(x2 / s / W, 4), round(y2 / s / H, 4)] for (x1, y1), (x2, y2) in zip(pts, pts[1:])]
sup = poly((582, 386), (838, 386), (838, 630)) + poly((255, 630), (255, 522))   # 24V 인입(p.230에서) → 전원모듈 25 / 모듈 27 → 코일 A1
ret = poly((740, 630), (740, 416), (582, 416)) + poly((349, 522), (349, 630))   # 0V 복귀(29 → p.230) / 코일 A2 → 모듈 30(ORD)
def hit(x, y):  # poly 꼭짓점이 도면 선 위에 있는지(3pt)
    p = pymupdf.Point(x / s, y / s); return any(on(p, a, b, 3) for a, b in segs)
BAD0 = [0, 1]  # ponytail: SIN1 기준 off-line 꼭짓점 인덱스(도면 선 밖 끝점), 이와 다르면 구조 다름
bad = [k for k, q in enumerate(sup + ret) if not (hit(q[0] * W * s, q[1] * H * s) and hit(q[2] * W * s, q[3] * H * s))]
print(STN, PAGE, len(sup), len(ret), 'off-line', bad, file=sys.stderr)
if bad != BAD0 and X: print('확인필요: 선 위치 불일치 — 경로 생성 안 함', file=sys.stderr); sys.exit(0)
new = [{"id": pid("PWR_SICAS_T52_STEKOP_PS"), "title": ("" if X else "T52 ") + "STEKOP 전원 조건 (24V PS-ORD → 전원모듈 → 계전기 PSM-K91 'STEKOP-PS o.k.' → STEKOP-PLATTER X3)", "station": STN, "verified": False,
        "steps": [{"doc": "SICAS_HW_Design_" + STN, "page": PAGE, "segments": sup, "segments0": ret,
                   "parts": [pt("+24V DC (인입)" if X else "+24V DC (=SIN1/08.02.21/9.C4 = p.230)", 590, 375), pt("RL 0V DC" if X else "RL 0V DC (p.230)", 590, 405), pt("전원모듈 S25790-C18-A1 (PS-ORD)", 560, 690),
                             pt("계전기 PSM-K91 STEKOP-PS o.k.", 130, 470), pt("STEKOP-PLATTER X3 (1/7)", 255, 172)],
                   "label": ("24V(붉은선, 다른 쪽에서 인입)" if X else "T52 24V(붉은선, p.230에서 인입)") + " → 전원모듈 PS-ORD → 계전기 PSM-K91 코일 (0V 복귀 파랑)",
                   "continues": "PSM-K91 접점(24/21)→STEKOP-PLATTER X3(1/7)은 8V 유무 신호 회로. 8V 자체는 SV2602가 60V를 변환해 만든다(유지보수 매뉴얼 p.81·103·137, 결선 p.78; S2 재조사). 24V 인입 원천은 " + ("SV2602 쪽 p.%s 참조" % CFG["paths"].get("SV2602", ["?"])[0] if X else "p.230(=SIN1/08.02.21 9/11) 참조")}]}]
if '--dry' not in sys.argv:
    fp = os.path.join(os.path.dirname(__file__), '..', 'power-paths.json')
    P = json.load(open(fp, encoding='utf-8')); P = [x for x in P if x['id'] != new[0]['id']] + new
    json.dump(P, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
if '--preview' in sys.argv:
    sh = pg.new_shape()
    for L, c in ((sup, (1, 0, 0)), (ret, (0, 0, 1))):
        for x1, y1, x2, y2 in L: sh.draw_line((x1 * W, y1 * H), (x2 * W, y2 * H)); sh.finish(color=c, width=2)
    sh.commit(); pg.get_pixmap(dpi=70).save(os.path.join(os.environ.get('TEMP', '.'), 'c3_p106.png'))
