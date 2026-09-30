# S8: EC/DSTT 측정지점 11개 추가 + 고장사례 measurePointRef 배열화·연결. JSON·HTML 동기화. 재실행해도 결과 동일.
import json, re
MPJ = 'measure-points.json'; FCJ = 'fault-cases.json'; H = '장비구성뷰_v3_시안.html'
DOC = 'SICAS 유지보수 매뉴얼(SICAS_유지보수_매뉴얼)'
POS = 'EC/DSTT 랙(기계실 T51/T52). 슬롯·단자 번호는 역별 EC/DSTT H/W Design으로 확인'
DMM = 'Digital Multimeter'
V24 = {'min': 21.6, 'max': 31.2, 'unit': 'V', 'nominal': 24}


def mp(id, title, t, acdc=None, rng=None, pos=None, method=None, pages=None, board=None, faults=(), note=None,
       led=None, check=None, caution=None, instr=None):
    d = {'id': id, 'facility': 'EC/DSTT'}
    if acdc: d['acdc'] = acdc
    d.update({'title': title, 'measureType': t, 'cycle': '미상', 'position': {'desc': pos or POS}})
    if rng: d['range'] = rng
    if instr: d['instrument'] = instr
    if method: d['method'] = method
    if check: d['checkItems'] = check
    if led: d['ledCheck'] = led
    if caution: d['caution'] = caution
    d['source'] = {'doc': DOC, 'page': pages}
    if board: d['boardRef'] = board
    if faults: d['relatedFaults'] = list(faults)
    d['note'] = (note + ' ' if note else '') + '2026-09-30 신규(S8): 정기점검 주기·실측 위치는 자료에 없어 미확정.'
    d['verify'] = True
    return d


