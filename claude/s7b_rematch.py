# S7b: 도면-설비 매칭 정리. 재실행해도 결과 동일.
import json, re, glob
J = 'board-info.json'; H = '장비구성뷰_v3_시안.html'
K = 'C:/Users/김영추/Desktop/2호선 PDF 자료/PDF_Knowledge_Base/01_pages/'
b = json.load(open(J, encoding='utf-8'))
B = {x['id']: x for g in b['boards'].values() for x in g}
# 1) ATOLOOP_CB: SICAS SIN2 항목은 FTGS 궤도회로 쪽(키워드 오매칭) → 삭제
rd = B['ATOLOOP_CB']['relatedDrawings']; rd['SIN2'] = [r for r in rd['SIN2'] if r['doc'] != 'SICAS_HW_Design_SIN2']
# 2) UPS_ATS_AVR_UNIT: ATP 항목은 ATO loop·LA-button 쪽 → 삭제(ATO loop 보드에 이미 있음, p.13은 IFC_EMS_RELAY)
rd = B['UPS_ATS_AVR_UNIT']['relatedDrawings']
for s in ('SIN1', 'SIN2'): rd[s] = [r for r in rd.get(s, []) if not r['doc'].startswith('ATP')]
# 3) FTGS 송신/수신 접속 도면 → TX / RX1 / RX2 보드 (도면 제목 기준, 확인필요 유지)
K3 = {'FTGS_TX_PCB': 'transmitter conn', 'FTGS_RX1_PCB': 'receiver 1 conn', 'FTGS_RX2_PCB': 'receiver 2 conn'}
for s in ('SIN1', 'SIN2'):
    d = 'SICAS_HW_Design_' + s; pg = {k: [] for k in K3}
    for f in sorted(glob.glob(K + d + '/page_*.md')):
        t = re.sub(r'\s+', ' ', open(f, encoding='utf-8').read())
        m = re.search(r'FTGS track circuit FTGS-cab\.: F\d+ (transmitter conn|receiver 1 conn|receiver 2 conn)', t)
        if m:
            for k, v in K3.items():
                if v == m.group(1): pg[k].append(int(f[-7:-3]))
    for k, p in pg.items():
        rd = B[k].setdefault('relatedDrawings', {}); rd[s] = [r for r in rd.get(s, []) if r['doc'] != d or 'note' not in r or '도면 제목 기준' not in r['note']]
        if p: rd[s].append({'doc': d, 'pages': p, 'totalPagesFound': len(p), 'note': '도면 제목 기준(FTGS 궤도회로 접속도)'})
    print(s, {k: len(v) for k, v in pg.items()})
MSG = '2026-09-30(S7): 도면-설비 매칭 정리 — ATOLOOP_CB SICAS·UPS_ATS_AVR_UNIT ATP 오매칭 항목 삭제, FTGS TX/RX1/RX2 보드에 궤도회로 접속도(SIN1·SIN2) 추가.'
if MSG not in b['changelog']: b['changelog'].append(MSG)
open(J, 'w', encoding='utf-8', newline='\r\n').write(json.dumps(b, ensure_ascii=False, indent=2))
h = open(H, encoding='utf-8').read()
h2, k = re.subn(r'^var BOARDINFO_RAW = \{\n.*?^\};\n', lambda m: 'var BOARDINFO_RAW = ' + json.dumps(b, ensure_ascii=False, indent=2) + ';\n', h, count=1, flags=re.S | re.M)
assert k == 1
open(H, 'w', encoding='utf-8', newline='\r\n').write(h2)
