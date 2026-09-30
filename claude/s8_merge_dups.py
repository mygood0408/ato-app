# S8: 매뉴얼 6장에서 여러 절에 반복 수록된 고장 4쌍 병합 — 설비 분류 사례를 대표로 남기고 신호기 사본 삭제, alsoDomains=['신호기'] 추가. JSON·HTML 동기화. 재실행 가능.
import json, re
FCJ = 'fault-cases.json'; MPJ = 'measure-points.json'; BJ = 'board-info.json'; H = '장비구성뷰_v3_시안.html'
PAIRS = {'FLT_ECD_02': 'FLT_SIG_06', 'FLT_ECD_07': 'FLT_SIG_08', 'FLT_ILK_01': 'FLT_SIG_02', 'FLT_PWR_01': 'FLT_SIG_03'}
DROP = {v: k for k, v in PAIRS.items()}
fc = json.load(open(FCJ, encoding='utf-8')); F = {c['id']: c for c in fc['cases']}
if all(d in F for d in DROP):
    for keep, drop in PAIRS.items():
        k, d = F[keep], F[drop]
        k['alsoDomains'] = sorted(set(k.get('alsoDomains', [])) | {d['domain']})
        k['measurePointRef'] = list(dict.fromkeys((k.get('measurePointRef') or []) + (d.get('measurePointRef') or [])))
        k['manualRefs'] = list(dict.fromkeys((k.get('manualRefs') or []) + (d.get('manualRefs') or [])))
        ks, ds = k.get('source') or {}, d.get('source') or {}
        cand = (ks.get('sectionPageCandidates') or []) + (ds.get('sectionPageCandidates') or [])
        if cand: ks['sectionPageCandidates'] = cand
        if ds.get('section') and ds['section'] != ks.get('section'):
            ks['section'] = str(ks.get('section')) + ', ' + str(ds['section'])
        k['source'] = ks
    fc['cases'] = [c for c in fc['cases'] if c['id'] not in DROP]
    MSG = '2026-09-30(S8): 매뉴얼 6장에서 여러 절에 반복 수록된 고장 4쌍 병합 — ECD_02(+SIG_06), ECD_07(+SIG_08), ILK_01(+SIG_02), PWR_01(+SIG_03). 설비 분류 사례를 대표로 남기고 신호기 사본 삭제, 대표 사례에 alsoDomains=["신호기"]를 두어 신호기 분류에서도 표시.'
    if MSG not in fc['changelog']: fc['changelog'].append(MSG)
open(FCJ, 'w', encoding='utf-8', newline='\r\n').write(json.dumps(fc, ensure_ascii=False, indent=2))
# 다른 데이터의 참조 치환
for jf in (MPJ, BJ):
    s = open(jf, encoding='utf-8', newline='').read()
    d = json.loads(s)

    def fix(o):
        if isinstance(o, list):
            out = []
            for x in o:
                x = fix(x)
                if isinstance(x, str) and x in DROP: x = DROP[x]
                if not (isinstance(x, str) and x in out): out.append(x)
            return out
        if isinstance(o, dict): return {k: fix(v) for k, v in o.items()}
        return o
    d2 = fix(d)
    if d2 != d: open(jf, 'w', encoding='utf-8', newline='\r\n').write(json.dumps(d2, ensure_ascii=False, indent=2))
h = open(H, encoding='utf-8').read()
m = json.load(open(MPJ, encoding='utf-8')); b = json.load(open(BJ, encoding='utf-8'))
for var, dd in (('FCASES', fc), ('MPOINTS', m), ('BOARDINFO_RAW', b)):
    h, k = re.subn(r'^var ' + var + r' = \{\n.*?^\};\n', lambda _: 'var ' + var + ' = ' + json.dumps(dd, ensure_ascii=False, indent=2) + ';\n', h, count=1, flags=re.S | re.M); assert k == 1
# 화면: alsoDomains 를 분류 필터·건수·상세에 반영
if 'faultInDomain' not in h:
    h = h.replace("function faultDomainCounts(cases){\n  var counts = {};\n  cases.forEach(function(c){ var d = c.domain || '기타'; counts[d] = (counts[d] || 0) + 1; });\n",
                  "function faultInDomain(c, d){ return c.domain === d || (c.alsoDomains || []).indexOf(d) >= 0; }\nfunction faultDomainCounts(cases){\n  var counts = {};\n  cases.forEach(function(c){ [c.domain || '기타'].concat(c.alsoDomains || []).forEach(function(d){ counts[d] = (counts[d] || 0) + 1; }); });\n")
    a = "items = items.filter(function(x){ return x.c.domain === state.faultDomain; });"
    assert h.count(a) == 1; h = h.replace(a, "items = items.filter(function(x){ return faultInDomain(x.c, state.faultDomain); });")
    a = "  h += '<dt>분류</dt><dd>' + faultHl(fc.domain) + '</dd>';"
    assert h.count(a) == 1
    h = h.replace(a, "  h += '<dt>분류</dt><dd>' + faultHl(fc.domain) + ((fc.alsoDomains || []).length ? ' <span style=\"color:var(--ink3)\">(' + escapeHtml(fc.alsoDomains.join(', ')) + ' 분류에도 표시)</span>' : '') + '</dd>';")
open(H, 'w', encoding='utf-8', newline='\r\n').write(h)
print('cases', len(fc['cases']))
