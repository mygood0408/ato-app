# 설치상세도 p.5 결선도 위에 얹을 전원 흐름 애니메이션 경로 생성.
# 선 연결(넷)은 PDF 벡터에서 직접 추적하고, 두꺼운(이중선) 모터 선은 도면 좌표 중심선으로 지정한다.
# 흐름 방향 = 전원 공급측 -> 부하/출력측 (접점 정위/반위 상태에 따른 실제 경로는 달라질 수 있음).
import re, math, collections
import pymupdf
from vec2 import parse, tf, bbox

PDF_INST = r'C:\Users\김영추\Desktop\2호선 PDF 자료\선로전환기 설치상세도(정반위표시등 포함).pdf'
CLIP = (115, 140, 1100, 725)


def segments():
    d = pymupdf.open(PDF_INST)
    s = d[4].get_svg_image(text_as_path=True)
    out = []
    for m in re.finditer(r'<path transform="matrix\(([^)]*)\)"([^>]*?)/>', s):
        M = [float(v) for v in m.group(1).split(',')]
        a = m.group(2)
        if 'clip-rule' in a or 'stroke=' not in a or 'fill="none"' not in a:
            continue
        w = float(re.search(r'stroke-width="([\d.]+)"', a).group(1))
        if w < 0.9:
            continue
        dm = re.search(r' d="([^"]+)"', a)
        if not dm:
            continue
        segs = tf(parse(dm.group(1)), M)
        bb = bbox(segs)
        if not bb:
            continue
        cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
        if not (CLIP[0] <= cx <= CLIP[2] and CLIP[1] <= cy <= CLIP[3]):
            continue
        pts = []
        subs = []
        for c, P in segs:
            if c == 'M':
                if pts: subs.append(pts)
                pts = [P[0]]
            elif c == 'L': pts.append(P[0])
            elif c == 'C': pts.append(P[2])
            elif c == 'Z' and pts: pts.append(pts[0])
        if pts: subs.append(pts)
        for sp in subs:
            if len(sp) > 6:
                continue
            for p, q in zip(sp, sp[1:]):
                if math.hypot(p[0]-q[0], p[1]-q[1]) > 1e-6:
                    out.append((p[0]-CLIP[0], p[1]-CLIP[1], q[0]-CLIP[0], q[1]-CLIP[1]))
    return out


def nets(segs):
    par = list(range(len(segs)))

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    TOL = 0.45
    bb = [(min(s[0], s[2])-TOL, min(s[1], s[3])-TOL, max(s[0], s[2])+TOL, max(s[1], s[3])+TOL) for s in segs]

    def on_seg(px, py, s):
        x1, y1, x2, y2 = s
        dx, dy = x2-x1, y2-y1
        L2 = dx*dx+dy*dy
        t = max(0, min(1, ((px-x1)*dx+(py-y1)*dy)/L2))
        return (px-(x1+t*dx))**2+(py-(y1+t*dy))**2 <= TOL*TOL
    for k, s in enumerate(segs):
        for (x, y) in ((s[0], s[1]), (s[2], s[3])):
            for j in range(len(segs)):
                if j != k:
                    b = bb[j]
                    if b[0] <= x <= b[2] and b[1] <= y <= b[3] and on_seg(x, y, segs[j]):
                        par[f(k)] = f(j)
    comps = collections.defaultdict(list)
    for k in range(len(segs)):
        comps[f(k)].append(k)
    return list(comps.values())


def oriented(segs, comp, entry, minlen=6.5):
    """넷 안에서 entry 점(가장 가까운 끝점)부터 BFS 로 선분 방향을 정해 연속 경로(폴리라인) 목록을 반환."""
    key = lambda p: (round(p[0] * 2) / 2, round(p[1] * 2) / 2)
    # T 접속: 다른 선분 중간에 닿는 끝점에서 그 선분을 분할
    S = [segs[k] for k in comp if math.hypot(segs[k][2]-segs[k][0], segs[k][3]-segs[k][1]) >= minlen]
    pts = {key((s[0], s[1])) for s in S} | {key((s[2], s[3])) for s in S}
    split = []
    for s in S:
        x1, y1, x2, y2 = s
        dx, dy = x2-x1, y2-y1
        L2 = dx*dx+dy*dy
        cut = [(0.0, (x1, y1)), (1.0, (x2, y2))]
        for p in pts:
            t = ((p[0]-x1)*dx+(p[1]-y1)*dy)/L2
            if 0.02 < t < 0.98:
                cx, cy = x1+t*dx, y1+t*dy
                if (p[0]-cx)**2+(p[1]-cy)**2 <= 0.6**2:
                    cut.append((t, p))
        cut.sort()
        for (t0, a), (t1, b) in zip(cut, cut[1:]):
            split.append((a[0], a[1], b[0], b[1]))
    comp = range(len(split)); segs = split; minlen = 0
    adj = collections.defaultdict(list)
    for k in comp:
        s = segs[k]
        if math.hypot(s[2]-s[0], s[3]-s[1]) < minlen:
            continue
        a, b = key((s[0], s[1])), key((s[2], s[3]))
        adj[a].append((b, s)); adj[b].append((a, s))
    # 정확한 끝점 일치가 안 되는 T 접속은 가장 가까운 노드로 연결
    nodes = list(adj)
    start = min(nodes, key=lambda p: math.hypot(p[0]-entry[0], p[1]-entry[1]))
    seen = {start}
    q = [start]
    dirs = []
    while q:
        u = q.pop(0)
        for v, s in adj[u]:
            if v not in seen:
                seen.add(v); q.append(v); dirs.append((u, v))
    # T 접속(끝점이 다른 선분 중간에 닿음)은 선분 분할로 처리: 방문 안 된 노드에 대해 연결 선분 위 접속점 찾기
    for _ in range(3):
        for n in nodes:
            if n in seen:
                continue
            for u in list(seen):
                for v, s in adj[u]:
                    pass
        break
    out_edges = collections.defaultdict(list)
    indeg = collections.Counter()
    for u, v in dirs:
        out_edges[u].append(v); indeg[v] += 1
    paths = []
    brk = lambda n: indeg[n] != 1 or len(out_edges[n]) != 1
    for n in list(out_edges):
        if brk(n) or n == start:
            for v in out_edges[n]:
                path = [n, v]
                while not brk(path[-1]) and out_edges[path[-1]]:
                    path.append(out_edges[path[-1]][0])
                paths.append(path)
    return paths


