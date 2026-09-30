# S8: SICAS 측정지점 3개 추가(OLM LED·SVK2102 5V·VENUS3 LED) + STEKOP/연동장치 고장사례 8건 연결. JSON·HTML 동기화. 재실행 가능.
import json, re
MPJ = 'measure-points.json'; FCJ = 'fault-cases.json'; H = '장비구성뷰_v3_시안.html'
DOC = 'SICAS 유지보수 매뉴얼(SICAS_유지보수_매뉴얼)'
NOTE_TAIL = '2026-09-30 신규(S8): 정기점검 주기·실측 위치는 자료에 없어 미확정.'


def mp(id, title, t, pos, pages, board, faults, note, acdc=None, rng=None, method=None, led=None, check=None, caution=None):
    d = {'id': id, 'facility': 'SICAS'}
    if acdc: d['acdc'] = acdc
    d.update({'title': title, 'measureType': t, 'cycle': '미상', 'position': {'desc': pos}})
    if rng: d['range'] = rng
    if method: d['method'] = method
    if check: d['checkItems'] = check
    if led: d['ledCheck'] = led
    if caution: d['caution'] = caution
    d.update({'source': {'doc': DOC, 'page': pages}, 'boardRef': board, 'relatedFaults': faults,
              'note': note + ' ' + NOTE_TAIL, 'verify': True})
    return d


NEW = [
    mp('MP_SICAS_OLM_LED', '연동 캐비닛 OLM 전면 LED (BUMA 광접속)', 'visual',
       '연동 컴퓨터 캐비닛 OLM(BUMA 3·4·5·6 광접속). 슬롯 위치는 역별 H/W Design "연동역 구성" 확인', 'p.112, p.124, p.131, p.138',
       'SICAS_OLM', ['FLT_ILK_01', 'FLT_ILK_03'],
       'OLM 작동전압 24V DC. 광 PROFIBUS 채널별 LED로 판정. FLT_ILK_01은 STEKOP 채널1 L4 깜박임(MP_ECD_STEKOP_LED)도 함께 본다.',
       led=[{'led': '채널 LED', 'meaning': '데이터 전송 인식', 'normal': '녹색 점등'},
            {'led': '소등', 'meaning': '전원 없음 또는 광 PROFIBUS 프레임 미수신', 'normal': '-'},
            {'led': '적색', 'meaning': '송·수신 뒤바뀜, 상대 장비 미접속·전원 OFF·손상, 광케이블 길이 초과·접촉불량', 'normal': '-'},
            {'led': '황색 깜빡임', 'meaning': '네트워크 버스로 데이터 전송 없음(광접속은 정상)', 'normal': '-'}],
       check=['BUMA↔STEKOP 광접속 장애 시 OLM 각 채널 LED 소등', '광케이블 접속 단자·플러그·라인 점검']),
    mp('MP_SICAS_SVK2102_5V', 'SVK2102 출력전압 5V 및 LED (UE·UA)', 'voltage',
       '연동 컴퓨터 캐비닛 SVK2102 전원장치(채널별 3개) 전면 LED. 출력 측정 단자는 자료에 없음 — LED 우선 확인', 'p.66, p.67, p.69',
       'SICAS_SVK2102', ['FLT_ILK_12'],
       'SVK2102는 입력 60V를 5V로 변환(입력 정상 36~84V). UA 4.5V 미만이면 출력 차단, 6.3V 초과 시 출력 차단·프론트 퓨즈 F2 차단. 입력측 60V는 MP_SICAS_S51_DC60.',
       acdc='DC', rng={'min': 4.5, 'max': 6.3, 'unit': 'V', 'nominal': 5},
       method=['전면 LED UE·UA 점등 확인', '두 LED 모두 소등이면 SVK2102 장치·필터 라인·퓨즈·라인 점검(유지 p.69 표)'],
       led=[{'led': 'UE', 'meaning': '입력전압 가용', 'normal': '점등'}, {'led': 'UA', 'meaning': '출력전압 가용', 'normal': '점등'}],
       caution='SVK2102 스위치 조작 시 채널 정지 가능 — 컴퓨터 재시동 절차(1.3.7.4) 확인'),
    mp('MP_SICAS_VENUS3_LED', 'VENUS3 모듈 전면 LED · 7세그먼트 오류코드', 'visual',
       '연동 컴퓨터 캐비닛 각 채널 VENUS3(프로세서·메모리) 모듈 전면 패널', 'p.15, p.46',
       'SICAS_VENUS3', ['FLT_ILK_13'],
       'LED 밝은 점등이 정상 상태(p.46). 오류는 7세그먼트에 F.0000 형태 코드로 표시. 모듈 교체 후 컴퓨터 Reset.',
       led=[{'led': 'RS', 'meaning': '채널 리셋 상태(리셋 중 적색)', 'normal': '소등'},
            {'led': 'SD', 'meaning': '프로그램 오류(오류 시 적색, 점검 시 채널전원 차단)', 'normal': '소등'},
            {'led': '1', 'meaning': '다른 채널과의 동기 상태', 'normal': '녹색 점등'},
            {'led': '2', 'meaning': '다른 채널과의 동기 상태', 'normal': '소등'}],
       check=['관련 채널 VENUS3 LED 전부 꺼짐 → VENUS3 장치 교체 후 컴퓨터 Reset', '교체 시 EPROM 버전 확인']),
]
FMAP = {'FLT_PWR_05': ['MP_ECD_SV2602_OUT', 'MP_ECD_SV2602_IN'], 'FLT_SIG_04': ['MP_ECD_STEKOP_LED', 'MP_ECD_STEKOP_24V'],
        'FLT_SIG_05': ['MP_ECD_STEKOP_LED'], 'FLT_SIG_07': ['MP_ECD_DESIMO', 'MP_ECD_STEKOP_LED'],
        'FLT_ILK_01': ['MP_SICAS_OLM_LED', 'MP_ECD_STEKOP_LED'], 'FLT_ILK_03': ['MP_SICAS_OLM_LED'],
        'FLT_ILK_12': ['MP_SICAS_S51_DC60', 'MP_SICAS_SVK2102_5V'], 'FLT_ILK_13': ['MP_SICAS_VENUS3_LED']}

