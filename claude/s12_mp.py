# S12: SIN1 H/W Design 도면으로 신규 측정지점 14건 위치 확정(verify 제거), 4건 유지. JSON·HTML(MPOINTS) 동시 갱신.
import json, re, glob
MPJ = 'measure-points.json'; H = '장비구성뷰_v3_시안.html'
K = 'C:/Users/김영추/Desktop/2호선 PDF 자료/PDF_Knowledge_Base/01_pages/SICAS_HW_Design_SIN1/page_%04d.md'
DOC = 'SICAS HW Design White_SIN1.pdf'
OLD_TAIL = '2026-09-30 신규(S8): 정기점검 주기·실측 위치는 자료에 없어 미확정.'
NEW_TAIL = '2026-10-03(S12): 신도림(SIN1) 도면으로 랙 위치 확정. 정기점검 주기는 자료에 없어 미확정.'
G = ('T51 p.206 / T52 p.230', 'G')
# id -> (cabinet, level, pages, 한 줄 설명)
CONF = {
 'MP_ECD_24V_FEED': ('T51·T52', 'G', 'p.206(T51), p.230(T52)', '레벨 G: +24V1/+24V2 STEKOP 공급, 10A 과전압 보호 모듈, 6.3A·4A 퓨즈'),
 'MP_ECD_LEVEL_M_24V': ('T51·T52', 'M', 'p.207(T51), p.231(T52)', '레벨 M: Z5 Line Load Filter 16A, 2A×2 분배, OLM P12'),
 'MP_ECD_SV2602_IN': ('T52', 'A', 'p.224(T52); 8V 분배 p.206', 'SIN1은 T52에만 SV 2602-BG 60/8V 5개 프레임(랙 S25790-C18-A1). T51은 T52에서 8V 분배'),
 'MP_ECD_SV2602_OUT': ('T52', 'A', 'p.224(T52); 8V 분배 p.206', 'SIN1은 T52에만 SV 2602-BG 60/8V 5개 프레임(랙 S25790-C18-A1). T51은 T52에서 8V 분배'),
 'MP_ECD_STEKOP_LED': ('T51·T52', 'B', 'p.201, 209~216(T51), p.233~240(T52)', 'STEKOP 8장(슬롯 11·31·51·71·91·111·131·151), 레벨 B 네트워크 14'),
 'MP_ECD_STEKOP_24V': ('T51·T52', 'B', 'p.201, 209~216(T51), p.233~240(T52)', 'STEKOP 8장(슬롯 11·31·51·71·91·111·131·151), 레벨 B 네트워크 14'),
 'MP_ECD_DEWEMO_24V': ('T51·T52', '-', 'p.199, 203~205(T51), p.227~229(T52)', 'DEWEMO·DESIMO 전면도 및 플러그 배선(포인트 P202 등, 슬롯 11·31·51…)'),
 'MP_ECD_DEWEMO_LED': ('T51·T52', '-', 'p.199, 203~205(T51), p.227~229(T52)', 'DEWEMO·DESIMO 전면도 및 플러그 배선(포인트 P202 등, 슬롯 11·31·51…)'),
 'MP_ECD_DEWEMO_MOTOR110': ('T51·T52', '-', 'p.199, 203~205(T51), p.227~229(T52)', 'DEWEMO·DESIMO 전면도 및 플러그 배선(포인트 P202 등, 슬롯 11·31·51…)'),
 'MP_ECD_DESIMO': ('T51·T52', '-', 'p.199, 203~205(T51), p.227~229(T52)', 'DEWEMO·DESIMO 전면도 및 플러그 배선(신호기 S02 등, 슬롯 11·31·51…)'),
 'MP_ECD_OLM_LED': ('T51·T52', 'M', 'p.207(T51), p.231(T52)', '레벨 M: OLM P12 2개'),
 'MP_SICAS_OLM_LED': ('S51', 'M·N', 'p.187, p.14', 'OLM P12 / G12-1300, PROFIBUS CH1~CH3'),
 'MP_SICAS_SVK2102_5V': ('S51', 'L', 'p.193', 'SVK 2102-BG 60V/5V 3개(S25790-B116-D1)'),
 'MP_SICAS_VENUS3_LED': ('S51', 'A·B·D·F', 'p.189~192, 187', '채널별 VENUS3 모듈(프로세서 랙)'),
}
KEEP = {  # SIN1 H/W Design에서 못 찾은 이유
 'MP_TWC_IMU100_LED': 'SIN1 SICAS·ATP H/W Design에 IMU-100 표기 없음(TWC 쪽은 루프 배선 ATP p.20~23뿐)',
 'MP_FTGS_PS_12V': 'SIN1 H/W Design에 FTGS 전원공급장치(V25913-Z150-C1) 표기 없음(ATP p.101은 Sync-Loop 캐비닛 전원)',
 'MP_FTGS_PS_5V': '위와 동일',
 'MP_FTGS_TRACK_CB': 'SIN1 H/W Design에 FTGS 궤도 접속상자(C/B) 도면 없음(ATP p.13·129·136은 Sync-Loop 트랙박스)',
}
# 도면 쪽 존재 검증(스크립트로)
def has(p, pat): return re.search(pat, open(K % p, encoding='utf-8').read())
assert has(206, 'STEKOP') and has(207, 'OLM P12') and has(224, 'SV 2602') and has(193, 'SVK 2102')
assert has(231, 'OLM P12') and has(230, 'STEKOP') and has(201, 'Level B') and has(189, 'VENUS3')
assert has(199, 'DEWEMO') and all(has(p, 'DEWEMO') for p in (203, 204, 205, 227, 228, 229))
assert all(has(p, 'STEKOP') for p in list(range(209, 217)) + list(range(233, 241)))
assert has(187, 'OLM') and has(14, 'OLM')