NEW = [
    mp('MP_ECD_24V_FEED', 'EC/DSTT 캐비닛 24V 전원 (분전반 인입)', 'voltage', 'DC', V24,
       'EC/DSTT 캐비닛 후면 터미널 스트립 레벨 G(수직, 전원공급장치 프레임 포함). ' + POS,
       ['DMM을 DC로 놓고 터미널 스트립 레벨 G의 24V 인입 단자(+)와 0V 단자(−) 사이 측정', '분전반부터 이 단자까지 24V 및 라인 점검'],
       'p.84, p.107, p.129, p.134', None, ['FLT_ECD_01'],
       '범위는 STEKOP 공급전압 사양(21.6/24/31.2V) 기준. 전원이 없으면 STEKOP LED ASS·RASS 적색, Command·message LED 소등, OLM 전 LED 소등.',
       caution='전원단자 측정 시 주변 단자와 단락 주의', instr=DMM),
    mp('MP_ECD_LEVEL_M_24V', 'EC/DSTT 레벨 M 터미널 24V (DSTT용, -X4)', 'voltage', 'DC', V24,
       'EC/DSTT 캐비닛 후면 레벨 M 터미널 스트립(Line Load Filter 16A, Z5 2A×2 옆). ' + POS,
       ['레벨 M 터미널 스트립에서 "24V DC for the DSTT\'s -X4" 단자 측정', '레벨 G에서 넘어오는 24V(24V DC from level G)와 같은 값이어야 함'],
       'p.108', None, ['FLT_ECD_01'],
       '전압 범위는 DSTT 24V 사양(STEKOP·DEWEMO 21.6~31.2V)을 적용한 값(매뉴얼 도면에는 범위 수치 없음).', instr=DMM),
    mp('MP_ECD_SV2602_IN', 'SV2602 입력전압 (60V)', 'voltage', 'DC', {'min': 42, 'max': 75, 'unit': 'V', 'nominal': 60},
       'EC/DSTT 랙 전원공급장치 프레임 SV2602, 후면 플러그 X1 4번(+)·6번(−). ' + POS,
       ['SV2602 X1 플러그 4번(+)·6번(−) 사이를 DC로 측정', '42V 미만이면 출력 없음. 75V 초과 시 출력 차단·프론트 퓨즈 F2 차단(회복: 42~75V로 조정 후 F2 재투입, 퓨즈 종류 확인)'],
       'p.101~105', 'ECDSTT_PS', ['FLT_PWR_01', 'FLT_SIG_03'],
       'SV2602는 60V→8V 변환 전원장치(STEKOP용). 스위치오프 과전압 ≥89V.',
       led=[{'led': 'UE', 'meaning': '입력전압 가용', 'normal': '점등'}, {'led': 'INH', 'meaning': '외부 스위치 OFF 명령', 'normal': '소등'}],
       caution='SV2602는 전면 스위치가 OFF일 때만 프레임에 삽입·제거(플러그 스파크 방지)', instr=DMM),
    mp('MP_ECD_SV2602_OUT', 'SV2602 출력전압 (8V)', 'voltage', 'DC', {'min': 7.5, 'max': 9, 'unit': 'V', 'nominal': 8},
       'SV2602 후면 플러그 X1 20·22번(+8V), 28·30번(0V). ' + POS,
       ['SV2602 X1 플러그 20/22번(+8V)과 28/30번(0V) 사이 측정', '6.3V 미만이면 출력 차단, 10V 초과 시 출력 차단·F2 차단'],
       'p.101~105', 'ECDSTT_PS', ['FLT_PWR_01', 'FLT_SIG_03'],
       '출력 전류 최대 14A(120W). 출력측 미전압 원인(과부하)을 제거하고 스위치 OFF→UE 소등 확인→ON.',
       led=[{'led': 'UA', 'meaning': '출력전압 가용', 'normal': '점등'}, {'led': 'UE', 'meaning': '입력전압 가용', 'normal': '점등'}], instr=DMM),
    mp('MP_ECD_STEKOP_LED', 'STEKOP 전면 LED (ASS·RASS·5V·L1~L4)', 'visual', None, None, None, None, 'p.20~22, p.82, p.83',
       'ECDSTT_STEKOP', ['FLT_ECD_02', 'FLT_ECD_05'],
       'STEKOP 컴퓨터 정지 등 오류는 L1~L4를 약 1초 간격으로 순환 표시(오류번호, 진단용). 리셋은 FEMES Reset-key(유지보수 담당자만).',
       led=[{'led': 'ASS(적색)', 'meaning': '안전 스위치 OFF 릴레이 해제 표시', 'normal': '평상시 소등(점등=스위치 OFF 발생)'},
            {'led': 'RASS(적색)', 'meaning': '되돌릴 수 없는(irreversible) 스위치 OFF 발생', 'normal': '평상시 소등'},
            {'led': '5V VK / 5V UK(녹색)', 'meaning': '처리채널/감시채널 공급전압 정상', 'normal': '점등'},
            {'led': 'L1~L4(황색)', 'meaning': '오류 메시지 진단용, 접속 장애는 채널1 L4 깜박임', 'normal': '평상시 오류번호 없음'}],
       check=['STEKOP 전 LED 소등이면 STEKOP 장애: 교체(교체 후 Reset 키)', 'LED ASS·RASS 적색+Command/message LED 소등+OLM 전 소등이면 24V 전원 장애'],
       caution='STEKOP 모듈은 전원 ON 상태로 뺄 수 있음. 이때 스위치를 OFF하면 연동장치 완전 정지 — 전원 스위치 OFF 금지'),
    mp('MP_ECD_STEKOP_24V', 'STEKOP 공급전압 (플러그 X1, 24V)', 'voltage', 'DC', V24,
       'STEKOP 후면 플러그 X1 2번(24V)·32번(0V). ' + POS,
       ['STEKOP 후면 프레임 플러그 X1의 24V 핀과 0V 핀 사이 측정', '24V 전하 레일 1.2A, 0V 전하 레일 0.26A, 무부하 전류 0.03~0.4A'],
       'p.84, p.85', 'ECDSTT_STEKOP', ['FLT_ECD_02'], None, instr=DMM),
    mp('MP_ECD_DEWEMO_24V', 'DEWEMO 24V 전원 (플러그 X1)', 'voltage', 'DC', V24,
       'DEWEMO-W 전면 플러그 X1(24V 전원), 핀레일 X1-1(0V)·X1-2(+24V). ' + POS,
       ['DEWEMO X1 핀레일 X1-2(+24V)와 X1-1(0V) 사이 DC 측정', '공급전류 약 100mA'],
       'p.95, p.97, p.99', 'ECDSTT_DEWEMO', ['FLT_ECD_04'], None, instr=DMM),
    mp('MP_ECD_DEWEMO_LED', 'DEWEMO LED (방향명령·선로전환기 표시)', 'visual', None, None, None, None, 'p.95, p.96',
       'ECDSTT_DEWEMO', ['FLT_ECD_03', 'FLT_ECD_05'],
       '명령 LED(녹색)·메시지 LED(황색). 출력 후 메시지는 약 300ms 뒤에 읽는다.',
       led=[{'led': '검지기1+ · 검지기2−', 'meaning': '우측 선로전환기 정상 표시', 'normal': '두 LED 점등'},
            {'led': '검지기1− · 검지기2+', 'meaning': '좌측 선로전환기 정상 표시', 'normal': '두 LED 점등'},
            {'led': '검지기1+ · 검지기2+', 'meaning': '선로전환기 드라이브에 크랭크 삽입', 'normal': '크랭크 삽입 중에만'},
            {'led': '전부 소등', 'meaning': '전환 중이면 정상, 끝 위치 도달 후에는 오류', 'normal': '전환 중에만'}],
       check=['표에 없는 조합은 오류(선로 접지·누전·방해)', '방향 명령 LED와 선로전환기 표시 LED가 일치하지 않으면 FLT_ECD_03~05·08·09 참고']),
    mp('MP_ECD_DEWEMO_MOTOR110', 'DEWEMO 모터전원 입력 (X2-6, AC 110V)', 'voltage', 'AC', {'min': 100, 'max': 120, 'unit': 'V', 'nominal': 110},
       'DEWEMO-W 핀레일 X2-6(110V AC 입력). 랙 쪽 측정 — 현장 쪽은 MP_FIELD_SW_MOTOR. ' + POS,
       ['선로전환기 전환 명령 순간에 X2-6 핀에서 AC 110V 확인', '평상시(정지)는 0V가 정상, 전환 중에만 인가'],
       'p.99, p.130, p.136, p.139', 'ECDSTT_DEWEMO', ['FLT_ECD_08', 'FLT_ECD_09'],
       '매뉴얼에는 "110V AC"만 명시. 범위 100~120V는 MP_FIELD_SW_MOTOR와 동일하게 적용. 모터 시작전류 최대 4s(10% ED)·끝위치 검지기 0.8A.',
       caution='전환 명령 순간에만 전압이 인가되므로 타이밍에 맞춰 측정', instr=DMM),
    mp('MP_ECD_DESIMO', 'DESIMO 24V 공급 및 LED (IK1·IK2·S0·S1)', 'voltage', 'DC', {'min': 21.6, 'max': 26.4, 'unit': 'V', 'nominal': 24},
       'DESIMO-WEZ 전면 플러그 4번(+24V)/8번(−24V) 및 전면 LED. ' + POS,
       ['DESIMO 전면 플러그 24V 공급단자 사이 DC 측정(21.6~26.4V)', '전면 LED IK1·IK2로 램프 전류 정상 여부 확인'],
       'p.92, p.93, p.130, p.142', 'ECDSTT_DESIMO', ['FLT_ECD_06', 'FLT_ECD_07', 'FLT_SIG_08'],
       '점등 시 램프전류 제한 26mA(24.7~27.3mA), 공급전류 20~25mA. 전면 플러그 번호는 p.93 표 기준.',
       led=[{'led': 'S0 / S1', 'meaning': '채널 0/1 제어라인 활성', 'normal': '해당 신호 현시 시 점등'},
            {'led': 'IK1 / IK2', 'meaning': '채널 1/2 램프전류 정상(Current OK)', 'normal': '신호기 점등 시 점등'}],
       check=['IK1·IK2 소등: 24V 없음 → DESIMO 플러그 연결 점검', 'IK1·IK2 소등+24V 정상: 신호기 기준 이하 전류 또는 LED 클러스터 손상 → 신호기 수리'],
       instr=DMM),
    mp('MP_ECD_OLM_LED', 'OLM 전면 LED (EC/DSTT 캐비닛)', 'visual', None, None, None, None, 'p.106, p.112, p.124, p.129, p.131',
       'ECDSTT_OLM', ['FLT_ECD_01'], 'OLM 작동전압은 24V DC. 캐비닛 24V 전원이 없으면 OLM 전 LED 소등.',
       led=[{'led': 'OLM 채널 LED', 'meaning': '데이터 전송 인식', 'normal': '녹색 점등'},
            {'led': 'LED 소등', 'meaning': '전원 없음 또는 광 PROFIBUS 프레임 미수신', 'normal': '-'},
            {'led': 'LED 적색', 'meaning': '송·수신 뒤바뀜, 상대 장비 미접속·전원 OFF·손상, 광케이블 길이 초과·접촉불량', 'normal': '-'},
            {'led': 'LED 황색 깜빡임', 'meaning': '네트워크 버스로 데이터 전송 없음(광접속은 정상)', 'normal': '-'}],
       check=['BUMA↔STEKOP 광접속 장애 시 OLM LED 각 채널 소등, STEKOP 채널1 L4 깜박임(p.131)']),
]
FMAP = {
    'FLT_ECD_01': ['MP_ECD_24V_FEED', 'MP_ECD_LEVEL_M_24V', 'MP_ECD_OLM_LED'],
    'FLT_ECD_02': ['MP_ECD_STEKOP_LED', 'MP_ECD_STEKOP_24V'], 'FLT_ECD_03': ['MP_ECD_DEWEMO_LED'],
    'FLT_ECD_04': ['MP_ECD_DEWEMO_24V', 'MP_ECD_DEWEMO_LED'], 'FLT_ECD_05': ['MP_ECD_STEKOP_LED', 'MP_ECD_DEWEMO_LED'],
    'FLT_ECD_06': ['MP_ECD_DESIMO', 'MP_FIELD_SIG_LAMP'], 'FLT_ECD_07': ['MP_ECD_DESIMO', 'MP_FIELD_SIG_LAMP'],
    'FLT_ECD_08': ['MP_ECD_DEWEMO_MOTOR110', 'MP_FIELD_SW_MOTOR'], 'FLT_ECD_09': ['MP_ECD_DEWEMO_MOTOR110', 'MP_FIELD_SW_MOTOR'],
    # 사용자 확정(2026-09-30): 강한추천 5건
    'FLT_ILK_08': ['MP_SICAS_S51_DC24'], 'FLT_ATO_04': ['MP_ATO_CONTROLLER_LED_TEST'],
    'FLT_PWR_01': ['MP_ECD_SV2602_IN', 'MP_ECD_SV2602_OUT'], 'FLT_SIG_03': ['MP_ECD_SV2602_IN', 'MP_ECD_SV2602_OUT'],
    'FLT_SIG_08': ['MP_ECD_DESIMO']}

