# '선로전환기 회로도 교육자료.PPTX'(2013, 궤도신호사업소 신호1팀 ATO과) 의 단동 회로도를 상태별 SVG 로 추출한다.
# 선행: PowerPoint 로 PDF 저장 -> deck.pdf   (PowerShell: $p.SaveAs("deck.pdf", 32))
# 원본 슬라이드의 검정 선·글자는 그대로(벡터), 빨강(전원 공급 경로)·파랑(복귀 경로) 굵은 선은 방향을 정해 점선 흐름 애니메이션으로 바꾼다.
#   빨강 = +24V(LB) 또는 BX110(C 단자) 에서 출발, 파랑 = 표시: 외부 표시계전기 -> LC(-0V) 복귀 / 모터: 전동기 D -> SW -> CX110.
import re, os, sys, math, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pymupdf
from vec2 import parse, tf, bbox, emit
import wiring_anim

DECK = os.environ.get('SW_DECK_PDF', r'C:\Users\김영추\AppData\Local\Temp\claude\C--Users-----Desktop-ATO-app\bea085ae-01b7-422c-84cb-092dafb53c96\scratchpad\ppt\deck.pdf')
OUT = r'C:\Users\김영추\Desktop\ATO app\board_svg'
CLIP = (14, 100, 650, 530)
# id: (슬라이드, 회로, 제목, 설명)
STATES = {
 'IND_N': (13, 'ind', '표시전원 — N접점(정위) 회로 구성', '정위 정지: 제어계전기·회로제어기 접점이 모두 정위(N)로 붙어 있다. +24V → 단자 8·10 → (N) 10-4 접점 → 단자 4·6 → 신호기계실 정위 표시계전기(NWP) → 단자 3·5 → (N) 9-5 접점 → C4-N4 → 단자 N4·R3 → −0V(LC).'),
 'IND_R': (20, 'ind', '표시전원 — R접점(반위) 회로 구성', '반위 정지: 접점이 모두 반위(R)로 붙어 있다. +24V → 단자 8·10 → (R) 8-3 접점 → 단자 3·5 → 신호기계실 반위 표시계전기(RWP) → 단자 4·6 → (R) 7-6 접점 → C3-R3 → 단자 N4·R3 → −0V(LC).'),
 'MOT_R1': (14, 'mot', '모터전원 — R접점 (정위→반위 전환순간)', '전환 취급 순간: 제어계전기가 반위로 동작해 순시접점 R1·R2·R3·R4 가 단락되고, 회로제어기는 아직 정위(변화 없음). 모터전원 C(BX110) → 회로제어기 (NC) → R1 → 단자 E → 전동기 앞단까지 전원이 걸린다.'),
 'MOT_R2': (16, 'mot', '모터전원 — R접점 (정위→반위 전환중)', '전환중: 동력회로가 구성되어 전동기가 반위로 회전한다. 회로제어기 (NC)·(RC) 접점이 모두 단락되고 R1 접점을 통해 단자 E → 전동기 → D → SW → CX110. 동시에 (N)·(R) 표시접점이 모두 개방되어 표시회로 구성을 막는다.'),
 'MOT_N1': (21, 'mot', '모터전원 — N접점 (반위→정위 전환순간)', '전환 취급 순간: 제어계전기가 정위로 동작해 순시접점 N1·N2·N3·N4 가 단락되고, 회로제어기는 아직 반위(변화 없음). 모터전원 C(BX110) → 회로제어기 (RC) → N2 → 단자 F → 전동기 앞단까지 전원이 걸린다.'),
 'MOT_N2': (23, 'mot', '모터전원 — N접점 (반위→정위 전환중)', '전환중: 동력회로가 구성되어 전동기가 정위로 회전한다. 회로제어기 (NC)·(RC) 접점이 모두 단락되고 N2 접점을 통해 단자 F → 전동기 → D → SW → CX110. 동시에 (N)·(R) 표시접점이 모두 개방되어 표시회로 구성을 막는다.'),
}
RED = (0.75, 0.0, 0.0); BLUE = (0.0, 0.44, 0.75)


def near(a, b): return all(abs(x - y) < 0.03 for x, y in zip(a, b))


