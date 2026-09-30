# S8: 약한추천 12건 확정 반영 — 측정지점 4개 신규(TWC IMU-100 LED, FTGS 전원 12V·5V, 궤도 접속상자) + 연결 + FLT_FTGS_01 삭제. 재실행 가능.
import json, re
MPJ = 'measure-points.json'; FCJ = 'fault-cases.json'; H = '장비구성뷰_v3_시안.html'
TAIL = '2026-09-30 신규(S8): 정기점검 주기·실측 위치는 자료에 없어 미확정.'
DMM = 'Digital Multimeter'


def mp(id, fac, doc, title, t, pos, pages, board, faults, note, acdc=None, rng=None, method=None, led=None, check=None, caution=None, instr=None):
    d = {'id': id, 'facility': fac}
    if acdc: d['acdc'] = acdc
    d.update({'title': title, 'measureType': t, 'cycle': '미상', 'position': {'desc': pos}})
    if rng: d['range'] = rng
    if instr: d['instrument'] = instr
    if method: d['method'] = method
    if check: d['checkItems'] = check
    if led: d['ledCheck'] = led
    if caution: d['caution'] = caution
    d.update({'source': {'doc': doc, 'page': pages}, 'boardRef': board, 'relatedFaults': faults, 'note': note + ' ' + TAIL, 'verify': True})
    return d


TWC = 'TWC 유지보수 매뉴얼(TWC_유지보수_매뉴얼)'; FT = 'FTGS 유지보수 매뉴얼(FTGS_유지보수_매뉴얼)'
NEW = [
    mp('MP_TWC_IMU100_LED', 'TWC', TWC, 'IMU-100(PTI 수신기) 전면 LED (Data1~8·전원·장애)', 'visual',
       'TWC 연동역 모듈(서브랙) IMU-100 PTI 수신기 전면 패널', 'p.13, p.14', 'TWC_IMU100', ['FLT_TWC_02', 'FLT_TWC_03'],
       '수신기는 채널별 Lemo 커넥터 Core[n]/Rim[n] 신호라인. 장애 시 장애 시간·장애 주파수·전면 패널 표시를 기록하고 예비품으로 교체, 그래도 안 되면 케이블·퓨즈(F1 M 2.5A 5x20)·전원 점검.',
       led=[{'led': '초록', 'meaning': '일반 동작 상태', 'normal': '점등 또는 점멸'},
            {'led': '황색', 'meaning': '상태의 변이', 'normal': '소등 또는 점멸'},
            {'led': '적색', 'meaning': '장애 발생', 'normal': '소등(상시 점등·점멸 = 장애)'},
            {'led': 'Power / Vint / Vext(녹색)', 'meaning': '외부 24V 입력 / 내부 동작전원 / 안테나 공급전원', 'normal': '항시 점등'},
            {'led': 'Data1~Data8(황색)', 'meaning': '채널별 수신 데이터', 'normal': '짧은 점멸(유효 데이터 수신) 또는 점멸(계속 수신)'},
            {'led': 'Data LED 소등', 'meaning': '수신 채널 케이블 미배선·비활성 또는 유효 데이터 미수신', 'normal': '-'},
            {'led': 'Data LED 항시 점등', 'meaning': '수신채널 장애 가능, 장비 교체 필요할 수 있음', 'normal': '-'}],
       check=['적색 LED 상시 점등·점멸 → 커넥션 박스 자체 이상이면 박스 교환, 연동역 모듈 이상이면 TWC 서브랙 교환', '교체 후 "TWC 시험 절차서"에 따라 증폭 조정']),
    mp('MP_FTGS_PS_12V', 'FTGS', FT, 'FTGS 후면 전원공급장치 출력 12V', 'voltage',
       'FTGS 캐비닛 후면 전원공급장치(V25913-Z150-C1, 궤도회로 2개당 1개). 측정소켓 "12V / 0V power supply"', 'p.18, p.34', 'FTGS_POWER_UNIT',
       ['FLT_FTGS_02'], '전원공급장치 입력 AC 220/230V(187~264V, 47~63Hz). 퓨즈 내장 안 됨. 출력은 과부하·단락 보호. 전원 공급장치를 뽑기 전 관련 궤도회로가 진로에 없도록(가능하면 진로 취소) 할 것.',
       acdc='DC', rng={'min': 11, 'max': 13, 'unit': 'V', 'nominal': 12},
       method=['측정소켓 12V/0V 사이 DC 측정(측정범위 30V DC)', '송신보드 LED L9(12V 전원 공급)로도 확인'], instr=DMM,
       caution='전원공급장치의 전원 연결 플러그를 뽑으면 두 궤도회로가 동시에 영향받음'),
    mp('MP_FTGS_PS_5V', 'FTGS', FT, 'FTGS 후면 전원공급장치 출력 5V', 'voltage',
       'FTGS 캐비닛 후면 전원공급장치(V25913-Z150-C1). 측정소켓 "5V / 0V power supply"', 'p.18, p.34', 'FTGS_POWER_UNIT',
       ['FLT_FTGS_02'], '입력 AC 220/230V. 보드 Vcc/Vcc2(-B44 소켓)도 5V±0.5V.',
       acdc='DC', rng={'min': 4.5, 'max': 5.5, 'unit': 'V', 'nominal': 5},
       method=['측정소켓 5V/0V 사이 DC 측정(측정범위 10V DC)'], instr=DMM),
    mp('MP_FTGS_TRACK_CB', 'FTGS', FT, '궤도 접속상자 내부 (튜닝보드·스위치 전환보드·배선)', 'visual',
       '현장 궤도 접속상자(C/B) 내부. 1개 접속상자에 인접 궤도회로 2개 설비', 'p.35, p.36, p.37, p.38', 'FTGS_CB_UNI',
       ['FLT_FTGS_04'], '튜닝보드는 주파수별로 종류가 다름(S25533-D10/D22/D16-A..). 전환모듈 입력 터미널 11(파랑)·14(빨강), 출력 15(회색)·16(노랑), 전원선은 전환모듈 터미널 1·2. 궤도 연결 케이블 A·C는 튜닝보드 터미널 9, B·D는 터미널 10. 접속상자와 실내설비 사이는 낙뢰·과전압 보호(낙뢰방지 퓨즈).',
       check=['튜닝보드 물품번호 뒷자리가 해당 궤도회로 주파수와 일치하는지', '스위치 전환보드(S25533-A55-A1~A8) 주파수 일치', '낙뢰방지 퓨즈 상태, 접속상자 접지', '전환모듈 입력 11/14·출력 15/16 결선, 튜닝보드 저항 브리지(터미널 2-7-8 등)', '튜닝보드·전환보드 교체 후에는 늦어도 다음날까지 궤도계전기 낙하시험']),
]
FMAP = {'FLT_PWR_06': ['MP_ECD_SV2602_OUT', 'MP_ECD_SV2602_IN'], 'FLT_PWR_07': ['MP_ECD_SV2602_OUT', 'MP_ECD_SV2602_IN'],
        'FLT_SIG_02': ['MP_SICAS_OLM_LED', 'MP_ECD_STEKOP_LED'], 'FLT_SIG_06': ['MP_ECD_STEKOP_LED', 'MP_ECD_STEKOP_24V'],
        'FLT_SIG_09': ['MP_ECD_DESIMO', 'MP_FIELD_SIG_LAMP'], 'FLT_VEN_01': ['MP_SICAS_VENUS3_LED'],
        'FLT_TWC_02': ['MP_TWC_IMU100_LED', 'MP_TWC_RX_WAVEFORM'], 'FLT_TWC_03': ['MP_TWC_IMU100_LED', 'MP_TWC_CB_DETAIL'],
        'FLT_FTGS_02': ['MP_FTGS_PS_12V', 'MP_FTGS_PS_5V'], 'FLT_FTGS_03': ['MP_FTGS_RELAY'],
        'FLT_FTGS_04': ['MP_FTGS_DCBOX', 'MP_FTGS_TX_FIELD', 'MP_FTGS_RX_FIELD', 'MP_FTGS_SBOND', 'MP_FTGS_TRACK_CB']}

