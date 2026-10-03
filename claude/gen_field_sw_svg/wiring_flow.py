# 실제 배선도(설치상세도 p.5) 위의 표시전원·모터전원 흐름 경로 생성 (wire_graph 의 선 추적 + 접점 상태)
# 접점 구성(닫힌 접점)은 wiring_states.STATES, 단자·핀 대응은 연결 시뮬레이션(sim.py)으로 검증한 것.
import math
import wire_graph as wg
from wiring_states import RELAY, PIN

NAMED = wg.NAMED
ADJ = wg.build()
XE = 922.0                     # 외부 화살표 끝
EXT = {'rel46': 88.4, 'rel35': 135.3, 'indp': 348.1, 'indm': 383.6, 'motC': 262.5, 'motD': 247.7}
ROW = wg.TERM                  # 단자 y
CP = {  # 접점 간선: 이름 -> (핀, 핀)
    'NC1': ('pG', 'pA'), 'NC2': ('p1', 'p6'), 'N1': ('p9', 'p5'), 'N2': ('p10', 'p4'),
    'R1': ('p3', 'p8'), 'R2': ('p6r', 'p7'), 'RC1': ('p5r', 'p2'), 'RC2': ('pB', 'pGr'),
}


def clean(pts):
    out = []
    for p in pts:
        if out and math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) < 0.9:
            continue
        out.append(p)
    # 일직선 위 중간점 제거
    res = [out[0]]
    for i in range(1, len(out) - 1):
        a, b, c = res[-1], out[i], out[i + 1]
        cr = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        if abs(cr) > 0.6:
            res.append(b)
    res.append(out[-1])
    return res


def wire(a, b):
    """핀 a -> 핀 b 를 선을 따라 간 좌표열 (양 끝은 핀 좌표)."""
    p = wg.path(ADJ, a, b)
    assert p, (a, b)
    return [NAMED[a]] + p + [NAMED[b]]


def seg(a, b):
    return [NAMED[a], NAMED[b]]


def ext_in(ye, yl):   # 외부 -> 단자대 왼쪽 열
    return [(XE, ye), (871.9, ye), (855.0, ye), (855.0, yl), (838.5, yl)]


def ext_out(yl, ye):  # 단자대 왼쪽 열 -> 외부
    return ext_in(ye, yl)[::-1]


def hop(y1, y2):      # 단자대 점퍼
    return [(838.5, y1), (855.0, y1), (855.0, y2), (838.5, y2)]


def relay(k, side):   # 제어계전기 접점: 피벗 -> N/R 핀
    cp, n, r = RELAY[k]
    return [cp, n if side == 'N' else r]


def join(*parts):
    pts = []
    for p in parts:
        pts += p
    return clean(pts)


Y = lambda t: ROW[t][1]


def ext_m(ye):        # 모터전원 외부 화살표 -> 단자대 오른쪽 원 (왼쪽 원과 같은 단자)
    return [(910.6, ye), (859.6, ye), (771.9, ye)]


def motor(side):
    """모터전원: 외부 C -> C·G 단자 -> (G') -> 회로제어기 접점 -> 제어계전기 접점 -> 전동기 권선 -> D -> 수동안전기 -> D 단자 -> 외부 D"""
    head = [(910.6, EXT['motC']), (859.6, EXT['motC']), (771.9, EXT['motC'])] + wire('SC', 'MG') + [(779.6, 282.4), (881.5, 282.4)] + wire('MGr', 'pGr')
    if side == 'N':   # 반위->정위: (RC) B-G -> N2 -> C2 -> F -> 전동기(우측 권선쌍)
        mid = seg('pGr', 'pB') + wire('pB', 'C2n') + [RELAY['C2'][1], RELAY['C2'][0]] + wire('C2', 'TRp') + seg('TRp', 'TRm') + wire('TRm', 'M6') + seg('M6', 'M5') + wire('M5', 'BRp') + seg('BRp', 'Bc')
    else:             # 정위->반위: (NC) A-G -> R1 -> C1 -> E -> 전동기(좌측 권선쌍)
        mid = seg('pGr', 'pG') + seg('pG', 'pA') + wire('pA', 'C1r') + [RELAY['C1'][2], RELAY['C1'][0]] + wire('C1', 'TLp') + seg('TLp', 'TLm') + wire('TLm', 'M2') + seg('M2', 'M3') + wire('M3', 'BLp') + seg('BLp', 'Bc')
    tail = wire('Bc', 'D2') + wire('D2', 'SD') + [(859.6, EXT['motD']), (910.6, EXT['motD'])]
    return join(head, mid, tail)


# 출구 화살표 <-> 입구 화살표를 잇는 선(기계실 표시 감지부로 갔다 오는 선; 번호 없이 선만)
IND_LINK = [(XE, EXT['rel35']), (XE + 14, EXT['rel35']), (XE + 14, EXT['rel46']), (XE, EXT['rel46'])]


