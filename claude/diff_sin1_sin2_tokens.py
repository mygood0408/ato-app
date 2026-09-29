"""B등급 보드의 SIN1/SIN2 토큰 차집합 표(읽기 전용). 사용: python claude/diff_sin1_sin2_tokens.py [최대sim=0.7]
보드·문서별로 SIN1 매칭쪽 전체 토큰 vs SIN2 매칭쪽 전체 토큰의 차집합에서 각 20개만 출력, 숫자성 토큰 비율 표시.
확정된 항목(note가 '자동매칭'으로 시작하지 않음)은 건너뜀. 결과는 claude/sin_diff_b.csv 에도 저장."""
import json,re,sys,csv
from compare_sin1_sin2 import toks as _toks
NOISE=re.compile(r'(sin|atp)\.pro/\d+|\d\d\.\d\d\.\d{4}|orig\./repl.*|.*projekte.*|[a-z]\d{5}-[a-z]\d+-[a-z]\d+.*|a6z0.*')
def toks(doc,p): return {re.sub(r'sin[12]/','sin/',x) for x in _toks(doc,p) if not NOISE.fullmatch(x)}
def main():
    mx=float(sys.argv[1]) if len(sys.argv)>1 else 0.7
    d=json.load(open('board-info.json',encoding='utf-8')); out=[]
    for l in d['boards'].values():
        for b in l:
            rd=b.get('relatedDrawings')
            if not isinstance(rd,dict): continue
            for r1 in rd['SIN1']:
                doc2=r1['doc'].replace('SIN1','SIN2')
                r2=next((x for x in rd['SIN2'] if x['doc']==doc2),None)
                if not r2 or not r2['note'].startswith('자동매칭'): continue
                a=set().union(*(toks(r1['doc'],p) for p in r1['pages'])); c=set().union(*(toks(doc2,p) for p in r2['pages']))
                sim=len(a&c)/len(a|c); 
                if sim>mx: continue
                o1,o2=sorted(a-c),sorted(c-a); num=lambda s:sum(bool(re.fullmatch(r'[\d./+-]+',t)) for t in s)/max(len(s),1)
                out.append((b['id'],r1['doc'][:4],round(sim,2),len(o1),len(o2),round(num(o1),2),round(num(o2),2),' '.join(sorted(o1,key=len,reverse=True)[:20]),' '.join(sorted(o2,key=len,reverse=True)[:20])))
    out.sort(key=lambda x:x[2])
    w=csv.writer(open('claude/sin_diff_b.csv','w',encoding='utf-8-sig',newline='')); w.writerow('board doc sim n1only n2only num1 num2 only1 only2'.split()); w.writerows(out)
    for r in out: print(*r[:7],sep=' '); print('  S1:',r[7][:150]); print('  S2:',r[8][:150])
if __name__=='__main__':
    sys.path.insert(0,'claude'); main()
