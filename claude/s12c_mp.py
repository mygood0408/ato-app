# S12 추가: 사용자 확인으로 OT 송신·수신·신호기 램프·접속상자 verify 해소. JSON·HTML(MPOINTS) 동시 갱신.
import json, re
MPJ = 'measure-points.json'; H = '장비구성뷰_v3_시안.html'
m = json.load(open(MPJ, encoding='utf-8'))
P = {p['id']: p for p in m['points']}
D = '2026-10-03(S12): '
GA = 'G=정진로(평상시), A=역진로. 진로가 바뀌면 송신과 수신이 반대가 되므로 표의 G/A 두 값은 각각 송신·수신 기준으로 판정(송신표의 A 값은 수신 범위, 수신표의 A 값은 송신 범위).'

p = P['MP_OT_FTGS_TX']; assert p.pop('verify')
p['thresholds'][0]['max'] = 60
p['note'] = D + '신도림 OT랙 O51 단자결선도 사진(송신 88개, 21.5~59.9V)과 사용자 결정으로 OT반 송신 11/14번 정상범위를 30~60V로 확정(현장 기준 30~50V와 별도). ' + GA + ' 203B 회로는 송신 21.5V·수신(역진로) 19.7V로 원래 낮은 값이므로 예외로 정상 처리.'
p['exceptions'] = [{'circuit': '203B', 'note': '30V 미만(약 20V)이 정상'}]

p = P['MP_OT_FTGS_RX']; assert p.pop('verify')
p['note'] = D + '신도림 OT랙 O52 단자결선도 사진(수신 91개, 0.38~6.71V)과 비교. ' + GA + ' 센터패드형 궤도는 6V를 넘는 값이 관측됨(090TR 1/2 3.70·4.20V, L440TR 1/2 6.25·6.28V, R430TR2 6.71V) — 센터패드형은 3V 초과 가능, 상한 미정.'
p['centerPadNote'] = '센터패드형 궤도는 수신전압이 6V를 넘을 수 있음(관측 최대 6.71V), 상한 미정'

p = P['MP_OT_SIG_LAMP']; assert p.pop('verify')
p['acdc'] = 'AC'
p['thresholds'] = [{'label': '공칭 AC110V ±5%', 'min': 104.5, 'max': 115.5, 'unit': 'V'}]
p['note'] = D + '사용자 결정: 정상범위 공칭 110V의 ±5%(104.5~115.5V).'

p = P['MP_FTGS_TRACK_CB']; assert p.pop('verify')
p['position']['desc'] = '현장 궤도 접속상자(C/B) 내부. 터널 측벽 또는 선로 내외선 중앙에 설치(현장 상태에 따라 다름). 1개 접속상자에 인접 궤도회로 2개 설비. 상자 외부 라벨 예: 430TF / 450TR (15.5kHz / 11.5kHz)'
p['checkItems'] += [
    '단방향·혼합형·센터패드형: 인터페이스 모듈 1,2번 단자 = 좌측 튜닝유니트 궤도, 3,4번 단자 = 우측 튜닝유니트 궤도. 혼합형은 좌측 튜닝유니트가 단방향 궤도에 해당하면 1,2번, 반대면 3,4번. 센터패드형에서 튜닝유니트가 1개만 설치된 곳은 좌측이면 1,2번, 우측이면 3,4번만 사용',
    '양방향: 전환모듈 단자는 1,2번뿐(전환모듈 특성상 1,2번이 송신일 수도 수신일 수도 있음)',
    '측정 단자: 11/14번, 9/10번(정상범위는 MP_FTGS_TX_FIELD·MP_FTGS_RX_FIELD 기준)']
p['source']['doc'] += ' + 현장 접속상자 사진(시설물 사진모음/궤도회로/CB박스) + 사용자(현장) 확인 2026-10-03'
p['note'] = p['note'].replace('2026-10-03(S12): SIN1 H/W Design 확인 결과 도면 없음 — SIN1 H/W Design에 FTGS 궤도 접속상자(C/B) 도면 없음(ATP p.13·129·136은 Sync-Loop 트랙박스).', D + 'H/W Design에는 도면이 없어 현장 사진·사용자 확인으로 확정(ATP p.13·129·136의 SL Track box는 ATO LOOP C/B BOX로 별개). 현장 사진: 내부 단자대 1~20번, 11번 파랑·14번 빨강·15번 회색·18번 노랑.')

MSG = '2026-10-03(S12): OT 송신(30~60V)·수신(센터패드 노트)·신호기 램프(110V±5%)·FTGS 접속상자 verify 해소. verify:true 0개.'
if MSG not in m['changelog']: m['changelog'].append(MSG)
open(MPJ, 'w', encoding='utf-8', newline='\r\n').write(json.dumps(m, ensure_ascii=False, indent=2))
h = open(H, encoding='utf-8').read()
h, k = re.subn(r'^var MPOINTS = \{\n.*?^\};\n', lambda _: 'var MPOINTS = ' + json.dumps(m, ensure_ascii=False, indent=2) + ';\n', h, count=1, flags=re.S | re.M)
assert k == 1
open(H, 'w', encoding='utf-8', newline='\r\n').write(h)
print('verify left', [p['id'] for p in m['points'] if p.get('verify')])
