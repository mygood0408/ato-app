# S8: SIN1/SIN2 확인필요 도면 항목 확정 + 남은 항목 목록 저장. 재실행 가능.
import json,re,sys
sys.path.insert(0,'claude')
from s8_score import pages,kws
J='board-info.json';H='장비구성뷰_v3_시안.html'
AMB={'fan','ps','cb','ems','ifc','computer','ats','ups','twc','psd','ftgs','ato','olm','svk','n레벨','n_level_panel','ems_relay','ftgs_distributor','terminal_map_sin051','amp_module','loop_coil','ats_avr_unit','rectifier_unit','output_distribution'}
b=json.load(open(J,encoding='utf-8')); P={}; n=0; left=[]; log={}
def verdict(x,s,r):
    if x['id'].startswith('FTGS_'): return 'ok','도면 제목·이미지 확인'
    if x['id']=='SICAS_N_LEVEL_PANEL': return 'ok','S52 Level N 전원 터미널 이미지 확인'
    ks=kws(x)
    if ks[0] in AMB or ks[0].split('_')[0]=='cb' or x['id']=='ATOLOOP_CB': return 'no','핵심어 범용/모호(이미지 확인 필요)'
    pre=x['id'].split('_')[0]; sic=r['doc'].startswith('SICAS')
    if not((pre in('SICAS','ECDSTT') and sic) or (pre in('LZB','ATOLOOP') and not sic)): return 'no','보드 계통과 도면 종류 불일치(SICAS↔ATP, 이미지 확인 필요)'
    if r['doc'] not in P: P[r['doc']]=pages(r['doc'])
    h=[sum(P[r['doc']].get(p,'').count(k) for k in set(ks)) for p in r['pages']]
    if min(h)<2: return 'no','일부 쪽에서 핵심어 언급 1회 이하(이미지 확인 필요)'
    return 'ok','핵심어 전 쪽 2회 이상'
for l in b['boards'].values():
    for x in l:
        for s,lst in (x.get('relatedDrawings') or {}).items():
            for r in lst:
                if r.get('confirmed'): continue
                if s in('SIN1','SIN2'):
                    v,why=verdict(x,s,r)
                    if v=='ok': r['confirmed']=True; r.pop('note',None); n+=1; continue
                else: why='SIN 외 역(이번 세션 범위 밖, 같은 규칙 적용 예정)'
                left.append(dict(board=x['id'],stn=s,doc=r['doc'],pages=r['pages'],reason=why))
MSG='2026-09-30(S8): SIN1·SIN2 확인필요 도면 항목 %d건 확정(FTGS 궤도회로 접속도·N레벨 전원 도면은 이미지 확인, 나머지는 핵심어 전 쪽 2회 이상). 남은 항목은 claude/s8_남은목록.json.'%n
if not any(m.startswith('2026-09-30(S8)') for m in b['changelog']): b['changelog'].append(MSG)
open(J,'w',encoding='utf-8',newline='\r\n').write(json.dumps(b,ensure_ascii=False,indent=2))
h=open(H,encoding='utf-8').read()
h2,k=re.subn(r'^var BOARDINFO_RAW = \{\n.*?^\};\n',lambda m:'var BOARDINFO_RAW = '+json.dumps(b,ensure_ascii=False,indent=2)+';\n',h,count=1,flags=re.S|re.M); assert k==1
open(H,'w',encoding='utf-8',newline='\r\n').write(h2)
json.dump(left,open('claude/s8_남은목록.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
import collections
print('confirmed',n,'left',len(left),dict(collections.Counter(x['reason'][:12] for x in left)))
