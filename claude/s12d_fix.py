# S12: 화면 확인 후 보정 — 콘덴서 점검 항목 문구, 캐비닛 1개 역의 "중 해당 쪽" 표현. JSON·HTML 동시 갱신.
import json, re
MPJ = 'measure-points.json'; H = '장비구성뷰_v3_시안.html'
m = json.load(open(MPJ, encoding='utf-8'))
p = [x for x in m['points'] if x['id'] == 'MP_SW_CAPACITOR'][0]
p['checkItems'] = ['외관 팽창/누액 여부', '단자 접속 상태', '정전용량 측정값이 기준(단동 120µF·쌍동 135µF) 이상인지 — 낮거나 불량이면 전환 모터 힘이 약해져 전환력 저하']
p['method'] = ['기동용 콘덴서 양 단자 사이를 멀티미터 정전용량(µF) 모드로 측정', '단동은 120µF, 쌍동은 135µF 이상이면 정상']
open(MPJ, 'w', encoding='utf-8', newline='\r\n').write(json.dumps(m, ensure_ascii=False, indent=2))
h = open(H, encoding='utf-8').read()
h, k1 = re.subn(r'^var MPOINTS = \{\n.*?^\};\n', lambda _: 'var MPOINTS = ' + json.dumps(m, ensure_ascii=False, indent=2) + ';\n', h, count=1, flags=re.S | re.M)
O = "' 중 해당 쪽' + (mp.position.level"
N = "(cb.length > 1 ? ' 중 해당 쪽' : '') + (mp.position.level"
assert O in h; h = h.replace(O, N)
open(H, 'w', encoding='utf-8', newline='\r\n').write(h)
s = open('claude/s12_stations.py', encoding='utf-8').read()
assert O in s; open('claude/s12_stations.py', 'w', encoding='utf-8', newline='').write(s.replace(O, N))
assert k1 == 1; print('ok')
