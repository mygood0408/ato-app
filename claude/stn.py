"""make_power_paths*.py 공용: --station <접미사>(없으면 env STN, 기본 SIN1) + stations.json 조회."""
import json, os, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
ST = json.load(open(os.path.join(ROOT, 'stations.json'), encoding='utf-8'))
def _arg():
    a = sys.argv
    if '--station' in a:
        i = a.index('--station'); s = a[i + 1]; del a[i:i + 2]; return s
    return os.environ.get('STN')
STN = _arg() or 'SIN1'
BASE = 'SIN1'  # 기준 역: id 접미사 없음
CFG = ST[STN]
PDF = "C:/Users/김영추/Desktop/2호선 PDF 자료/" + CFG['sicas']
CAB = CFG['titleCab']            # 제목용 캐비닛명 (SIN1·SIN2 는 기존 결과 유지 위해 S51)
PCAB = 'P' + CAB[1:]             # 전원반
DCAB = CFG.get('dcab', 'D' + CAB[1:])  # ID 캐비닛
def pid(base_id, stn=None): return base_id + ("" if (stn or STN) == BASE else "_" + (stn or STN))
def page(key):
    p = CFG['paths'].get(key)
    if not p: print('확인필요: %s 의 %s 쪽 미지정(stations.json paths.%s) — 경로 생성 안 함' % (STN, key, key), file=sys.stderr); sys.exit(0)
    return p
