# 도면(PDF 벡터) 기반 선로전환기 보드 SVG 생성기. 출력: board_svg/FIELD_SW_*.svg
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pymupdf
from vec2 import extract, render

ROOT = r'C:\Users\김영추\Desktop\2호선 PDF 자료'
PDF = os.path.join(ROOT, '선로전환기 제작도면.pdf')
PDF_INST = os.path.join(ROOT, '선로전환기 설치상세도(정반위표시등 포함).pdf')
OUT = r'C:\Users\김영추\Desktop\ATO app\board_svg'
doc = pymupdf.open(PDF)
S = 2.4  # width/height 속성 배율(viewBox 는 pt 단위)
STYLE = ('<style>.fsw-t{font:5px sans-serif;fill:#222}.fsw-h{font:bold 6px sans-serif;fill:#222}.fsw-s{font:3.8px sans-serif;fill:#333}'
         '.fsw-hot{fill:rgba(224,48,30,.14);stroke:#e0301e;stroke-width:1;stroke-dasharray:3 2;cursor:pointer}'
         '.fsw-jmp{fill:none;stroke:#c0392b;stroke-width:1.6}.fsw-tag{fill:#f2d21e;stroke:#333;stroke-width:.4}'
         '.fsw-role{fill:none;stroke:#555;stroke-width:.4}</style>')


def T(x, y, s, c='fsw-t', a='middle'):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{c}" text-anchor="{a}">{s}</text>'


def hot(x, y, w, h, mp, id_):
    return f'<g id="{id_}" data-act="mp" data-mp="{mp}"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="2" class="fsw-hot"/></g>'


def px21(x, y):  # 확인용 2배 렌더 픽셀 -> 페이지 pt
    return 28 + x / 2, 174 + y / 2


def body_core():
    clip = (28, 174, 509, 386)
    ox, oy = clip[0], clip[1]

    def R(x0, y0, x1, y1):
        a = px21(x0, y0); b = px21(x1, y1); return (a[0], a[1], b[0], b[1])
    regions = [
        ('motor-terminal', R(395, 265, 460, 320)),
        ('relay-control', R(640, 118, 752, 192)),
        ('relay-circuit', R(640, 255, 752, 312)),
        ('terminal-green', R(752, 135, 780, 192)),
        ('terminal-yellow', R(752, 250, 780, 302)),
        ('breaker-wiring', R(752, 192, 790, 250)),
        ('lock-switch', R(650, 192, 745, 255)),
        ('motor', R(0, 130, 262, 310)),
        ('gear', R(262, 100, 640, 330)),
        ('gland', R(880, 100, 975, 360)),
    ]
    skip = [(380, 174, 408, 196), (480, 368, 512, 396)]  # 호출 번호 '5'
    g, W, H = extract(doc[20], clip, regions, skip=skip)
    for gid, d in g.items():  # 호출 지시선(대각 직선) 제거
        for a, ds in d.items():
            keep = []
            for dd in ds:
                m = re.fullmatch(r'M([-\d.]+) ([-\d.]+)l([-\d.]+) ([-\d.]+)', dd)
                if m:
                    dx, dy = float(m.group(3)), float(m.group(4))
                    if (dx * dx + dy * dy) ** .5 >= 22 and abs(dx) > 3 and abs(dy) > 3:
                        continue
                keep.append(dd)
            d[a] = keep
    return render(g), W, H, ox, oy


def lamp_group():
    d = pymupdf.open(PDF_INST)
    g, W, H = extract(d[6], (460, 575, 590, 706), [])
    return render(g), W, H


LABELS_TOP = [('전동기', 45, (65, 80)), ('기어·캠(전환부)', 150, (195, 100)), ('제어계전기', 300, (348, 70)),
              ('쇄정 감지 스위치', 365, (352, 108)), ('단자반(녹색)', 440, (383, 80))]
LABELS_BOT = [('모터 단자블록(F E D)', 190, (212, 148)), ('회로제어기', 310, (348, 140)), ('단자반(노랑·적)', 385, (383, 138)),
              ('케이블 인입구', 455, (467, 138))]


def labels(my, H):
    o = []
    for t, x, (tx, ty) in LABELS_TOP:
        o.append(f'<line x1="{x}" y1="{my-14}" x2="{tx}" y2="{my+ty:.0f}" class="fsw-role"/>' + T(x, my - 17, t, 'fsw-s'))
    for t, x, (tx, ty) in LABELS_BOT:
        o.append(f'<line x1="{x}" y1="{my+H+6:.0f}" x2="{tx}" y2="{my+ty:.0f}" class="fsw-role"/>' + T(x, my + H + 14, t, 'fsw-s'))
    return ''.join(o)


