# 실제 배선도(설치상세도 p.5) 위에서 제어계전기·회로제어기 접점 기호만 상태별로 바꾼 SVG 를 만든다.
import os, re, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pymupdf
from vec2 import extract, render

PDF_INST = r'C:\Users\김영추\Desktop\2호선 PDF 자료\선로전환기 설치상세도(정반위표시등 포함).pdf'
CLIP = (115, 140, 1100, 725)
OX, OY = CLIP[0], CLIP[1]

# 접점 기호가 있는 영역(클립 좌표). 핀 점은 제외하고 혀·화살표·점선 곡선만 담는다.
RELAY = {  # id: (pivot, N pin, R pin)
    'C1': ((207.8, 110.0), (229.5, 93.0), (229.5, 127.3)),
    'C2': ((209.0, 170.0), (229.5, 152.0), (229.5, 186.5)),
    'C3': ((266.5, 113.0), (290.0, 95.0), (290.0, 130.0)),
    'C4': ((266.5, 172.3), (290.0, 154.5), (290.0, 188.5)),
}
RELAY_BOX = {  # 혀·N/R 화살표를 통째로 담는 상자(도면 좌표 실측)
    'C1': [(207.0, 103.5, 236.0, 111.8), (227.0, 99.3, 232.5, 106.2), (227.0, 113.8, 232.5, 121.0)],
    'C2': [(207.5, 162.8, 237.0, 171.0), (227.0, 158.0, 232.5, 165.5), (227.0, 172.5, 232.5, 180.5)],
    'C3': [(265.5, 105.8, 296.0, 114.0), (287.0, 101.0, 294.0, 108.5), (287.0, 116.5, 294.0, 124.0)],
    'C4': [(265.5, 163.8, 296.5, 173.3), (287.0, 160.5, 294.0, 168.5), (287.0, 175.0, 294.0, 182.5)],
}
ROWS = {'1': 329.0, '2': 353.6, '3': 379.0, '4': 404.6}
CTRL = {  # id: (pin P, pin Q, (x0,x1) 영역 가로, 행)
    'NC1': ('G', 'A', (211.5, 228.5), '1'), 'NC2': ('1', '6', (211.5, 228.5), '2'),
    'N1': ('9', '5', (211.5, 228.5), '3'), 'N2': ('10', '4', (211.5, 228.5), '4'),
    'R1': ('3', '8', (300.5, 322.5), '1'), 'R2': ('6', '7', (300.5, 322.5), '2'),
    'RC1': ('5', '2', (300.5, 322.5), '3'), 'RC2': ('B', 'G', (300.5, 322.5), '4'),
}
PIN = {  # 핀 좌표(클립)
    'G': (213.5, 329.0), 'A': (230.0, 328.0), '1': (213.5, 353.5), '6': (230.0, 353.0), '9': (213.5, 379.0), '5': (230.0, 379.0),
    '10': (213.5, 404.7), '4': (230.0, 404.0), '3': (302.6, 329.0), '8': (325.0, 329.0), '6r': (302.6, 354.0), '7': (325.0, 354.0),
    '5r': (302.6, 379.0), '2': (325.0, 379.0), 'B': (302.6, 404.7), 'Gr': (325.0, 404.7),
}
# 회로제어기 접점 핀 짝(실제 핀 좌표 기준)
CPAIR = {'NC1': ('G', 'A'), 'NC2': ('1', '6'), 'N1': ('9', '5'), 'N2': ('10', '4'),
         'R1': ('3', '8'), 'R2': ('6r', '7'), 'RC1': ('5r', '2'), 'RC2': ('B', 'Gr')}
STATES = {  # 상태: (제어계전기, 닫힌 회로제어기 접점)
    'ind_n': ('N', ['NC1', 'NC2', 'N1', 'N2']),
    'ind_r': ('R', ['R1', 'R2', 'RC1', 'RC2']),
    'mot_n1': ('N', ['R1', 'R2', 'RC1', 'RC2']),
    'mot_n2': ('N', ['NC1', 'NC2', 'RC1', 'RC2']),
    'mot_r1': ('R', ['NC1', 'NC2', 'N1', 'N2']),
    'mot_r2': ('R', ['NC1', 'NC2', 'RC1', 'RC2']),
}