m = json.load(open(MPJ, encoding='utf-8'))
n = 0
for p in m['points']:
    if p['id'] in CONF:
        cab, lv, pg, txt = CONF[p['id']]
        pos = p['position']
        pos['desc'] = pos['desc'].replace(' 슬롯·단자 번호는 역별 EC/DSTT H/W Design으로 확인', '').replace('EC/DSTT 랙(기계실 T51/T52).', 'EC/DSTT 랙.').strip()
        pos['sin1'] = {'cabinet': cab, 'level': lv, 'drawing': DOC, 'pages': pg, 'summary': txt}
        assert p['note'].endswith(OLD_TAIL)
        p['note'] = p['note'][:-len(OLD_TAIL)] + NEW_TAIL
        p.pop('verify'); n += 1
    elif p['id'] in KEEP:
        assert p.get('verify')
        p['note'] = p['note'].replace(OLD_TAIL, '2026-10-03(S12): SIN1 H/W Design 확인 결과 도면 없음 — ' + KEEP[p['id']] + '. 정기점검 주기 미확정.')
assert n == 14
MSG = '2026-10-03(S12): 신규 측정지점 18개 중 14개 SIN1 SICAS H/W Design 도면으로 위치 확정(verify 제거, position.sin1 추가), 4개(TWC IMU100·FTGS 전원 12V/5V·궤도 접속상자)는 도면 없어 verify 유지.'
if MSG not in m['changelog']: m['changelog'].append(MSG)
open(MPJ, 'w', encoding='utf-8', newline='\r\n').write(json.dumps(m, ensure_ascii=False, indent=2))
h = open(H, encoding='utf-8').read()
h, k = re.subn(r'^var MPOINTS = \{\n.*?^\};\n', lambda _: 'var MPOINTS = ' + json.dumps(m, ensure_ascii=False, indent=2) + ';\n', h, count=1, flags=re.S | re.M)
assert k == 1
open(H, 'w', encoding='utf-8', newline='\r\n').write(h)
print('confirmed', n, 'kept', len(KEEP), 'verify left', sum(1 for p in m['points'] if p.get('verify')))