def body_svg(ver):
    core, W, H, ox, oy = body_core()
    a = px21(650, 192); b = px21(745, 255)
    hs = lambda sfx: hot(a[0] - ox, a[1] - oy, b[0] - a[0], b[1] - a[1], 'MP_FIELD_SW_LOCK', 'lock-hot' + sfx)
    lamp, lw, lh = lamp_group()
    my = 50
    Wt = W + 12 + lw / 2 + 6

    def lampsvg(dy):
        return (f'<g id="np-lamp" transform="translate({W+12:.0f},{dy+60:.0f}) scale(.5)">{lamp}</g>'
                + T(W + 12 + lw / 4, dy + 52, '정반위표시등(전면)', 'fsw-s')
                + f'<line x1="{W+12:.0f}" y1="{dy+60+lh/4:.0f}" x2="{W-12:.0f}" y2="{dy+my+107:.0f}" class="fsw-role" stroke-dasharray="2 2"/>')
    ttl = 'NS-AM형 전기선로전환기(개량형) 외형 — 뚜껑 열림'
    if ver == 'SINGLE':
        inner = (f'<g id="body" transform="translate(0,{my})">{core}</g><g transform="translate(0,{my})">{hs("")}</g>'
                 + labels(my, H) + lampsvg(0) + T(6, 10, ttl + ' (단동·쌍동 동일)', 'fsw-h', 'start'))
        Ht = my + H + 24
    else:
        step = my + H + 24 + 14

        def one(sfx, dy):
            return (f'<g id="body{sfx}" transform="translate(0,{dy+my})"><use href="#core"/></g>'
                    f'<g transform="translate(0,{dy+my})">{hs(sfx)}</g><g transform="translate(0,{dy})">' + labels(my, H) + '</g>'
                    + T(6, dy + 10, f'{sfx[1]}호기 — ' + ttl + ' (쌍동)', 'fsw-h', 'start'))
        inner = f'<defs><g id="core">{core}</g></defs>' + one('-A', 0) + one('-B', step) + lampsvg(0)
        Ht = 2 * step - 14
    return (f'<svg width="{Wt*S:.0f}" height="{Ht*S:.0f}" viewBox="0 0 {Wt:.0f} {Ht:.0f}" xmlns="http://www.w3.org/2000/svg">'
            f'{STYLE}<rect width="{Wt:.0f}" height="{Ht:.0f}" fill="#fff"/>{inner}</svg>')


# ---------------- 단자반 보드 (제작도면 p.23 평면도 + 설치상세도 p.5 결선도) ----------------
CELLS = {'+': 56.2, '-': 66.7, 'R3': 77.3, 'N4': 87.8, '8': 98.3, '10': 108.8, 'C': 142.0, 'D': 156.0,
         '5': 213.2, '3': 223.6, '1': 234.0, '2': 244.4, '4': 254.8, '6': 265.2}
TAGS = [('R3', '반위'), ('N4', '정위'), ('8', '반위'), ('10', '정위'), ('5', '정위'), ('1', '반위'), ('2', '정위'), ('6', '반위')]  # 사진 참고
J_SINGLE = [('R3', 'N4'), ('8', '10'), ('5', '3'), ('1', '2'), ('4', '6')]
J_A = [('R3', 'N4'), ('8', '10'), ('3', '1'), ('2', '4')]
J_B = [('5', '3'), ('1', '2'), ('4', '6')]


def strip_core():
    g, W, H = extract(doc[22], (88, 176, 412, 254), [], skip=[(383, 176, 412, 254)])
    for gid, d in g.items():  # 호출 지시선 제거
        for a, ds in d.items():
            d[a] = [dd for dd in ds if not (lambda m: m and (float(m.group(3)) ** 2 + float(m.group(4)) ** 2) ** .5 >= 22
                                           and abs(float(m.group(3))) > 3 and abs(float(m.group(4))) > 3)(
                re.fullmatch(r'M([-\d.]+) ([-\d.]+)l([-\d.]+) ([-\d.]+)', dd))]
    return render(g), W, H


def strip_overlay(sfx, jumps, mp=True):
    o = []
    for k, x in CELLS.items():
        lab = {'+': '(+)', '-': '(−)'}.get(k, k)
        o.append(T(x, 51.5, lab, 'fsw-h'))
    o.append(T(148.5, 36, 'MOTOR', 'fsw-s'))
    for a, b in jumps:
        o.append(f'<path id="jumper-{a}-{b}{sfx}" d="M{CELLS[a]} 26V17H{CELLS[b]}V26" class="fsw-jmp"/>')
    for k, l in TAGS:
        x = CELLS[k]
        o.append(f'<rect x="{x-5:.1f}" y="82" width="10" height="7" class="fsw-tag"/>' + T(x, 87.5, l, 'fsw-s'))
    def br(k1, k2, label, mpid=None):
        x1, x2 = CELLS[k1] - 4.5, CELLS[k2] + 4.5
        r = f'<g id="role-{k1}{sfx}"' + (f' data-act="mp" data-mp="{mpid}"' if mpid else '') + '>'
        if mpid:
            r += f'<rect x="{x1-1:.1f}" y="26" width="{x2-x1+2:.1f}" height="50" class="fsw-hot"/>'
        return r + f'<path d="M{x1:.1f} 94v3H{x2:.1f}v-3" class="fsw-role"/>' + T((x1 + x2) / 2, 106, label, 'fsw-s') + '</g>'
    o.append(br('+', '-', '제어전원', 'MP_FIELD_SW_CONTROL'))
    o.append(br('R3', '10', '표시전원 입력', 'MP_FIELD_SW_INDICATION'))
    o.append(br('C', 'D', '모터전원', 'MP_FIELD_SW_MOTOR'))
    o.append(br('5', '6', '표시전원 출력(→표시계전기)'))
    o.append(T(0, 118, '※ 정위/반위 태그는 현장 사진 참고(도면 외)', 'fsw-s', 'start'))
    return ''.join(o)