def regions():
    R = []
    for k, boxes in RELAY_BOX.items():
        for i, (x0, y0, x1, y1) in enumerate(boxes):
            R.append((f'ctb_{k}_{i}', (x0 + OX, y0 + OY, x1 + OX, y1 + OY)))
    for k, (_, _, (x0, x1), row) in CTRL.items():
        y = ROWS[row]
        R.append((f'ct_{k}', (x0 + OX, y - 14 + OY, x1 + OX, y + 7 + OY)))
    return R


STRIP_COLORS = [  # 단자대 블록 색(클립 좌표, 단자대 보드와 같은 배치): 초록=표시 출력, 노랑=표시 입력, 빨강=제어, 하늘=예비(Interface)
    ('#00b050', 60.5, 92.7), ('#00b050', 96.2, 128.2), ('#00b050', 131.7, 163.7),
    ('#ffd800', 320.3, 352.5), ('#ffd800', 356.0, 388.0), ('#ff2a2a', 391.5, 423.5), ('#19d3ff', 427.0, 459.0),
]
JUMP_Y = {'4': 80.2, '6': 72.2, '2': 107.7, '1': 115.7, '3': 143.2, '5': 151.2, '10': 332.0, '8': 340.0, 'N4': 367.5, 'R3': 375.5}
JUMPERS = {  # 설치상세도 점퍼표
    'single': [('R3', 'N4'), ('8', '10'), ('5', '3'), ('1', '2'), ('4', '6')],
    'A': [('R3', 'N4'), ('8', '10'), ('3', '1'), ('2', '4')],
    'B': [('5', '3'), ('1', '2'), ('4', '6')],
}


def strip_colors():
    return '<g class="fsw-stripc">' + ''.join(
        f'<rect x="831.8" y="{y0}" width="46.8" height="{y1 - y0:.1f}" fill="{c}" fill-opacity=".30"/>' for c, y0, y1 in STRIP_COLORS) + '</g>'


def jumpers(kind):
    o = ''
    for a, b in JUMPERS[kind]:
        y1, y2 = JUMP_Y[a], JUMP_Y[b]
        x = 850.0 if abs(y1 - y2) > 12 else 846.0   # 블록을 건너는 점퍼는 한 칸 더 오른쪽
        o += f'<path d="M838.5 {y1}H{x}V{y2}H838.5" fill="none" stroke="#e11d1d" stroke-width="2" stroke-linejoin="round"><title>점퍼 {a}-{b}</title></path>'
    return f'<g class="fsw-jmps">{o}</g>'


def base():
    d = pymupdf.open(PDF_INST)
    g, W, H = extract(d[4], CLIP, regions(), subpaths=True)
    hidden = {k: v for k, v in g.items() if k.startswith('ct')}
    keep = {k: v for k, v in g.items() if not k.startswith('ct')}
    # E·F 선(두꺼운 이중선)은 x=207.8 에서 끝나고 C1/C2 피벗은 14pt 위에 떠 있어 -> 세로선으로 이어 붙임
    join = ''.join(line((207.8, py), (207.8, wy), 1.5) for py, wy in ((110.0, 124.2), (170.0, 183.6)))
    join += line((213.6, 341.4), (213.5, 353.5), 1.4)  # 핀 1 으로 가는 선(접점 영역에 묻혀 끊김)
    return strip_colors() + render(keep) + join, W, H, hidden


def line(a, b, w=1.4, extra=''):
    return f'<path d="M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}" fill="none" stroke="#000" stroke-width="{w}" stroke-linecap="round" {extra}/>'