m = json.load(open(MPJ, encoding='utf-8')); ids = {p['id'] for p in NEW}
m['points'] = [p for p in m['points'] if p['id'] not in ids]
# SICAS 그룹 안에서 기존 SICAS 항목 뒤에 배치되도록 마지막에 추가
m['points'] += NEW
rel = {}
for f, l in FMAP.items():
    for x in l: rel.setdefault(x, set()).add(f)
for p in m['points']:
    if p['id'] in rel and p['id'] not in ids: p['relatedFaults'] = sorted(set(p.get('relatedFaults', [])) | rel[p['id']])
MSG = '2026-09-30(S8): SICAS 측정지점 3개 신규(MP_SICAS_OLM_LED·SVK2102_5V·VENUS3_LED, 근거 SICAS 유지보수 매뉴얼) 및 STEKOP·연동장치 고장사례 8건 연결.'
if MSG not in m['changelog']: m['changelog'].append(MSG)
open(MPJ, 'w', encoding='utf-8', newline='\r\n').write(json.dumps(m, ensure_ascii=False, indent=2))

fc = json.load(open(FCJ, encoding='utf-8')); M = {p['id'] for p in m['points']}


def walk(o):
    if isinstance(o, dict):
        if str(o.get('id', '')).startswith('FLT_') and 'symptom' in o: yield o
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)


n = 0
for c in walk(fc):
    if c['id'] in FMAP:
        assert all(x in M for x in FMAP[c['id']]); c['measurePointRef'] = FMAP[c['id']]; n += 1
open(FCJ, 'w', encoding='utf-8', newline='\r\n').write(json.dumps(fc, ensure_ascii=False, indent=2))

h = open(H, encoding='utf-8').read()
for var, d in (('MPOINTS', m), ('FCASES', fc)):
    h, k = re.subn(r'^var ' + var + r' = \{\n.*?^\};\n', lambda _: 'var ' + var + ' = ' + json.dumps(d, ensure_ascii=False, indent=2) + ';\n',
                   h, count=1, flags=re.S | re.M)
    assert k == 1
open(H, 'w', encoding='utf-8', newline='\r\n').write(h)
print('MP', len(m['points']), 'linked', n)
