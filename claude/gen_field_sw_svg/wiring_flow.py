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


def single_flows():
    """단동: {상태: [(클래스, 폴리라인)]}  (지역 좌표)"""
    F = {}
    F['ind_n'] = [
        ('ind', join(ext_in(EXT['indp'], Y('T10')), wire('T10', 'p10'), seg('p10', 'p4'), wire('p4', 'T4'), ext_out(Y('T4'), EXT['rel46']))),
        ('ind', join(ext_in(EXT['rel35'], Y('T5')), wire('T5', 'p5'), seg('p5', 'p9'), wire('p9', 'C4'), relay('C4', 'N'), wire('C4n', 'N4'), ext_out(Y('N4'), EXT['indm']))),
    ]
    F['ind_r'] = [
        ('ind', join(ext_in(EXT['indp'], Y('T8')), wire('T8', 'p8'), seg('p8', 'p3'), wire('p3', 'T3'), ext_out(Y('T3'), EXT['rel35']))),
        ('ind', join(ext_in(EXT['rel46'], Y('T6')), wire('T6', 'p6r'), seg('p6r', 'p7'), wire('p7', 'C3'), relay('C3', 'R'), wire('C3r', 'R3'), ext_out(Y('R3'), EXT['indm']))),
    ]
    mn, mr = motor('N'), motor('R')
    F['mot_n1'] = F['mot_n2'] = [('mot', mn)]
    F['mot_r1'] = F['mot_r2'] = [('mot', mr)]
    return F


def double_flows(W, dy, LINK_Y):
    """쌍동: 전역 좌표(A 는 +(10,10), B 는 +(10,10+dy)) 폴리라인."""
    X = 838.5 + 10
    A = lambda pts: [(x + 10, y + 10) for x, y in pts]
    B = lambda pts: [(x + 10, y + 10 + dy) for x, y in pts]
    link = lambda i, a, b, rev=False: ([(X, 10 + LINK_Y['out'][a]), (10 + W - 15 + i * 12, 10 + LINK_Y['out'][a]), (10 + W - 15 + i * 12, 10 + dy + LINK_Y['in'][b]), (X, 10 + dy + LINK_Y['in'][b])][::-1 if rev else 1])
    F = {}
    F['ind_n'] = [
        ('ind', join(A(join(ext_in(EXT['indp'], Y('T10')), wire('T10', 'p10'), seg('p10', 'p4'), wire('p4', 'T4'), hop(Y('T4'), Y('T2')))),
                     link(0, 'T2', 'T10'),
                     B(join([(838.5, Y('T10'))], wire('T10', 'p10'), seg('p10', 'p4'), wire('p4', 'T4'), ext_out(Y('T4'), EXT['rel46']))))),
        ('ind', join(B(join(ext_in(EXT['rel35'], Y('T5')), wire('T5', 'p5'), seg('p5', 'p9'), wire('p9', 'C4'), relay('C4', 'N'), wire('C4n', 'N4'), [(838.5, Y('N4'))])),
                     link(1, 'T5', 'N4', True),
                     A(join([(838.5, Y('T5'))], wire('T5', 'p5'), seg('p5', 'p9'), wire('p9', 'C4'), relay('C4', 'N'), wire('C4n', 'N4'), ext_out(Y('N4'), EXT['indm']))))),
    ]
    F['ind_r'] = [
        ('ind', join(A(join(ext_in(EXT['indp'], Y('T8')), wire('T8', 'p8'), seg('p8', 'p3'), wire('p3', 'T3'), hop(Y('T3'), Y('T1')))),
                     link(0, 'T1', 'T8'),
                     B(join([(838.5, Y('T8'))], wire('T8', 'p8'), seg('p8', 'p3'), wire('p3', 'T3'), ext_out(Y('T3'), EXT['rel35']))))),
        ('ind', join(B(join(ext_in(EXT['rel46'], Y('T6')), wire('T6', 'p6r'), seg('p6r', 'p7'), wire('p7', 'C3'), relay('C3', 'R'), wire('C3r', 'R3'), [(838.5, Y('R3'))])),
                     link(1, 'T6', 'R3', True),
                     A(join([(838.5, Y('T6'))], wire('T6', 'p6r'), seg('p6r', 'p7'), wire('p7', 'C3'), relay('C3', 'R'), wire('C3r', 'R3'), ext_out(Y('R3'), EXT['indm']))))),
    ]
    mn, mr = motor('N'), motor('R')
    F['mot_n1'] = F['mot_n2'] = [('mot', A(mn)), ('mot', B(mn))]
    F['mot_r1'] = F['mot_r2'] = [('mot', A(mr)), ('mot', B(mr))]
    return F


def overlay(flows):
    """{상태: [(cls, pts)]} -> SVG 조각(상태별 그룹, 지역/전역 좌표 그대로)"""
    out = []
    for sid, lst in flows.items():
        o = ''
        for cls, pts in lst:
            d = 'M' + ' L'.join('%.1f %.1f' % p for p in pts)
            o += f'<path d="{d}" class="fsw-flowbase fsw-fb-{cls}"/><path d="{d}" class="fsw-flow fsw-fl-{cls}"/>'
        out.append(f'<g class="fsw-ws ws-{sid}">{o}</g>')
    return ''.join(out)


if __name__ == '__main__':
    for k, v in single_flows().items():
        for cls, pl in v:
            print(k, cls, len(pl), [tuple(round(c) for c in p) for p in pl])
