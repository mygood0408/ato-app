"""전 역: 위치(왼→오른쪽) 기준으로 랙(XL) 번호·O.T. 번호·현장 단자 이름을 뽑아 SIN1 과 같은 순서인지 확인하고 표로 저장."""
import os, re, sys, json, pymupdf
sys.path.insert(0, 'claude')
import s14_cmp as c
sys.stdout.reconfigure(encoding='utf-8')
SCAN = json.load(open('claude/_scan.json', encoding='utf-8'))
FIELD = {'13', '14', 'C', 'D', 'N4', '10', '3', '4', 'R3', '8', '1', '2', '5', '6'}


def nums(page):
    ox, oy, ws = c.origin(page)
    rel = [(w[0] - ox, w[1] - oy, w[4]) for w in ws]
    ot = sorted([(x, t) for x, y, t in rel if re.fullmatch(r'0\d\d', t) and 150 < y < 270])
    xl = sorted([(x, t) for x, y, t in rel if re.fullmatch(r'\d{1,2}', t) and 60 < y < 140 and 30 < x < 900
                 and not any(abs(x - px) < 3 for px, _ in [])])
    # 현장 단자 이름: O.T. 번호 아래 첫 줄(점선 아래), 'Point Machine' 위
    fy = [y for x, y, t in rel if t in ('13', '14', 'C', 'D', 'N4') and 270 < y < 420]
    fld = []
    if fy:
        y0 = min(fy)
        fld = sorted([(x, t) for x, y, t in rel if abs(y - y0) < 6 and t in FIELD and x > 30])
    return [t for _, t in xl], [t for _, t in ot], [t for _, t in fld], [round(x) for x, _ in ot]


if __name__ == '__main__':
    out = {}
    ref = {}
    for stn, pages in SCAN.items():
        if not pages:
            continue
        d = c.pdf(stn)
        for pg, names, kind in pages:
            xl, ot, fld, ox = nums(d[pg - 1])
            out.setdefault(stn, []).append({'pg': pg, 'name': names[0] if names else '', 'kind': kind, 'xl': xl, 'ot': ot, 'field': fld})
    json.dump(out, open('claude/_nums.json', 'w', encoding='utf-8'), ensure_ascii=False)
    R = {'D': next(p for p in out['SIN1'] if p['pg'] == 64), 'S': next(p for p in out['SIN1'] if p['pg'] == 40)}
    print('기준 쌍동 field', R['D']['field'], 'xl', R['D']['xl'], 'ot', R['D']['ot'])
    print('기준 단동 field', R['S']['field'], 'xl', R['S']['xl'], 'ot', R['S']['ot'])
    for stn, ps in out.items():
        for p in ps:
            r = R[p['kind']]
            okf = p['field'] == r['field']
            okn = len(p['xl']) == len(r['xl']) and len(p['ot']) == len(r['ot'])
            print('%-5s p%-3d %-11s %s 현장단자순서=%s 개수=%s xl=%s ot=%s' % (stn, p['pg'], p['name'], p['kind'], 'OK' if okf else 'DIFF ' + str(p['field']), 'OK' if okn else 'DIFF(%d,%d)' % (len(p['xl']), len(p['ot'])), p['xl'], p['ot']))
