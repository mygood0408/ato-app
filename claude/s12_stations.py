# S12: stations.json에 ecdCabinets·ecdRef·mpPages 추가, 측정지점 position을 역 공통 구조(cabinetType·level)+drawingLinks kind STN으로 전환. JSON·HTML 동시 갱신.
import json, re, sys
sys.path.insert(0, 'claude')
from s12_stn_probe import scan
MPJ = 'measure-points.json'; SJ = 'stations.json'; H = '장비구성뷰_v3_시안.html'
REF = {'SIN2': 'SIN1', 'SNU2': 'SNU1', 'SON2': 'SON1'}  # EC/DSTT 도면은 1호 역 도면에 있음
MAP = {'MP_ECD_24V_FEED': 'G', 'MP_ECD_LEVEL_M_24V': 'M', 'MP_ECD_OLM_LED': 'M', 'MP_ECD_SV2602_IN': 'SV', 'MP_ECD_SV2602_OUT': 'SV',
       'MP_ECD_STEKOP_LED': 'STK', 'MP_ECD_STEKOP_24V': 'STK', 'MP_ECD_DEWEMO_24V': 'DEW', 'MP_ECD_DEWEMO_LED': 'DEW',
       'MP_ECD_DEWEMO_MOTOR110': 'DEW', 'MP_ECD_DESIMO': 'DEW', 'MP_SICAS_OLM_LED': 'S_OLM', 'MP_SICAS_SVK2102_5V': 'S_SVK',
       'MP_SICAS_VENUS3_LED': 'S_VEN'}
st = json.load(open(SJ, encoding='utf-8'))
for k, e in st.items():
    r = scan(k)
    r['STK'] = sorted(set(r['STK_FRAME'] + r['STK_ALLOC']))
    e['ecdCabinets'] = r['ECDCABS']
    if k in REF: e['ecdRef'] = REF[k]
    e['mpPages'] = {i: r[g] for i, g in MAP.items() if r[g]}
    print(k, e['ecdCabinets'], e.get('ecdRef', ''), len(e['mpPages']), 'of 14')
json.dump(st, open(SJ, 'w', encoding='utf-8', newline='\r\n'), ensure_ascii=False, indent=1)

m = json.load(open(MPJ, encoding='utf-8'))
n = 0
for p in m['points']:
    s = p.get('position', {}).pop('sin1', None)
    if s and p['id'] in MAP:
        pos = p['position']
        pos['cabinetType'] = 'EC/DSTT' if p['id'].startswith('MP_ECD') else 'SICAS'
        pos['level'] = s['level']
        pos['desc'] += ' [SIN1 기준 %s %s] %s' % (s['cabinet'], s['pages'], s['summary'])
        p['drawingLinks'] = {'kind': 'STN'}
        n += 1
assert n == 14
MSG = '2026-10-03(S12): position.sin1 → 역 공통 구조(cabinetType·level)+drawingLinks kind STN로 전환, 역별 쪽은 stations.json mpPages, EC/DSTT 캐비닛은 ecdCabinets(SIN2·SNU2·SON2는 ecdRef로 1호 역 도면 참조).'
if MSG not in m['changelog']: m['changelog'].append(MSG)
open(MPJ, 'w', encoding='utf-8', newline='\r\n').write(json.dumps(m, ensure_ascii=False, indent=2))

h = open(H, encoding='utf-8').read()
h, k1 = re.subn(r'^var MPOINTS = \{\n.*?^\};\n', lambda _: 'var MPOINTS = ' + json.dumps(m, ensure_ascii=False, indent=2) + ';\n', h, count=1, flags=re.S | re.M)
h, k2 = re.subn(r'^var STATIONS = .*;$', lambda _: 'var STATIONS = ' + json.dumps(st, ensure_ascii=False, separators=(',', ':')) + ';', h, count=1, flags=re.M)
OLD = "    var pg = (L.kind === 'N' ? [(STATIONS[s].paths || {}).N] : (s === 'SIN1' ? L.pages : [])).filter(Boolean);\n"
NEW = ("    var pg = (L.kind === 'N' ? [(STATIONS[s].paths || {}).N] : L.kind === 'STN' ? (STATIONS[s].mpPages || {})[mp.id] || [] : (s === 'SIN1' ? L.pages : [])).filter(Boolean);\n"
       "    if (L.kind === 'STN' && mp.position.cabinetType === 'EC/DSTT') {\n"
       "      var cb = STATIONS[s].ecdCabinets || [];\n"
       "      if (STATIONS[s].ecdRef) { o.push('SICAS HW Design ' + s + ': EC/DSTT 캐비닛은 ' + STATIONS[s].ecdRef + ' 도면 참조'); return; }\n"
       "      if (pg.length) o.push('EC/DSTT 캐비닛 ' + cb.join('·') + (cb.length > 1 ? ' 중 해당 쪽' : '') + (mp.position.level !== '-' ? ' / 레벨 ' + mp.position.level : ''));\n"
       "    }\n")
assert OLD in h
h = h.replace(OLD, NEW)
assert k1 == 1 and k2 == 1
open(H, 'w', encoding='utf-8', newline='\r\n').write(h)
print('done')
