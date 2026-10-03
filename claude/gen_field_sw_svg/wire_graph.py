# 설치상세도 p.5 선 그래프: 선분 끝점/T 접속으로 연결(교차선은 연결 아님), 이름 붙은 핀은 근처 선 투영점들의 묶음 노드 -> 최단 경로
import math, collections, heapq
import wiring_anim as wa
import wiring_states as ws
from wiring_states import PIN, RELAY

TERM = {  # 단자대 왼쪽 열(배선 쪽) 좌표 (클립 좌표, 선 y 실측)
    'T6': (838.5, 72.2), 'T4': (838.5, 80.2), 'T2': (838.5, 107.7), 'T1': (838.5, 115.7), 'T3': (838.5, 143.2), 'T5': (838.5, 151.2),
    'T10': (838.5, 323.9), 'T10b': (838.5, 332.0), 'T8b': (838.5, 340.0), 'T8': (838.5, 348.0),
    'N4': (838.5, 367.5), 'R3': (838.5, 375.5), 'CM': (838.5, 403.0), 'CP': (838.5, 411.0),
}
NAMED = dict(TERM)
for k, v in PIN.items():
    NAMED['p' + k] = v
for k, (cp, n, r) in RELAY.items():
    NAMED[k] = cp; NAMED[k + 'n'] = n; NAMED[k + 'r'] = r
NAMED.update({  # 전동기 단자·권선 점, 단자대 모터 단자 (클립 좌표)
    'F': (50.4, 279.1), 'E': (67.0, 279.1), 'Dm': (83.4, 279.1),
    'M1': (30.4, 227.8), 'M2': (42.6, 227.6), 'M3': (54.4, 227.6), 'M4': (66.5, 227.3), 'M5': (79.0, 227.6), 'M6': (90.8, 228.0), 'M7': (103.2, 228.7),
    'TLp': (45.8, 134.2), 'TLm': (56.4, 146.0), 'TRp': (87.2, 134.6), 'TRm': (76.5, 146.7), 'BLp': (55.1, 164.7), 'BRp': (78.7, 164.9), 'Bc': (66.9, 177.6),
    'F2': (50.4, 283.9), 'E2': (67.0, 284.1), 'D2': (83.4, 284.1), 'SC': (771.9, 262.5), 'SD': (771.9, 249.9), 'MG': (779.6, 282.4), 'MGr': (881.5, 282.4), 'XC': (859.6, 262.5), 'XD': (859.6, 247.7),
})
EXTRA_LINES = [(207.8, 110.0, 207.8, 124.2), (207.8, 170.0, 207.8, 183.6), (111.1, 449.25, 153.7, 449.25)]  # E·F 선 끝 -> C1/C2 피벗 (그림에서 이어 붙인 선)
PERM = [('F', 'F2'), ('E', 'E2'), ('Dm', 'D2'), ('pG', 'pGr')]  # 단자 원 중심 <-> 굵은 선 시작점(원 아래)
KEY = lambda p: (round(p[0] * 2) / 2, round(p[1] * 2) / 2)


def merged_lines():
    segs = wa.segments()
    boxes = [(x0 - 0.3, y0 - 0.3, x1 + 0.3, y1 + 0.3) for _, (x0, y0, x1, y1) in
             [(n, (a - ws.OX, b - ws.OY, c - ws.OX, d - ws.OY)) for n, (a, b, c, d) in ws.regions()]]
    inside = lambda s: any(b[0] <= min(s[0], s[2]) and max(s[0], s[2]) <= b[2] and b[1] <= min(s[1], s[3]) and max(s[1], s[3]) <= b[3] for b in boxes)
    segs = [s for s in segs if not (inside(s) and abs(s[0] - s[2]) > 0.15 and abs(s[1] - s[3]) > 0.15)]  # 접점 기호(혀·화살표)는 상태별로 따로 다룬다
    H = collections.defaultdict(list); V = collections.defaultdict(list); O = []
    for x1, y1, x2, y2 in segs:
        if abs(y1 - y2) < 0.15: H[round((y1 + y2) / 2, 1)].append([min(x1, x2), max(x1, x2)])
        elif abs(x1 - x2) < 0.15: V[round((x1 + x2) / 2, 1)].append([min(y1, y2), max(y1, y2)])
        elif math.hypot(x1 - x2, y1 - y2) >= 4: O.append((x1, y1, x2, y2))

    def merge(l, gap=1.5):
        l.sort(); o = []
        for a, b in l:
            if o and a <= o[-1][1] + gap: o[-1][1] = max(o[-1][1], b)
            else: o.append([a, b])
        return o
    L = []
    for y, l in H.items():
        for a, b in merge(l):
            if b - a >= 4 and -5 < y < 600 and a > -5 and b < 1000: L.append((a, y, b, y))
    for x, l in V.items():
        for a, b in merge(l):
            if b - a >= 4 and -5 < x < 1000 and a > -5 and b < 600: L.append((x, a, x, b))
    return L + O + EXTRA_LINES