def split_at(pts, pt):
    """폴리라인을 pt 에 가장 가까운 지점에서 둘로 나눔 -> (앞, 뒤)"""
    best = None
    for k in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[k], pts[k + 1]
        dx, dy = x2 - x1, y2 - y1
        L2 = dx * dx + dy * dy
        t = max(0, min(1, ((pt[0] - x1) * dx + (pt[1] - y1) * dy) / L2)) if L2 else 0
        q = (x1 + t * dx, y1 + t * dy)
        d = math.hypot(pt[0] - q[0], pt[1] - q[1])
        if best is None or d < best[0]:
            best = (d, k, q)
    _, k, q = best
    return pts[:k + 1] + [q], [q] + pts[k + 1:]


def legs(pts, pt, rev=False):
    """(+)구간·(−)구간으로 분리. rev=True 면 극성 반대(앞이 (−))."""
    a, b = split_at(pts, pt)
    return [('m' if rev else 'p', a), ('p' if rev else 'm', b)]


def ctrl_flows():
    """제어전원: {상태: [(종류, 구간, 폴리라인, 모양)]}  N=정방향 (+)->코일(+), R=역방향(반대)"""
    import wiring_anim
    from wiring_states import STATES
    r = wiring_anim.build()['ctrl']      # [(+)단자->코일+, 코일(−)스텁, 코일(−)->(−)단자, 코일]
    coil_mid = (326, 125)
    N = [('p', r[0]), ('m', r[1]), ('m', r[2])] + legs(r[3], coil_mid)
    R = [('m' if l == 'p' else 'p', p[::-1]) for l, p in N]
    return {sid: [('ctrl', l, p, '') for l, p in (N if STATES[sid][0] == 'N' else R)] for sid in STATES}


MID = (XE + 14, (EXT['rel35'] + EXT['rel46']) / 2)


def single_flows():
    """단동: {상태: [(종류, 구간, 폴리라인, 모양)]}  (지역 좌표). 구간 p/m = (+)/(−), 모양 dim=연하게, x=차단 표시"""
    F = {}
    # 표시전원(계통도 기준): (+) 는 N4·R3 로 들어가 제어계전기 접점 -> 회로제어기 접점 -> 출구 단자 -> 기계실 감지부(연결선) -> 입구 단자 -> 회로제어기 접점 -> 단자 10·8 -> (-)
    ind_n = join(ext_in(EXT['indm'], Y('N4')), wire('N4', 'C4n'), [RELAY['C4'][1], RELAY['C4'][0]], wire('C4', 'p9'), seg('p9', 'p5'), wire('p5', 'T5'),
                 ext_out(Y('T5'), EXT['rel35']), IND_LINK, ext_in(EXT['rel46'], Y('T4')), wire('T4', 'p4'), seg('p4', 'p10'), wire('p10', 'T10'),
                 ext_out(Y('T10'), EXT['indp']))
    ind_r = join(ext_in(EXT['indm'], Y('R3')), wire('R3', 'C3r'), [RELAY['C3'][2], RELAY['C3'][0]], wire('C3', 'p7'), seg('p7', 'p6r'), wire('p6r', 'T6'),
                 ext_out(Y('T6'), EXT['rel46']), IND_LINK[::-1], ext_in(EXT['rel35'], Y('T3')), wire('T3', 'p3'), seg('p3', 'p8'), wire('p8', 'T8'),
                 ext_out(Y('T8'), EXT['indp']))
    # 전환순간·전환중: (+) 가 회로제어기 접점(N1 / R2)에서 막힘
    blk_n = join(ext_in(EXT['indm'], Y('N4')), wire('N4', 'C4n'), [RELAY['C4'][1], RELAY['C4'][0]], wire('C4', 'p9'))
    blk_r = join(ext_in(EXT['indm'], Y('R3')), wire('R3', 'C3r'), [RELAY['C3'][2], RELAY['C3'][0]], wire('C3', 'p7'))
    L = lambda cls, pts, pt, mod='': [(cls, l, p, mod) for l, p in legs(pts, pt)]
    mn, mr = motor('N'), motor('R')
    C = ctrl_flows()
    F['ind_n'] = C['ind_n'] + L('ind', ind_n, MID)
    F['ind_r'] = C['ind_r'] + L('ind', ind_r, MID)
    for sid, blk, mot in (('mot_n1', blk_n, mn), ('mot_n2', blk_n, mn), ('mot_r1', blk_r, mr), ('mot_r2', blk_r, mr)):
        F[sid] = (C[sid] + [('ind', 'p', blk, ''), ('ind', 'x', [blk[-1]], 'x')]
                  + L('mot', mot, NAMED['Bc'], 'dim' if sid.endswith('1') else ''))
    return F


