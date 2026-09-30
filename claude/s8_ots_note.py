# S8: 측정지점이 없는 OTS 사례 14건에 measureNote(OTS 감시화면 안내) 추가 + 고장 상세 렌더. JSON·HTML 동기화. 재실행 가능.
import json, re
FCJ = 'fault-cases.json'; H = '장비구성뷰_v3_시안.html'
NOTE = '측정값은 OTS(선로전환기 감시시스템) 감시 화면에서 확인합니다. 이 앱에는 OTS 측정지점이 없습니다.'
fc = json.load(open(FCJ, encoding='utf-8')); n = 0
for c in fc['cases']:
    if not c.get('measurePointRef') and ('OTS' in c['domain'] or c['id'] == 'FLT_SW_01'):
        c['measureNote'] = NOTE; n += 1
MSG = '2026-09-30(S8): 측정지점 없는 OTS 사례 %d건에 measureNote(OTS 감시화면 안내) 추가, 고장 상세에 표시.' % n
if MSG not in fc['changelog']: fc['changelog'].append(MSG)
open(FCJ, 'w', encoding='utf-8', newline='\r\n').write(json.dumps(fc, ensure_ascii=False, indent=2))
h = open(H, encoding='utf-8').read()
h, k = re.subn(r'^var FCASES = \{\n.*?^\};\n', lambda _: 'var FCASES = ' + json.dumps(fc, ensure_ascii=False, indent=2) + ';\n', h, count=1, flags=re.S | re.M); assert k == 1
old = "  if (acts) h += '<div class=\"stage-actions\">' + acts + '</div>';\n"
new = old + "  if (fc.measureNote && !mpRefs.length) h += '<div class=\"note-text\" style=\"margin-top:8px\">📍 ' + escapeHtml(fc.measureNote) + '</div>';\n"
if 'fc.measureNote' not in h:
    assert h.count(old) == 1; h = h.replace(old, new)
open(H, 'w', encoding='utf-8', newline='\r\n').write(h)
print('measureNote', n)