def proj(p, s):
    x1, y1, x2, y2 = s
    dx, dy = x2 - x1, y2 - y1
    t = max(0, min(1, ((p[0] - x1) * dx + (p[1] - y1) * dy) / (dx * dx + dy * dy)))
    return t, (x1 + t * dx, y1 + t * dy)


def build(pins=None, tol=1.0, r=3.2):
    pins = NAMED if pins is None else pins
    segs = merged_lines()
    ends = {KEY((s[0], s[1])) for s in segs} | {KEY((s[2], s[3])) for s in segs}
    pinnodes = collections.defaultdict(set)
    cuts = [[(0.0, (s[0], s[1])), (1.0, (s[2], s[3]))] for s in segs]
    for i, s in enumerate(segs):  # T 접속
        for p in ends:
            t, c = proj(p, s)
            if 0 < t < 1 and (p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2 <= tol ** 2:
                cuts[i].append((t, p))
    for name, P in pins.items():  # 핀: 근처 선에 투영
        for i, s in enumerate(segs):
            t, c = proj(P, s)
            if (P[0] - c[0]) ** 2 + (P[1] - c[1]) ** 2 <= r * r:
                cuts[i].append((t, c)); pinnodes[name].add(KEY(c))
    adj = collections.defaultdict(list)
    for c in cuts:
        c.sort()
        for (t0, a), (t1, b) in zip(c, c[1:]):
            a, b = KEY(a), KEY(b)
            if a != b:
                d = math.hypot(a[0] - b[0], a[1] - b[1])
                adj[a].append((b, d)); adj[b].append((a, d))
    nodes = list(adj)
    for i, a in enumerate(nodes):  # 끝점끼리 tol 이내면 같은 노드
        for b in nodes[i + 1:]:
            if abs(a[0] - b[0]) <= tol and abs(a[1] - b[1]) <= tol:
                adj[a].append((b, 0.01)); adj[b].append((a, 0.01))
    for name, ns in pinnodes.items():  # 핀 가상 노드
        for n in ns:
            if n in adj:
                adj[('P', name)].append((n, 0)); adj[n].append((('P', name), 0))
    return adj


def path(adj, a, b, extra=()):
    """a,b: 핀 이름. extra: 추가 가상 간선 [(핀이름,핀이름)] (접점 닫힘). 반환 좌표 폴리라인 목록(가상 노드 제외)"""
    g = collections.defaultdict(list)
    for u, l in adj.items(): g[u] += l
    for p, q in list(extra) + PERM:
        g[('P', p)].append((('P', q), 0)); g[('P', q)].append((('P', p), 0))
    A, B = ('P', a), ('P', b)
    dist = {A: 0}; prev = {}; h = [(0, 0, A)]; n = 0
    while h:
        d, _, u = heapq.heappop(h)
        if u == B: break
        if d > dist.get(u, 1e18): continue
        for v, w in g[u]:
            if d + w < dist.get(v, 1e18):
                dist[v] = d + w; prev[v] = u; n += 1; heapq.heappush(h, (d + w, n, v))
    if B not in dist: return None
    out = [B]
    while out[-1] != A: out.append(prev[out[-1]])
    return [q for q in out[::-1] if q[0] != 'P']


def plen(p):
    return round(sum(math.hypot(p[i][0] - p[i + 1][0], p[i][1] - p[i + 1][1]) for i in range(len(p) - 1)))


if __name__ == '__main__':
    adj = build()
    pairs = [('T10', 'p10'), ('T10b', 'C4r'), ('T8b', 'C3n'), ('T8', 'p8'), ('T4', 'p4'), ('T6', 'p6'), ('T3', 'p3'), ('T5', 'p5r'),
             ('T1', 'p1'), ('T2', 'p2'), ('R3', 'C3r'), ('N4', 'C4n'), ('C3', 'p7'), ('C4', 'p9')]
    for a, b in pairs:
        p = path(adj, a, b)
        print(a, b, None if p is None else (len(p), plen(p)))