# ---- measure-points.json
m = json.load(open(MPJ, encoding='utf-8')); ids = {p['id'] for p in NEW}
m['points'] = [p for p in m['points'] if p['id'] not in ids] + NEW
for p in m['points']:
    if p['id'] == 'MP_SICAS_S51_DC24': p['relatedFaults'] = [f for f in p.get('relatedFaults', []) if f != 'FLT_ECD_01']
    if p['id'] == 'MP_FIELD_SIG_LAMP': p['relatedFaults'] = sorted(set(p['relatedFaults']) | {'FLT_SIG_08'})
    if p['id'] == 'MP_FIELD_SW_MOTOR': p['relatedFaults'] = sorted(set(p['relatedFaults']) | {'FLT_ECD_08', 'FLT_ECD_09'})
MSG = '2026-09-30(S8): EC/DSTT 측정지점 11개 신규(MP_ECD_*, 근거 SICAS 유지보수 매뉴얼) 추가. 측정 탭에 EC/DSTT 분류 신설. 기존 측정지점은 이동하지 않음.'
if MSG not in m['changelog']: m['changelog'].append(MSG)
open(MPJ, 'w', encoding='utf-8', newline='\r\n').write(json.dumps(m, ensure_ascii=False, indent=2))

# ---- fault-cases.json (measurePointRef 전부 배열화)
fc = json.load(open(FCJ, encoding='utf-8'))


def walk(o):
    if isinstance(o, dict):
        if str(o.get('id', '')).startswith('FLT_') and 'symptom' in o: yield o
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)


M = {p['id'] for p in m['points']}; n = 0
for c in walk(fc):
    r = FMAP.get(c['id'], c.get('measurePointRef'))
    if r is None: continue
    r = [r] if isinstance(r, str) else list(r)
    assert all(x in M for x in r), (c['id'], r)
    c['measurePointRef'] = r; n += 1
open(FCJ, 'w', encoding='utf-8', newline='\r\n').write(json.dumps(fc, ensure_ascii=False, indent=2))

# ---- HTML 동기화
h = open(H, encoding='utf-8').read()
for var, d in (('MPOINTS', m), ('FCASES', fc)):
    h, k = re.subn(r'^var ' + var + r' = \{\n.*?^\};\n', lambda _: 'var ' + var + ' = ' + json.dumps(d, ensure_ascii=False, indent=2) + ';\n',
                   h, count=1, flags=re.S | re.M)
    assert k == 1
open(H, 'w', encoding='utf-8', newline='\r\n').write(h)
print('MP', len(m['points']), 'fault refs', n)
