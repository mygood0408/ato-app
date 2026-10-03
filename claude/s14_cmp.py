"""SICAS HW Design 전 역: DEWEMO 선로전환기 쪽의 선 배치를 SIN1 기준(쌍동 p64 / 단동 p40)과 기하로 비교하고, 같은 위치의 랙·O.T. 번호를 뽑는다."""
import os, re, sys, json, pymupdf
sys.stdout.reconfigure(encoding='utf-8')
BASE = r'C:\Users\김영추\Desktop\2호선 PDF 자료'
SCAN = json.load(open('claude/_scan.json', encoding='utf-8'))


def pdf(stn):
    return pymupdf.open(os.path.join(BASE, 'SICAS HW Design White_%s.pdf' % stn))


def origin(page):
    ws = page.get_text('words')
    c = [w for w in ws if w[4] == 'X3' and w[1] > 250]
    if not c:
        c = [w for w in ws if w[4] == 'X3']
    w = sorted(c, key=lambda w: w[1])[-1]
    return w[0], w[1], ws


def sig(page, ox, oy, ymax_rel=108):
    """원점 기준 선분 집합(0.5pt 반올림) — 플러그 줄부터 O.T. 줄 근처까지의 세로 범위"""
    S = set()
    for d in page.get_drawings():
        if d.get('dashes') and d['dashes'] != '[] 0':
            continue
        for it in d['items']:
            if it[0] != 'l':
                continue
            a, b = it[1], it[2]
            x1, y1, x2, y2 = a.x - ox, a.y - oy, b.x - ox, b.y - oy
            if y1 > y2 or (y1 == y2 and x1 > x2):
                x1, y1, x2, y2 = x2, y2, x1, y1
            if y1 < 3 or y2 > ymax_rel:
                continue
            S.add((round(x1 * 2), round(y1 * 2), round(x2 * 2), round(y2 * 2)))
    return S


def jac(a, b):
    return len(a & b) / max(1, len(a | b))


def labels(ws, ox, oy):
    """원점 기준 숫자 단어: XL 줄(oy+95~140), O.T. 줄(oy+190~215), 현장 줄(oy+280~)"""
    out = []
    for w in ws:
        t = w[4]
        if re.fullmatch(r'\d{1,3}|C|D|N4|R3', t):
            out.append((round(w[0] - ox), round(w[1] - oy), t))
    return out


if __name__ == '__main__':
    refs = {'D': (pdf('SIN1'), 63), 'S': (pdf('SIN1'), 39)}
    R = {}
    for k, (d, i) in refs.items():
        ox, oy, ws = origin(d[i])
        R[k] = (sig(d[i], ox, oy), ox, oy)
    res = {}
    for stn, pages in SCAN.items():
        if not pages:
            continue
        d = pdf(stn)
        for pg, names, kind in pages:
            p = d[pg - 1]
            try:
                ox, oy, ws = origin(p)
            except Exception as e:
                print(stn, pg, 'origin?', e); continue
            s = sig(p, ox, oy)
            jd, js = jac(s, R['D'][0]), jac(s, R['S'][0])
            print('%-5s p%-3d %-12s 표기=%s  쌍동기준=%.2f 단동기준=%.2f  원점=(%.0f,%.0f)' % (stn, pg, names[0] if names else '', kind, jd, js, ox, oy))
            res.setdefault(stn, []).append([pg, names[0] if names else '', kind, round(jd, 2), round(js, 2)])
    json.dump(res, open('claude/_cmp.json', 'w', encoding='utf-8'), ensure_ascii=False)
