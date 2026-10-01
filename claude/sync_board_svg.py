"""board_svg/<ID>.svg -> HTML var BOARD_SVG 항목 교체/추가. 실행: python claude/sync_board_svg.py"""
import re, json, glob, os
H = '장비구성뷰_v3_시안.html'
t = open(H, 'rb').read().decode('utf-8')
m = re.search(r'^(var BOARD_SVG = \{\r\n)(.*?)(^\};\r\n)', t, re.M | re.S)
lines = [l for l in m.group(2).split('\r\n') if l]
ents = {re.match(r' "([^"]+)": ', l).group(1): l.rstrip(',') for l in lines}
for f in sorted(glob.glob('board_svg/*.svg')):
    bid = os.path.basename(f)[:-4]
    svg = ' '.join(open(f, encoding='utf-8').read().split())  # 한 줄로
    new = ' ' + json.dumps(bid) + ': ' + json.dumps(svg, ensure_ascii=False)
    print(('교체 ' if bid in ents else '추가 ') + bid, len(svg))
    ents[bid] = new
body = ',\r\n'.join(ents.values()) + '\r\n'
t = t[:m.start(2)] + body + t[m.end(2):]
open(H, 'wb').write(t.encode('utf-8'))