def wiring_group():
    d = pymupdf.open(PDF_INST)
    g, W, H = extract(d[4], (115, 140, 1100, 725), [])
    return render(g), W, H


def strip_svg(ver):
    """단자대(단자반 평면)만 크게. 쌍동은 A·B 2세트."""
    core, sw, sh = strip_core()
    core = '<g clip-path="url(#fswsc)">' + core + '</g>'  # 도면 치수선 등 단자대 밖 선 잘라냄
    clipdef = '<clipPath id="fswsc"><rect x="-4" y="0" width="300" height="80"/></clipPath>'
    SC = 2.4
    Wt = sw * SC + 80
    blocks = []
    y = 28
    if ver == 'SINGLE':
        specs = [('', J_SINGLE, '선로전환기 단자대 — 단동 (제작도면 p.23 평면도)')]
        defs = f'<defs>{clipdef}</defs>'
    else:
        specs = [('-A', J_A, 'A호기 단자대 — 쌍동 A'), ('-B', J_B, 'B호기 단자대 — 쌍동 B')]
        defs = f'<defs>{clipdef}<g id="stripcore">{core}</g></defs>'
    for sfx, jm, title in specs:
        body = core if ver == 'SINGLE' else '<use href="#stripcore"/>'
        blocks.append(T(10, y - 10, title, 'fsw-h', 'start')
                      + f'<g id="strip{sfx}" transform="translate(40,{y}) scale({SC})">{body}{strip_overlay(sfx, jm)}</g>')
        y += 122 * SC + 24
    Ht = y - 10
    return (f'<svg width="{Wt*1.3:.0f}" height="{Ht*1.3:.0f}" viewBox="0 0 {Wt:.0f} {Ht:.0f}" xmlns="http://www.w3.org/2000/svg">'
            f'{STYLE}<rect width="{Wt:.0f}" height="{Ht:.0f}" fill="#fff"/>{defs}{"".join(blocks)}</svg>')


FLOW_STYLE = ('<style>.fsw-flowbase{fill:none;stroke-width:3.4;stroke-opacity:.16;stroke-linejoin:round}'
              '.fsw-flow{fill:none;stroke-width:2.8;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:.1 9;animation:fswflow .9s linear infinite}'
              '.fsw-fb-ctrl,.fsw-fl-ctrl{stroke:#2563eb}.fsw-fb-ind,.fsw-fl-ind{stroke:#16a34a}.fsw-fb-mot,.fsw-fl-mot{stroke:#e11d48}'
              '@keyframes fswflow{to{stroke-dashoffset:-9.1}}'
              '@media (prefers-reduced-motion:reduce){.fsw-flow{animation:none;stroke-dasharray:none}}</style>')


def wiring_svg():
    """내부 결선도(설치상세도 p.5) + 전원 흐름 애니메이션. 참고자료 팝업용."""
    import wiring_anim
    wir, ww, wh = wiring_group()
    ov = wiring_anim.overlay(wiring_anim.build())
    Wt, Ht = ww + 20, wh + 20
    return (f'<svg width="{Wt*1.3:.0f}" height="{Ht*1.3:.0f}" viewBox="0 0 {Wt:.0f} {Ht:.0f}" xmlns="http://www.w3.org/2000/svg">'
            f'{STYLE}{FLOW_STYLE}<rect width="{Wt:.0f}" height="{Ht:.0f}" fill="#fff"/>'
            f'<g id="wiring" transform="translate(10,10)">{wir}{ov}</g></svg>')


if __name__ == '__main__':
    for v in ('SINGLE', 'DOUBLE'):
        for kind, fn in (('BODY', body_svg), ('STRIP', strip_svg)):
            if kind == 'BODY' and v == 'DOUBLE':   # 외형은 단동·쌍동 동일 — 단동 이미지 하나만
                continue
            t = fn(v)
            open(os.path.join(OUT, f'FIELD_SW_{v}_{kind}.svg'), 'w', encoding='utf-8').write(t)
            print(v, kind, len(t))
    import wiring_states
    wiring_states.write_all(OUT)