def base_paths(page):
    """검정 선·글자 등 기본 도형(주황 해설·표·빨강/파랑 굵은선 제외) -> {attr: [d,...]}."""
    s = page.get_svg_image(text_as_path=True)
    x0, y0, x1, y1 = CLIP
    groups = {}
    for m in re.finditer(r'<path transform="matrix\(([^)]*)\)"([^>]*?)/>', s):
        M = [float(v) for v in m.group(1).split(',')]
        a = m.group(2)
        if 'clip-rule' in a:
            continue
        if 'fill="#ffffff"' in a and 'stroke=' not in a:   # 배경·그림자용 흰 면
            continue
        if '#e46c0a' in a or '#8eb4e3' in a:      # 주황 해설/불릿, 표 테두리
            continue
        if re.search(r'stroke="#(c00000|0070c0)"', a) and 'stroke-width="2.76"' in a:   # 굵은 전원 경로(별도 처리)
            continue
        dm = re.search(r' d="([^"]+)"', a)
        if not dm:
            continue
        segs = tf(parse(dm.group(1)), M)
        bb = bbox(segs)
        if not bb:
            continue
        cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
        if not (x0 <= cx <= x1 and y0 <= cy <= y1):
            continue
        if cx > 495 and cy < 280:                 # 우상단 동작상태 표
            continue
        attrs = ' '.join(re.sub(r' d="[^"]+"', '', a).replace('stroke-linecap="butt" ', '').replace('stroke-linejoin="round" ', '').split())
        if 'fill=' not in attrs:
            attrs += ' fill="#000"'
        groups.setdefault(attrs, []).append(emit(segs, 0, x0, y0))
    # 글자(글리프): <use data-text=.. xlink:href="#font_*" transform="matrix(..)" fill=".."/>
    defs = dict(re.findall(r'<path id="(font_[^"]+)" d="([^"]+)"/>', s))
    for m in re.finditer(r'<use data-text="([^"]*)" xlink:href="#(font_[^"]+)" transform="matrix\(([^)]*)\)"(?: fill="(#\w+)")?/>', s):
        ch, gid, mat, col = m.groups()
        if ch == '&#x3161;':                     # 'ㅡ' 는 선 효과용 장식 글자(검정 막대로 보임) — 제외
            continue
        col = col or '#000000'
        if col in ('#ffffff', '#e46c0a') or gid not in defs:
            continue
        M = [float(v) for v in mat.split(',')]
        segs = tf(parse(defs[gid]), M)
        bb = bbox(segs)
        if not bb:
            continue
        cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
        if not (x0 <= cx <= x1 and y0 <= cy <= y1) or (cx > 495 and cy < 280):
            continue
        groups.setdefault(f'fill="{col}" fill-rule="evenodd"', []).append(emit(segs, 0, x0, y0))
    # 래스터 조각(모터 기호, 저항, 접점 설) — 클립 안에 있는 것만
    imgs = ''
    for m in re.finditer(r'<g transform="matrix\(([^)]*)\)">\s*<image id="image_\d+" width="(\d+)" height="(\d+)" xlink:href="(data:[^"]+)"', s):
        import base64
        raw = base64.b64decode(''.join(m.group(4).split()).split(',', 1)[-1][:64] + '==')
        if (int(m.group(2)), int(m.group(3))) not in ((52, 52), (77, 38)):   # 모터 기호·저항만 사용(나머지는 선 효과용 마스크 조각)
            continue
        M = [float(v) for v in m.group(1).split(',')]
        w, h = int(m.group(2)), int(m.group(3))
        cx, cy = M[4] + M[0] * w / 2, M[5] + M[3] * h / 2
        if not (x0 <= cx <= x1 and y0 <= cy <= y1) or (cx > 495 and cy < 280):
            continue
        M[4] -= x0; M[5] -= y0
        tag = '<image transform="matrix(%s)" width="%d" height="%d" href="%s"/>' % (','.join('%g' % v for v in M), w, h, ''.join(m.group(4).split()))
        if tag not in imgs:                      # PDF 가 같은 그림을 마스크용으로 한 번 더 내보내므로 중복 제거
            imgs += tag
    return imgs + ''.join('<path %s d="%s"/>' % (a, ''.join(ds)) for a, ds in groups.items())


def colored(page):
    out = []
    for x in page.get_drawings():
        col = x.get('color'); w = x.get('width') or 0
        if not col or abs(w - 2.8) > 0.25:
            continue
        kind = 'red' if near(col, RED) else 'blue' if near(col, BLUE) else None
        if not kind:
            continue
        for it in x['items']:
            if it[0] == 'l':
                a, b = it[1], it[2]
                out.append((kind, (a.x - CLIP[0], a.y - CLIP[1], b.x - CLIP[0], b.y - CLIP[1])))
    return out