def relay_symbols(state_relay):
    o = []
    for k, (cp, npin, rpin) in RELAY.items():
        tgt = npin if state_relay == 'N' else rpin
        o.append(line(cp, tgt, 1.5))
        other = rpin if state_relay == 'N' else npin
        # 열린 쪽 접점: 짧은 간극 표시(작은 화살표)
        d = 1 if other[1] > cp[1] else -1
        o.append(f'<path d="M{other[0]-2.4:.1f} {other[1]-d*8:.1f}L{other[0]:.1f} {other[1]-d*3.2:.1f}L{other[0]+2.4:.1f} {other[1]-d*8:.1f}" fill="none" stroke="#000" stroke-width=".8"/>')
    return ''.join(o)


def ctrl_symbols(closed):
    o = []
    for k, (a, b) in CPAIR.items():
        pa, pb = PIN[a], PIN[b]
        if k in closed:
            o.append(line(pa, pb, 1.6))
        else:  # 열림: 피벗에서 비스듬히 뜬 혀
            mx = pa[0] + (pb[0] - pa[0]) * 0.62
            o.append(line(pa, (mx, pa[1] - 6.5), 1.3))
    return ''.join(o)


def state_group(sid):
    rel, closed = STATES[sid]
    return f'<g class="fsw-ws ws-{sid}">{relay_symbols(rel)}{ctrl_symbols(closed)}</g>'


if __name__ == '__main__':
    b, W, H, hidden = base()
    print(round(W), round(H), len(b), {k: sum(len(x) for v in d.values() for x in v) for k, d in hidden.items()})


# ---------------- 단동/쌍동 배선도 SVG (제어전원 흐름 + 접점 상태별 정지 화면) ----------------
SID = list(STATES)
STYLE = ('<style>.fsw-t{font:6px sans-serif;fill:#222}.fsw-h{font:bold 9px sans-serif;fill:#222}.fsw-s{font:5px sans-serif;fill:#444}'
         '.fsw-ws{display:none}' + ''.join(f'svg.wsv-{k} .ws-{k}{{display:inline}}' for k in SID) +
         '.fsw-x{fill:none;stroke:#111;stroke-width:2.2;stroke-linecap:round}.fsw-mlab{display:none;font:5px sans-serif;fill:#444}svg.only-mot .fsw-mlab{display:inline}'
         '.fsw-mod-dim .fsw-flow{display:none}.fsw-mod-dim .fsw-flowbase{stroke-opacity:.32}'
         + ''.join(f'svg.only-{k} .fsw-k-{j}{{display:none}}' for k, js in (('ctrl', ('ind', 'mot')), ('ind', ('ctrl', 'mot')), ('mot', ('ctrl', 'ind'))) for j in js) +
         'svg.pol .fsw-leg-p .fsw-flowbase,svg.pol .fsw-leg-p .fsw-flow{stroke:#dc2626}svg.pol .fsw-leg-m .fsw-flowbase,svg.pol .fsw-leg-m .fsw-flow{stroke:#2563eb}'
         '.fsw-flowbase{fill:none;stroke-width:3.4;stroke-opacity:.16;stroke-linejoin:round}'
         '.fsw-flow{fill:none;stroke-width:2.8;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:.1 9;animation:fswflow .9s linear infinite}'
         '.fsw-fb-ctrl,.fsw-fl-ctrl{stroke:#2563eb}.fsw-fb-ind,.fsw-fl-ind{stroke:#16a34a}.fsw-fb-mot,.fsw-fl-mot{stroke:#dc2626}@keyframes fswflow{to{stroke-dashoffset:-9.1}}'
         '@media (prefers-reduced-motion:reduce){.fsw-flow{animation:none;stroke-dasharray:none}}</style>')


def single_svg():
    b, W, H, _ = base()
    states = ''.join(state_group(k) for k in SID)
    import wiring_flow
    ov = wiring_flow.overlay(wiring_flow.single_flows()) + wiring_flow.mot_labels()
    Wt, Ht = W + 20, H + 20
    return (f'<svg width="{Wt*1.3:.0f}" height="{Ht*1.3:.0f}" viewBox="0 0 {Wt:.0f} {Ht:.0f}" xmlns="http://www.w3.org/2000/svg">{STYLE}'
            f'<rect width="{Wt:.0f}" height="{Ht:.0f}" fill="#fff"/><g id="wiring" transform="translate(10,10)">{b}{jumpers('single')}{states}{ov}</g></svg>')


