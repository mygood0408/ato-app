"""역_인벤토리.md 표 -> stations.json (역 접미사별 SICAS/ATP 문서명·쪽수·주 캐비닛). 쪽 매핑(paths)은 기존 값을 보존."""
import re, json, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
md = open(os.path.join(R, 'claude', '역_인벤토리.md'), encoding='utf-8').read()
sic = md.split('## SICAS HW Design')[1].split('## ATP HW Design')[0]
atp = md.split('## ATP HW Design')[1].split('## 템플릿')[0]
A = {m[0]: m[1] for m in re.findall(r'^\| (\w+) \| (\d+) \|', atp, re.M)}
out = json.load(open(os.path.join(R, 'stations.json'), encoding='utf-8')) if os.path.exists(os.path.join(R, 'stations.json')) else {}
for k, pg, cab in re.findall(r'^\| (\w+) \| (\d+) \| \w+ \| ([^|]*?) \|', sic, re.M):
    base = re.sub(r'\d$', '', k)
    e = out.get(k, {})
    e.update({"station": base, "sicas": "SICAS HW Design White_%s.pdf" % k, "sicasPages": int(pg),
              "atp": ("ATP HW Design_%s.pdf" % (k if k in A else base)), "cabinet": cab.split(';')[0].strip()})
    e.setdefault("paths", {}); e.setdefault("titleCab", e["cabinet"])
    out[k] = e
json.dump(out, open(os.path.join(R, 'stations.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out), 'stations')