def double_flows(W, dy, LINK_Y):
    """쌍동: 전역 좌표(A 는 +(10,10), B 는 +(10,10+dy)) 폴리라인."""
    X = 838.5 + 10
    A = lambda pts: [(x + 10, y + 10) for x, y in pts]
    B = lambda pts: [(x + 10, y + 10 + dy) for x, y in pts]
    link = lambda i, a, b, rev=False: ([(X, 10 + LINK_Y['out'][a]), (10 + W - 15 + i * 12, 10 + LINK_Y['out'][a]), (10 + W - 15 + i * 12, 10 + dy + LINK_Y['in'][b]), (X, 10 + dy + LINK_Y['in'][b])][::-1 if rev else 1])
    F = {}
    # 표시 흐름은 S14 에서 계통도 기준으로 재작업 — 구간(+/−) 구분 없이 'p' 로 둔다
    F['ind_n'] = [
        ('ind', 'p', join(A(join(ext_in(EXT['indp'], Y('T10')), wire('T10', 'p10'), seg('p10', 'p4'), wire('p4', 'T4'), hop(Y('T4'), Y('T2')))),
                          link(0, 'T2', 'T10'),
                          B(join([(838.5, Y('T10'))], wire('T10', 'p10'), seg('p10', 'p4'), wire('p4', 'T4'), ext_out(Y('T4'), EXT['rel46'])))), ''),
        ('ind', 'p', join(B(join(ext_in(EXT['rel35'], Y('T5')), wire('T5', 'p5'), seg('p5', 'p9'), wire('p9', 'C4'), relay('C4', 'N'), wire('C4n', 'N4'), [(838.5, Y('N4'))])),
                          link(1, 'T5', 'N4', True),
                          A(join([(838.5, Y('T5'))], wire('T5', 'p5'), seg('p5', 'p9'), wire('p9', 'C4'), relay('C4', 'N'), wire('C4n', 'N4'), ext_out(Y('N4'), EXT['indm'])))), ''),
    ]
    F['ind_r'] = [
        ('ind', 'p', join(A(join(ext_in(EXT['indp'], Y('T8')), wire('T8', 'p8'), seg('p8', 'p3'), wire('p3', 'T3'), hop(Y('T3'), Y('T1')))),
                          link(0, 'T1', 'T8'),
                          B(join([(838.5, Y('T8'))], wire('T8', 'p8'), seg('p8', 'p3'), wire('p3', 'T3'), ext_out(Y('T3'), EXT['rel35'])))), ''),
        ('ind', 'p', join(B(join(ext_in(EXT['rel46'], Y('T6')), wire('T6', 'p6r'), seg('p6r', 'p7'), wire('p7', 'C3'), relay('C3', 'R'), wire('C3r', 'R3'), [(838.5, Y('R3'))])),
                          link(1, 'T6', 'R3', True),
                          A(join([(838.5, Y('T6'))], wire('T6', 'p6r'), seg('p6r', 'p7'), wire('p7', 'C3'), relay('C3', 'R'), wire('C3r', 'R3'), ext_out(Y('R3'), EXT['indm'])))), ''),
    ]
    mn, mr = motor('N'), motor('R')
    C = ctrl_flows()
    for sid in C:
        for f in (A, B):
            F.setdefault(sid, []).extend((k, l, f(p), m) for k, l, p, m in C[sid])
    for sid, mot in (('mot_n1', mn), ('mot_n2', mn), ('mot_r1', mr), ('mot_r2', mr)):
        for f in (A, B):
            F[sid] += [('mot', l, f(p), 'dim' if sid.endswith('1') else '') for l, p in legs(mot, NAMED['Bc'])]
    return F


def mot_labels():
    """모터전원 단자 라벨(전원 하나 보기에서만 보임): C=BX110, D=CX110"""
    t = lambda y, s: f'<text x="{XE - 2:.0f}" y="{y - 4:.0f}" class="fsw-mlab">{s}</text>'
    return t(EXT['motC'], 'C (BX110)') + t(EXT['motD'], 'D (CX110)')


def overlay(flows):
    """{상태: [(종류, 구간, pts, 모양)]} -> SVG 조각(상태별 그룹, 지역/전역 좌표 그대로)"""
    out = []
    for sid, lst in flows.items():
        o = ''
        for cls, leg, pts, mod in lst:
            if mod == 'x':
                x, y = pts[0]
                o += f'<path d="M{x-3.5:.1f} {y-3.5:.1f}l7 7m0 -7l-7 7" class="fsw-x"/>'
                continue
            d = 'M' + ' L'.join('%.1f %.1f' % p for p in pts)
            o += (f'<g class="fsw-k-{cls} fsw-leg-{leg} fsw-mod-{mod or "n"}"><path d="{d}" class="fsw-flowbase fsw-fb-{cls}"/>'
                  f'<path d="{d}" class="fsw-flow fsw-fl-{cls}"/></g>')
        out.append(f'<g class="fsw-ws ws-{sid}">{o}</g>')
    return ''.join(out)


if __name__ == '__main__':
    for k, v in single_flows().items():
        print(k, [(c, l, m, len(p)) for c, l, p, m in v])