def snap(S, tol=3.2):
    """선분 끝점을 서로(또는 다른 선분 위로) 끌어 붙여 연결을 만든다."""
    pts = []
    def cl(p):
        for q in pts:
            if math.hypot(p[0]-q[0], p[1]-q[1]) <= tol:
                return q
        pts.append(p); return p
    S = [(cl((a, b)), cl((c, d))) for a, b, c, d in S]
    out = []
    for p, q in S:
        out.append([p, q])
    # 끝점 -> 다른 선분 내부 투영(T 접속)
    for i, (p, q) in enumerate(out):
        for k in (0, 1):
            pt = out[i][k]
            for j, (a, b) in enumerate(out):
                if j == i: continue
                dx, dy = b[0]-a[0], b[1]-a[1]; L2 = dx*dx+dy*dy
                if L2 < 1e-9: continue
                t = ((pt[0]-a[0])*dx+(pt[1]-a[1])*dy)/L2
                if 0.03 < t < 0.97:
                    px, py = a[0]+t*dx, a[1]+t*dy
                    if math.hypot(pt[0]-px, pt[1]-py) <= tol:
                        out[i][k] = (px, py)
    return [(p[0], p[1], q[0], q[1]) for p, q in out]


def flows(segs, circuit):
    """segs: [(kind,(x1,y1,x2,y2))]. 회로(영역)별 빨강/파랑 방향 있는 폴리라인 반환."""
    res = []
    ymid = 300 - CLIP[1]
    sel = [(k, s) for k, s in segs if (((s[1] + s[3]) / 2 < ymid) == (circuit == 'mot'))]
    for kind in ('red', 'blue'):
        S = snap([s for k, s in sel if k == kind])
        if not S:
            continue
        pts = [(s[0], s[1]) for s in S] + [(s[2], s[3]) for s in S]
        if circuit == 'mot':
            entry = (489.7 - CLIP[0], 162.8 - CLIP[1]) if kind == 'red' else (88.9 - CLIP[0], 190.4 - CLIP[1])
            rev = False
        else:
            entry = (47.0 - CLIP[0], 361.4 - CLIP[1]) if kind == 'red' else (43.0 - CLIP[0], 493.6 - CLIP[1])
            rev = (kind == 'blue')                 # 파랑은 LC(-0V) 쪽에서 거슬러 올라가며 방향을 잡은 뒤 뒤집는다
        paths = wiring_anim.oriented(S, range(len(S)), entry, minlen=0.5)
        for p in paths:
            res.append((kind, list(reversed(p)) if rev else p))
    return res


STYLE = ('<style>.fsw-t{font:5px sans-serif;fill:#222}.fsw-h{font:bold 11px sans-serif;fill:#222}'
         '.fsw-flowbase{fill:none;stroke-width:3.4;stroke-opacity:.2;stroke-linejoin:round}'
         '.fsw-flow{fill:none;stroke-width:2.8;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:.1 9;animation:fswflow .9s linear infinite}'
         '.fsw-fb-red,.fsw-fl-red{stroke:#c00000}.fsw-fb-blue,.fsw-fl-blue{stroke:#0070c0}'
         '.fsw-static{fill:none;stroke-width:2.2;stroke-linecap:round;stroke-opacity:.28}.fsw-st-red{stroke:#c00000}.fsw-st-blue{stroke:#0070c0}'
         '@keyframes fswflow{to{stroke-dashoffset:-9.1}}@media (prefers-reduced-motion:reduce){.fsw-flow{animation:none;stroke-dasharray:none}}</style>')


def build(sid):
    slide, circuit, title, desc = STATES[sid]
    page = DOC[slide - 1]
    base = base_paths(page)
    cs = colored(page)
    # 선택한 회로 밖의 색선은 흐리게 정지 상태로만 표시
    other = ''.join('<path class="fsw-static fsw-st-%s" d="M%.1f %.1f L%.1f %.1f"/>' % (k, s[0], s[1], s[2], s[3])
                    for k, s in cs if (((s[1] + s[3]) / 2 < 300 - CLIP[1]) != (circuit == 'mot')))
    fl = flows(cs, circuit)
    def dstr(p): return 'M' + ' L'.join('%.1f %.1f' % q for q in p)
    fg = ''.join(f'<g class="fsw-flowg"><path d="{dstr(p)}" class="fsw-flowbase fsw-fb-{k}"/><path d="{dstr(p)}" class="fsw-flow fsw-fl-{k}"/></g>' for k, p in fl)
    W, H = CLIP[2] - CLIP[0], CLIP[3] - CLIP[1]
    svg = (f'<svg width="{W*2.2:.0f}" height="{H*2.2:.0f}" viewBox="0 0 {W:.0f} {H:.0f}" xmlns="http://www.w3.org/2000/svg">{STYLE}'
           f'<rect width="{W:.0f}" height="{H:.0f}" fill="#fff"/><g id="circuit">{base}</g><g id="other">{other}</g><g id="flow-{circuit}">{fg}</g></svg>')
    return svg, fl


if __name__ == '__main__':
    DOC = pymupdf.open(DECK)
    for sid in STATES:
        svg, fl = build(sid)
        open(os.path.join(OUT, f'FIELD_SW_CKT_{sid}.svg'), 'w', encoding='utf-8').write(svg)
        print(sid, len(svg), 'paths', len(fl), collections.Counter(k for k, _ in fl))
