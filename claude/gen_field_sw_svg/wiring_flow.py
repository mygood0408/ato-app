# 실제 배선도(설치상세도 p.5) 위의 표시전원·모터전원 흐름 경로 생성 (wire_graph 의 선 추적 + 접점 상태)
# 접점 구성(닫힌 접점)은 wiring_states.STATES, 단자·핀 대응은 연결 시뮬레이션(sim.py)으로 검증한 것.
import math
import wire_graph as wg
from wiring_states import RELAY, PIN

NAMED = wg.NAMED
ADJ = wg.build()
XE = 922.0                     # 외부 화살표 끝
EXT = {'rel46': 88.4, 'rel35': 135.3, 'indp': 348.1, 'indm': 383.6, 'motC': 262.5, 'motD': 247.7, 'sp1': 430.0, 'sp2': 447.0}
ROW = {**wg.TERM, 'S1a': (838.5, 430.0), 'S1b': (838.5, 438.4), 'S2a': (838.5, 447.0), 'S2b': (838.5, 455.0)}  # 단자 y (S1·S2 = 예비단자 2칸, 칸마다 입·출 두 구멍)
DIAG = 26                      # 기구함에서 들어오는 제어·모터 선의 비스듬한 길이
LANE = 9                       # 쌍동 연결선 가로 간격
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
    def link(i, ya, yb, rev=False):   # A 쪽 y(지역) <-> B 쪽 y(지역) 연결선, 기본 방향 A->B
        xr = 10 + W + 15 + i * LANE
        return [(X, 10 + ya), (xr, 10 + ya), (xr, 10 + dy + yb), (X, 10 + dy + yb)][::-1 if rev else 1]
    t = lambda n: (838.5, Y(n))
    # 한 호기 안의 표시 경로(단자 -> 단자). (+): 입력(N4/R3) -> 출력(5/6), (-): 입력(4/3) -> 출구(10/8)
    plus = {'N': join([t('N4')], wire('N4', 'C4n'), [RELAY['C4'][1], RELAY['C4'][0]], wire('C4', 'p9'), seg('p9', 'p5'), wire('p5', 'T5'), [t('T5')]),
            'R': join([t('R3')], wire('R3', 'C3r'), [RELAY['C3'][2], RELAY['C3'][0]], wire('C3', 'p7'), seg('p7', 'p6r'), wire('p6r', 'T6'), [t('T6')])}
    minus = {'N': join([t('T4')], wire('T4', 'p4'), seg('p4', 'p10'), wire('p10', 'T10'), [t('T10')]),
             'R': join([t('T3')], wire('T3', 'p3'), seg('p3', 'p8'), wire('p8', 'T8'), [t('T8')])}
    blkp = {'N': join([t('N4')], wire('N4', 'C4n'), [RELAY['C4'][1], RELAY['C4'][0]], wire('C4', 'p9')),
            'R': join([t('R3')], wire('R3', 'C3r'), [RELAY['C3'][2], RELAY['C3'][0]], wire('C3', 'p7'))}
    spare_in = B(join(ext_in(EXT['sp1'], Y('S1a')), [t('S1b')]))      # 기구함 38(+) -> 메인(B) 예비단자
    mx, my = XE + 10 + 14, 10 + dy
    F = {}
    # 표시전원(계통도 205): 기구함 38(+)/37(−) -> 메인(B) 예비단자 -> A 입력 -> A 접점 -> A 출력 -> B 입력 -> B 접점 -> B 출력 -> 기구함 40/39
    # (−): B 입구 -> B 접점 -> B 10/8 -> A 2·1(점퍼로 4·3) -> A 접점 -> A 10/8 -> 예비단자 -> 기구함 37
    for sid, k, (op, ip, a_in, o_t, i_t, hop_t, r_t) in (
            ('ind_n', 'N', ('rel35', 'rel46', 'N4', 'T5', 'T4', ('T2', 'T4'), 'T10')),
            ('ind_r', 'R', ('rel46', 'rel35', 'R3', 'T6', 'T3', ('T1', 'T3'), 'T8'))):
        pl = join(spare_in, link(2, Y(a_in), Y('S1b'), True), A(plus[k]), link(0, Y(o_t), Y(a_in)),
                  B(join(plus[k], ext_out(Y(o_t), EXT[op]))), [(mx, my + EXT[op]), (mx, my + MID[1])])
        mi = join([pl[-1], (mx, my + EXT[ip])], B(join(ext_in(EXT[ip], Y(i_t)), minus[k])),
                  link(1, Y(hop_t[0]), Y(r_t), True), A(join(hop(Y(hop_t[0]), Y(hop_t[1])), minus[k])), link(3, Y(r_t), Y('S2b')),
                  B(join([t('S2b')], [t('S2a')], ext_out(Y('S2a'), EXT['sp2']))))
        F[sid] = [('ind', 'p', pl, ''), ('ind', 'm', mi, '')]
    for sid in ('mot_n1', 'mot_n2', 'mot_r1', 'mot_r2'):    # 전환 중: (+) 가 A 회로제어기 접점에서 막힘
        k = 'N' if sid.startswith('mot_n') else 'R'
        blk = join(spare_in, link(2, Y('N4' if k == 'N' else 'R3'), Y('S1b'), True), A(blkp[k]))
        F[sid] = [('ind', 'p', blk, ''), ('ind', 'x', [blk[-1]], 'x')]
    mn, mr = motor('N'), motor('R')
    C = ctrl_flows()
    # 제어전원: 기구함 선은 메인(밑 단 B) (+)(−) 단자로 들어오고, 같은 단자에서 보조(A) 단자로 건너감(계통도 205 제어전원 타원)
    from wiring_states import STATES
    cl = lambda i, t, rev: (lambda p: p[::-1] if rev else p)([(X, 10 + dy + Y(t)), (10 + W + 15 + i * LANE, 10 + dy + Y(t)), (10 + W + 15 + i * LANE, 10 + Y(t)), (X, 10 + Y(t))])
    for sid in C:
        for f in (A, B):
            F.setdefault(sid, []).extend((k, l, f(p), m) for k, l, p, m in C[sid])
        rev = STATES[sid][0] != 'N'     # N: B(+) -> A(+) ... A(−) -> B(−), R: 반대
        F[sid] += [('ctrl', 'm' if rev else 'p', cl(4, 'CP', rev), ''), ('ctrl', 'p' if rev else 'm', cl(5, 'CM', not rev), '')]
        # 기구함 -> 메인(B) 제어 단자 (들어오는 선·나가는 선)
        i_t, o_t = ('CP', 'CM') if not rev else ('CM', 'CP')
        # 기구함에서 오는 선은 우상단에서 좌하단으로 비스듬히 들어온다(DIAG)
        F[sid] += [('ctrl', 'p', [(10 + XE + DIAG, 10 + dy + Y(i_t) - DIAG), (10 + XE, 10 + dy + Y(i_t)), (X, 10 + dy + Y(i_t))], ''),
                   ('ctrl', 'm', [(X, 10 + dy + Y(o_t)), (10 + XE, 10 + dy + Y(o_t)), (10 + XE + DIAG, 10 + dy + Y(o_t) - DIAG)], '')]
    # 모터전원: 기구함 -> 메인(B) 외부 단자 C -> B 와 A 로 병렬 -> D -> 기구함. A 는 B 의 C·D 외부점에서 연결선으로 받는다.
    XT = 10 + 910.6
    ml = lambda i, name, rev=False: (lambda p: p[::-1] if rev else p)([(XT, 10 + dy + EXT[name]), (10 + W + 15 + i * LANE, 10 + dy + EXT[name]), (10 + W + 15 + i * LANE, 10 + EXT[name]), (XT, 10 + EXT[name])])
    for sid, mot in (('mot_n1', mn), ('mot_n2', mn), ('mot_r1', mr), ('mot_r2', mr)):
        mod = 'dim' if sid.endswith('1') else ''
        (_, pc), (_, pd) = legs(mot, NAMED['Bc'])
        F[sid] += [('mot', 'p', [(XT + DIAG, 10 + dy + EXT['motC'] - DIAG)] + B(pc), mod), ('mot', 'm', B(pd) + [(XT + DIAG, 10 + dy + EXT['motD'] - DIAG)], mod),
                   ('mot', 'p', join(ml(6, 'motC'), A(pc)), mod), ('mot', 'm', join(A(pd), ml(7, 'motD', True)), mod)]
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