m = json.load(open(MPJ, encoding='utf-8')); ids = {p['id'] for p in NEW}
m['points'] = [p for p in m['points'] if p['id'] not in ids] + NEW
rel = {}
for f, l in FMAP.items():
    for x in l: rel.setdefault(x, set()).add(f)
for p in m['points']:
    if p['id'] in rel and p['id'] not in ids: p['relatedFaults'] = sorted(set(p.get('relatedFaults', [])) | rel[p['id']])
MSG = '2026-09-30(S8): 측정지점 4개 신규(MP_TWC_IMU100_LED, MP_FTGS_PS_12V·5V, MP_FTGS_TRACK_CB) 및 약한추천 12건 확정 반영(고장사례 11건 연결, FLT_FTGS_01 삭제).'
if MSG not in m['changelog']: m['changelog'].append(MSG)
open(MPJ, 'w', encoding='utf-8', newline='\r\n').write(json.dumps(m, ensure_ascii=False, indent=2))

fc = json.load(open(FCJ, encoding='utf-8')); M = {p['id'] for p in m['points']}
fc['cases'] = [c for c in fc['cases'] if c['id'] != 'FLT_FTGS_01']
n = 0
for c in fc['cases']:
    if c['id'] in FMAP:
        assert all(x in M for x in FMAP[c['id']]), c['id']; c['measurePointRef'] = FMAP[c['id']]; n += 1
MSG2 = '2026-09-30(S8): FLT_FTGS_01(ATS 열차만 낙하) 삭제(사용자 지시: ATS 관련 불필요). 약한추천 11건 측정지점 연결.'
if MSG2 not in fc['changelog']: fc['changelog'].append(MSG2)
open(FCJ, 'w', encoding='utf-8', newline='\r\n').write(json.dumps(fc, ensure_ascii=False, indent=2))

h = open(H, encoding='utf-8').read()
for var, d in (('MPOINTS', m), ('FCASES', fc)):
    h, k = re.subn(r'^var ' + var + r' = \{\n.*?^\};\n', lambda _: 'var ' + var + ' = ' + json.dumps(d, ensure_ascii=False, indent=2) + ';\n',
                   h, count=1, flags=re.S | re.M)
    assert k == 1
open(H, 'w', encoding='utf-8', newline='\r\n').write(h)
print('MP', len(m['points']), 'cases', len(fc['cases']), 'linked', n)
