# S12 추가: 사용자 제공 자료로 IMU100·FTGS 전원 2·OT 선로전환기 3·콘덴서 verify 해소. JSON·HTML(MPOINTS) 동시 갱신.
import json, re
MPJ = 'measure-points.json'; H = '장비구성뷰_v3_시안.html'
m = json.load(open(MPJ, encoding='utf-8'))
P = {p['id']: p for p in m['points']}
D = '2026-10-03(S12): '
def done(i, note, desc=None, **kw):
    p = P[i]; assert p.pop('verify'), i
    if desc: p['position']['desc'] = desc
    p.update(kw); p['note'] = (p.get('note', '') + ' ' + note).strip()

p = P['MP_TWC_IMU100_LED']; p['source']['page'] += '; 지침서 p.226, p.228, p.232'
done('MP_TWC_IMU100_LED', D + '신호업무 지침서 p.226·228·232로 위치 확인(기계실 TWC 실내장치 IMU-100 모듈 전면). 역별 소켓 번호는 ATP 도면(신도림은 ATP p.20~23 TWC loops wiring)으로 확인.',
     desc='기계실 TWC 실내장치 IMU-100 모듈(PTI 수신기) 전면 패널. TWC 실외케이블이 연결되는 전면 소켓 번호는 역별 ATP 도면으로 확인')
PS = '기계실 FTGS 랙 후면 상단 PULS 전원공급장치(V25913-Z150-C1, Vout1 12V/14A·Vout2 5V/6A, LED 12V·5V). '
for i in ('MP_FTGS_PS_12V', 'MP_FTGS_PS_5V'):
    done(i, D + '신도림 FTGS 랙 후면 현장사진(현장자료/SIN1_FTGS랙_후면_전체.jpg)에서 전원공급장치 2대 위치·라벨 확인. 측정소켓 위치는 매뉴얼 근거.',
         desc=PS + P[i]['position']['desc'])
for i in ('MP_OT_SW_CONTROL', 'MP_OT_SW_INDICATION', 'MP_OT_SW_MOTOR'):
    done(i, D + '사용자(현장) 확인: 현장 측정전압·정상범위와 동일.')
done('MP_SW_CAPACITOR', D + '사용자(현장) 확인: 선로전환기 기동용 콘덴서, 선로전환기 가장 앞단 원형 함 내부. 기준 쌍동 135·단동 120(µF, 현장사진 Fluke 정전용량 측정 123µF 표시 확인). 값이 낮거나 불량이면 전환 모터 힘이 약해져 전환력 저하. 현장사진: 현장자료/콘덴서.',
     desc='선로전환기 가장 앞단 원형 함 내부 기동용 콘덴서(양 단자 사이 정전용량)',
     thresholds=[{'label': '단동', 'min': 120, 'unit': 'µF'}, {'label': '쌍동', 'min': 135, 'unit': 'µF'}],
     instrument='멀티미터 정전용량 측정(Fluke 87V 등)',
     source={'doc': '사용자(현장) 확인 2026-10-03 + 현장자료/콘덴서 사진'})
MSG = '2026-10-03(S12): verify 해소 7개(IMU100·FTGS 전원 12V/5V·OT 선로전환기 3·콘덴서). 남은 verify는 OT 궤도 송수신·신호기 램프·FTGS 접속상자.'
if MSG not in m['changelog']: m['changelog'].append(MSG)
open(MPJ, 'w', encoding='utf-8', newline='\r\n').write(json.dumps(m, ensure_ascii=False, indent=2))
h = open(H, encoding='utf-8').read()
h, k = re.subn(r'^var MPOINTS = \{\n.*?^\};\n', lambda _: 'var MPOINTS = ' + json.dumps(m, ensure_ascii=False, indent=2) + ';\n', h, count=1, flags=re.S | re.M)
assert k == 1
open(H, 'w', encoding='utf-8', newline='\r\n').write(h)
print('verify left', [p['id'] for p in m['points'] if p.get('verify')])
