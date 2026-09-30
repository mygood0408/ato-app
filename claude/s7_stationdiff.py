# S7: board-info.json 보드에 stationDiff.SIN2 추가 + HTML BOARDINFO_RAW 동기화 (재실행해도 결과 동일)
import json, re
J = 'board-info.json'; H = '장비구성뷰_v3_시안.html'
b = json.load(open(J, encoding='utf-8'))
S = 'SICAS_HW_Design_SIN2'
olm = {'summary': 'SIN2 S52 캐비닛 OLM 4개 (SIN1 S51 캐비닛은 6개)', 'doc': S, 'pages': [104], 'confirmed': False,
 'items': ['OLM 4개(A1·A2·A5·A6) 모두 P12형. SIN1의 G12-1300형(모노모드 광섬유) 2개는 없음',
           '연결 대상: SIN2 ATP +L52, SIN1 SICAS +S51_BUMA0·BUMA2, S&D mobile. SIN1 도면의 HON·YAN·SNU1·IF-C 연결 표기는 SIN2에 없음',
           '케이블: 플라스틱 광섬유 V25132-Z2811-A20·Z1803-A10, RS485 구리선 V25132-M971-A1 (SIN1은 모노모드 E10/125·M973-A1도 사용)',
           '전원: -X14 +24V/0V (SIN1과 동일)']}
ups = {'summary': 'SIN2는 SICAS 캐비닛 S52에 UPS 캐비닛 P51의 60V/24V/230V가 들어옴 (SIN1은 EC/DSTT 캐비닛 T52)', 'doc': S, 'pages': [107], 'confirmed': False,
 'items': ['60V DC (채널 A/B/C용): 단자 1~38, 인입 2×6㎟ 2계통(−/+), UPS까지 최대 20m',
           '24V DC (주변장치용): 단자 40~59, 퓨즈 4A(40~43)·1A(44~46)·6.3A(47~49), 인입 24V DC Indoor(접지) 2×6㎟ 2계통',
           '230V AC (팬용): L/N 단자 66~73 → 팬1·팬2, 팬 고장 신호(단자 76~81, V25132-Z18-A30·2×1.5㎟) → ID캐비닛 D51',
           'SIN1 T52 도면(p.106)의 STEKOP 8V·PSM-K91·24V ORD 공급 조건은 SIN2 p.107에 없음']}
loop = {'summary': 'ATO loop 캐비닛 표기가 SIN1은 신도림(ATP +L51), SIN2는 신대방(ATP +L52)', 'doc': 'ATP_HW_Design_SIN2', 'pages': [6], 'confirmed': False,
 'items': ['SIN1 p.7 "ATO loops Cabinet Sindorim" ↔ SIN2 p.6 "ATO loops Cabinet Sindaebang" (둘 다 Sync-Loop interface 도면)',
           '연결 회로명: SIN1 L52.001·L52.002·F59.001 계열 ↔ SIN2 L51.001·F58.001 계열 (텍스트 발췌 기준)',
           '도면 텍스트만 비교, 이미지 미확인']}
D = {'SICAS_OLM': olm, 'ECDSTT_OLM': olm, 'UPS_ATS_AVR_UNIT': ups, 'UPS_RECTIFIER_UNIT': ups, 'UPS_OUTPUT_DISTRIBUTION': ups, 'ATOLOOP_CB': loop}
n = 0
for g in b['boards'].values():
    for x in g:
        if x['id'] in D: x['stationDiff'] = {'SIN2': D[x['id']]}; n += 1
MSG = '2026-09-30(S7): 6개 보드(OLM 2·UPS 3·ATOLOOP_CB)에 stationDiff.SIN2 추가 — SIN2 도면 대조 결과, 확인필요 유지.'
if MSG not in b['changelog']: b['changelog'].append(MSG)
open(J, 'w', encoding='utf-8', newline='\r\n').write(json.dumps(b, ensure_ascii=False, indent=2))
h = open(H, encoding='utf-8').read()
h2, k = re.subn(r'^var BOARDINFO_RAW = \{\n.*?^\};\n', lambda m: 'var BOARDINFO_RAW = ' + json.dumps(b, ensure_ascii=False, indent=2) + ';\n', h, count=1, flags=re.S | re.M)
assert k == 1
open(H, 'w', encoding='utf-8', newline='\r\n').write(h2)
print('boards', n)
