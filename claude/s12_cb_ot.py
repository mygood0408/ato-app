# S12: C/B박스 보드 SVG 4종에 "기계실 OT반" 연결선(쓰는 단자만) 추가. board_svg/FTGS_CB_*.svg 생성 -> sync_board_svg.py 로 HTML 반영.
import re, json, os
H = '장비구성뷰_v3_시안.html'
h = open(H, encoding='utf-8').read()
PUR = '#6a3fb0'
# id: (OT 선 x들, 단자번호, 시작 y, 모듈 하단 y, 범례 첫 y, 범례 이동량, 코멘트)
CFG = {
 'FTGS_CB_UNI': ([(262, 294, 326, 358)], ['1', '2', '3', '4'], [532.45], 550.0, 568, 40, None),
 'FTGS_CB_BI': ([(64.5, 77.5), (354.5, 367.5)], ['1', '2', '1', '2'], [513, 513], 525.0, 568, 20, None),
 'FTGS_CB_MIXED': ([(152.0, 167.3), (367.3, 378.8)], ['1', '2', '1', '2'], [517, 518], 530.0, 555, 40,
                   ['※ 단방향 궤도가 좌측에 있는 경우를 표현함. 단방향 궤도가 우측이면 인터페이스 3·4번을 사용']),
 'FTGS_CB_CENTERPAD': ([(336, 368)], ['3', '4'], [563.1], 580.0, 590, 50,
                       ['※ 튜닝유니트가 우측에 설치된 경우를 표현함.', '   좌측 설치면 인터페이스 1·2번, 튜닝유니트가 2개면 1~4번을 사용']),
}
os.makedirs('board_svg', exist_ok=True)
for bid, (groups, nums, ybs, mb, leg0, D, cm) in CFG.items():
    m = re.search(r'^ "' + bid + r'": (".*"),?\r?$', h, re.M)
    s = json.loads(m.group(1)); assert 'ot-lines' not in s
    extra = 14 * len(cm) + 8 if cm else 0
    Ht = 640 + D + extra
    s = s.replace('width="640" height="640" viewBox="0 0 640 640"', 'width="640" height="%d" viewBox="0 0 640 %d"' % (Ht, Ht), 1)
    s = s.replace('<rect x="20" y="20" width="600" height="600"', '<rect x="20" y="20" width="600" height="%d"' % (600 + D + extra), 1)
    def shl(mm):
        y1, y2 = float(mm.group(2)), float(mm.group(4))
        if y1 == y2 and y1 >= leg0 - 1: return '<line x1="%s" y1="%g" x2="%s" y2="%g"' % (mm.group(1), y1 + D, mm.group(3), y2 + D)
        return mm.group(0)
    s = re.sub(r'<line x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"', shl, s)
    ymax = [0]
    def sht(mm):
        y = float(mm.group(2))
        if y >= leg0 - 1 and 'font-size="9.5"' in mm.group(0):
            ymax[0] = max(ymax[0], y + D); return mm.group(0).replace('y="%s"' % mm.group(2), 'y="%g"' % (y + D), 1)
        return mm.group(0)
    s = re.sub(r'<text x="([\d.]+)" y="([\d.]+)"[^>]*>', sht, s)
    yend = mb + 22; g = ['<g id="ot-lines">']; k = 0
    for xs, yb in zip(groups, ybs):
        for x in xs:
            g.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="2.4" stroke-dasharray="5 3"/>' % (x, yb, x, yend, PUR))
            g.append('<text x="%g" y="%g" text-anchor="middle" font-size="10" font-weight="700" fill="%s">%s</text>' % (x, yend + 11, PUR, nums[k])); k += 1
        g.append('<text x="%g" y="%g" text-anchor="middle" font-size="11" font-weight="700" fill="%s">기계실 OT반</text>' % (sum(xs) / len(xs), yend + 26, PUR))
    for i, c in enumerate(cm or []):
        g.append('<text x="40" y="%g" font-size="9.5" fill="#555" xml:space="preserve">%s</text>' % (ymax[0] + 16 + 12 * i, c))
    g.append('</g>')
    s = s.replace('</svg>', ''.join(g) + '</svg>')
    open('board_svg/%s.svg' % bid, 'w', encoding='utf-8').write(s)
    print(bid, 'height', Ht)
