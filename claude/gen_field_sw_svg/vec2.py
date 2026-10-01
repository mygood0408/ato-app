# MuPDF SVG(page.get_svg_image) -> 영역 잘라 그룹별 합친 path 로 압축.
import re, pymupdf

TOK = re.compile(r'([MLHVCZmlhvcz])|(-?\d*\.?\d+(?:e-?\d+)?)')


def parse(d):
    """절대 좌표 점열 목록(서브패스별) + 곡선 여부. 반환: [(cmd, [pts])]  cmd in M,L,C,Z"""
    out = []
    cmd = None
    nums = []
    cur = (0.0, 0.0)
    start = (0.0, 0.0)

    def flush():
        nonlocal cur, start
        if cmd is None:
            return
        if cmd == 'Z':
            out.append(('Z', []))
            cur = start
            return
        n = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'C': 6}[cmd]
        for i in range(0, len(nums) - n + 1, n):
            v = nums[i:i + n]
            if cmd in 'ML':
                cur = (v[0], v[1])
                if cmd == 'M' and i == 0:
                    out.append(('M', [cur]))
                    start = cur
                else:
                    out.append(('L', [cur]))
            elif cmd == 'H':
                cur = (v[0], cur[1]); out.append(('L', [cur]))
            elif cmd == 'V':
                cur = (cur[0], v[0]); out.append(('L', [cur]))
            elif cmd == 'C':
                out.append(('C', [(v[0], v[1]), (v[2], v[3]), (v[4], v[5])]))
                cur = (v[4], v[5])
    for m in TOK.finditer(d):
        if m.group(1):
            flush()
            cmd = m.group(1).upper(); nums = []
            if cmd == 'Z':
                flush(); cmd = None
        else:
            nums.append(float(m.group(2)))
    flush()
    return out


def tf(segs, M):
    a, b, c_, d, e, f = M
    return [(c, [(a * x + c_ * y + e, b * x + d * y + f) for x, y in pts]) for c, pts in segs]


def bbox(segs, H=None):
    xs = []; ys = []
    for c, pts in segs:
        for x, y in pts:
            xs.append(x); ys.append(y)
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def fmt(v):
    s = '%.1f' % v
    return s[:-2] if s.endswith('.0') else s


def emit(segs, H, ox, oy):
    """상대좌표(소수 1자리, 반올림 오차 누적 방지) + 같은 명령 연속 묶음."""
    o = []
    cur = (0.0, 0.0); start = cur; last = None
    q = lambda v: round(v * 10)  # 0.1 단위 정수
    for c, pts in segs:
        if c == 'Z':
            o.append('z'); cur = start; last = 'z'; continue
        P = [(q(x - ox), q(y - oy)) for x, y in pts]
        if c == 'M':
            o.append('M%s %s' % (fmt(P[0][0] / 10), fmt(P[0][1] / 10)))
            cur = P[0]; start = cur; last = 'M'
        elif c == 'L':
            dx, dy = P[0][0] - cur[0], P[0][1] - cur[1]
            if dx == 0 and dy == 0:
                continue
            txt = '%s %s' % (fmt(dx / 10), fmt(dy / 10))
            o.append((' ' + txt) if last == 'l' else ('l' + txt)); last = 'l'; cur = P[0]
        elif c == 'C':
            a = ' '.join('%s %s' % (fmt((p[0] - cur[0]) / 10), fmt((p[1] - cur[1]) / 10)) for p in P)
            o.append((' ' + a) if last == 'c' else ('c' + a)); last = 'c'; cur = P[2]
    return ''.join(o)


def extract(page, clip, regions, skip=(), minsize=0.0):
    """clip pt (x0,y0,x1,y1). regions [(id,(x0,y0,x1,y1))]. 반환 {gid: {attrkey: [d,...]}}, W, H"""
    s = page.get_svg_image(text_as_path=True)
    H = page.rect.height
    x0, y0, x1, y1 = clip
    groups = {rid: {} for rid, _ in regions}
    groups['rest'] = {}
    for m in re.finditer(r'<path transform="matrix\(([^)]*)\)"([^>]*?)/>', s):
        M = [float(v) for v in m.group(1).split(',')]
        a = m.group(2)
        if 'clip-rule' in a:
            continue
        dm = re.search(r' d="([^"]+)"', a)
        if not dm:
            continue
        segs = tf(parse(dm.group(1)), M)
        bb = bbox(segs, H)
        if not bb:
            continue
        cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
        if not (x0 <= cx <= x1 and y0 <= cy <= y1):
            continue
        if any(p <= cx <= q and r <= cy <= t for p, r, q, t in skip):
            continue
        if max(bb[2] - bb[0], bb[3] - bb[1]) < minsize:
            continue
        attrs = re.sub(r' d="[^"]+"', '', a)
        attrs = re.sub(r'stroke-linecap="round" stroke-linejoin="round"', '', attrs).strip()
        attrs = ' '.join(attrs.split())
        if 'fill=' not in attrs:
            attrs += ' fill="#000"'
        tgt = 'rest'
        for rid, (p, r, q, t) in regions:
            if p <= cx <= q and r <= cy <= t:
                tgt = rid
                break
        groups[tgt].setdefault(attrs, []).append(emit(segs, H, x0, y0))
    return groups, x1 - x0, y1 - y0


def render(groups, order=None, wrapid=True):
    out = []
    for gid, d in groups.items():
        if not d:
            continue
        inner = ''.join('<path %s d="%s"/>' % (a, ''.join(ds)) for a, ds in d.items())
        out.append('<g id="%s">%s</g>' % (gid, inner))
    return ''.join(out)