# 쌍동: A 호기 표시출력 단자 -> B 호기 표시입력 단자 연결(계통도 205 정위/반위 페이지에서 읽음)
LINK_Y = {'out': {'T1': 116.0, 'T2': 108.0, 'T5': 151.0, 'T6': 72.0}, 'in': {'T10': 324.0, 'T8': 348.0, 'N4': 367.0, 'R3': 376.0}}
LINKS = {  # 상태: [(A 출력, B 입력, 색, 라벨)]
    'ind_r': [('T1', 'T8', '#808080', 'A 단자1 → B 단자8'), ('T6', 'R3', '#00b050', 'A 단자6 → B 단자R3')],
    'ind_n': [('T2', 'T10', '#808080', 'A 단자2 → B 단자10'), ('T5', 'N4', '#00b050', 'A 단자5 → B 단자N4')],
}


def double_svg():
    b, W, H, _ = base()
    states = ''.join(state_group(k) for k in SID)
    gap = 40
    dy = H + gap
    Wt, Ht = W + 70, 2 * H + gap + 40
    X = 838.5 + 10
    import wiring_flow
    flows = wiring_flow.overlay(wiring_flow.double_flows(W, dy, LINK_Y))
    link = ''
    for k, lst in LINKS.items():
        o = ''
        for i, (a, bb_, col, lab) in enumerate(lst):
            ya = 10 + LINK_Y['out'][a]; yb = 10 + dy + LINK_Y['in'][bb_]
            xr = 10 + W - 15 + i * 12
            o += (f'<path d="M{X} {ya}H{xr}V{yb}H{X}" fill="none" stroke="{col}" stroke-width="2.4" stroke-linejoin="round"/>'
                  f'<text x="{xr+4}" y="{(ya+yb)/2:.0f}" class="fsw-s">{lab}</text>')
        link += f'<g class="fsw-ws ws-{k}">{o}</g>'
    for i, (t, col, lab_) in enumerate((('CP', '#00b0f0', '제어(+)'), ('CM', '#002060', '제어(−)'))):
        yb = 10 + dy + wiring_flow.Y(t); ya = 10 + wiring_flow.Y(t); xr = 10 + W - 15 + (2 + i) * 12
        link += (f'<path d="M{X} {yb}H{xr}V{ya}H{X}" fill="none" stroke="{col}" stroke-width="2.4" stroke-linejoin="round"/>'
                 f'<text x="{xr+4}" y="{(ya+yb)/2 + 40*i - 20:.0f}" class="fsw-s">{lab_}</text>')
    lab = (f'<text x="10" y="8" class="fsw-h">A호기</text><text x="10" y="{dy+8}" class="fsw-h">B호기</text>')
    return (f'<svg width="{Wt*1.3:.0f}" height="{Ht*1.3:.0f}" viewBox="0 0 {Wt:.0f} {Ht:.0f}" xmlns="http://www.w3.org/2000/svg">{STYLE}'
            f'<rect width="{Wt:.0f}" height="{Ht:.0f}" fill="#fff"/><defs><g id="wcore">{b}</g></defs>{lab}'
            f'<g id="wiring-A" transform="translate(10,10)"><use href="#wcore"/>{jumpers('A')}{states}{wiring_flow.mot_labels()}</g>'
            f'<g id="wiring-B" transform="translate(10,{10+dy:.0f})"><use href="#wcore"/>{jumpers('B')}{states}{wiring_flow.mot_labels()}</g>{link}{flows}</svg>')


def write_all(out_dir):
    for name, fn in (('FIELD_SW_WIRING', single_svg), ('FIELD_SW_WIRING_DOUBLE', double_svg)):
        t = fn()
        open(os.path.join(out_dir, name + '.svg'), 'w', encoding='utf-8').write(t)
        print(name, len(t))