def build():
    segs = segments()
    comps = nets(segs)
    ep = lambda c: [(segs[k][0], segs[k][1]) for k in c] + [(segs[k][2], segs[k][3]) for k in c]

    def net_at(pt, tol=3.5):
        best = None
        for c in comps:
            if len(c) < 2:
                continue
            for p in ep(c):
                d = math.hypot(p[0]-pt[0], p[1]-pt[1])
                if d <= tol and (best is None or d < best[0]):
                    best = (d, c)
        return best[1] if best else None
    spec = {
        'ctrl': [(838.5, 411), (326, 150), (838.5, 403)],
        'ind': [(838.5, 324), (838.5, 332), (838.5, 340), (838.5, 348), (838.5, 367), (838.5, 376),
                (266.4, 113.1), (231, 405), (311, 319), (303, 379), (325, 380), (267, 174), (298, 163)],
    }
    # (+) 단자 -> 코일 + : 입력, 코일 - -> (-) 단자 : 복귀. (-)(+) 단자 쪽 진입점은 위 목록 첫 항목(+)만 쓰고 (-)는 코일측에서 시작
    spec['ctrl'] = [(838.5, 411), (326, 150)]
    res = collections.defaultdict(list)
    used = set()
    for cls, pts in spec.items():
        for pt in pts:
            c = net_at(pt)
            if c is None:
                print('no net at', cls, pt)
                continue
            if id(c) in used:
                print('dup net', cls, pt)
                continue
            used.add(id(c))
            for p in oriented(segs, c, pt):
                res[cls].append(p)
    manual = {
        'ctrl': [[(326, 106), (326, 144)]],  # 코일(+ -> -)
        'ind': [[(298, 205), (298, 163)]],   # 끊긴 구간(N4 배선) 연결
        'mot': [
            [(773, 249.5), (548.5, 249.5), (548.5, 449.5), (154, 449.5)],             # C 단자 -> 수동안전기 SW
            [(118, 449), (111, 449), (83.5, 449), (83.5, 284)],                       # SW -> 전동기 D
            [(882, 283), (913.5, 283), (913.5, 304.5), (536.5, 304.5), (536.5, 437.5), (326, 437.5), (326, 404)],  # D 단자 -> 회로제어기 G'
            [(302.8, 404), (302.8, 424.5), (367.9, 424.5), (367.9, 280.6), (250.6, 280.6), (250.6, 153.2), (229.3, 153.2)],  # 회로제어기 B -> 제어계전기 N2
            [(233, 328.5), (241.9, 328.5), (241.9, 127.4), (231.1, 127.4)],           # 회로제어기 A -> 제어계전기 R1
            [(208, 124.4), (158.5, 124.4), (158.5, 360.5), (67, 360.5), (67, 284)],   # R1 -> 전동기 E
            [(208, 184.3), (166.5, 184.3), (166.5, 369.5), (50.5, 369.5), (50.5, 284)],  # R2 -> 전동기 F
        ],
    }
    for cls, ps in manual.items():
        res[cls].extend(ps)
    return res


def overlay(res):
    cname = {'ctrl': 'ctrl', 'ind': 'ind', 'mot': 'mot'}
    out = []
    for cls, paths in res.items():
        d = ''.join('M' + ' L'.join('%.1f %.1f' % p for p in path) for path in paths)
        out.append(f'<g id="flow-{cls}" class="fsw-flowg fsw-flowg-{cls}"><path d="{d}" class="fsw-flowbase fsw-fb-{cls}"/><path d="{d}" class="fsw-flow fsw-fl-{cls}"/></g>')
    return ''.join(out)


if __name__ == '__main__':
    r = build()
    for k, v in r.items():
        print(k, len(v), [(tuple(round(c) for c in p[0]), tuple(round(c) for c in p[-1])) for p in v][:30])
