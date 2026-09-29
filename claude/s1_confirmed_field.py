"""S1 일회성: note 의 직접|완료|확정 → confirmed:true 필드로 이관 (board-info relatedDrawings, rack-layout stage drawings). JSON·HTML 동시 갱신."""
import json,re
HTML='장비구성뷰_v3_시안.html'
rx=re.compile('직접|완료|확정')
def mark(arr):
    n=0
    for r in arr:
        if rx.search(r.get('note','')) and 'confirmed' not in r: r['confirmed']=True; n+=1
    return n
h=open(HTML,encoding='utf-8',newline='').read()
# board-info
s=open('board-info.json',encoding='utf-8',newline='').read(); d=json.loads(s); n1=0
for l in d['boards'].values():
    for b in l:
        for arr in (b.get('relatedDrawings') or {}).values(): n1+=mark(arr)
out=json.dumps(d,ensure_ascii=False,indent=2)
open('board-info.json','w',encoding='utf-8',newline='').write(out)
i=h.index('var BOARDINFO_RAW = ')+len('var BOARDINFO_RAW = '); _,e=json.JSONDecoder().raw_decode(h[i:])
h=h[:i]+out+h[i+e:]
# rack-layout: 줄 단위 (원본 서식 유지). JSON 파일과 HTML 내장 블록 모두 같은 변환.
n2=[0]
def fix(m):
    a=json.loads(m.group(2)); k=mark(a); n2[0]+=k
    return m.group(1)+json.dumps(a,ensure_ascii=False)+m.group(3)
pat=re.compile(r'^(\s*"drawings": )(\[.*\])(,?)$',re.M)
r=open('rack-layout.json',encoding='utf-8',newline='').read(); r2=pat.sub(fix,r); n2[0]//=1
open('rack-layout.json','w',encoding='utf-8',newline='').write(r2); nj=n2[0]; n2[0]=0
m=re.search(r'^var RACK = \{\n.*?^\};\n',h,re.S|re.M)
h=h[:m.start()]+pat.sub(fix,m.group(0))+h[m.end():]
# 렌더러
a="/직접|완료|확정/.test(r.note || '') ? '' : '확인필요'"; assert a in h
h=h.replace(a,"r.confirmed ? '' : '확인필요'")
b="' <span style=\"color:var(--ink3)\">(' + escapeHtml(r.confidence) + ')</span></li>' : '';"; assert b in h
h=h.replace(b,"(r.confidence === '확정' ? '' : ' <span style=\"color:var(--ink3)\">(' + escapeHtml(r.confidence) + ')</span>') + '</li>' : '';")
open(HTML,'w',encoding='utf-8',newline='').write(h)
print('board',n1,'rackJSON',nj,'rackHTML',n2[0])
