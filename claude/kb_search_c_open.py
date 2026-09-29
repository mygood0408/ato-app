import re,os,sys,collections,json
KB=r"C:\Users\김영추\Desktop\2호선 PDF 자료\PDF_Knowledge_Base\01_pages"
KW={
 'SV2602':r'SV\s*2602',
 '60V/8V':r'60\s*V\s*/\s*8\s*V|60V.{0,10}8V',
 'X203':r'X\s*20[03]',
 'J209':r'J209',
 'T51/T52':r'\bT5[12]\b',
 'FanFail':r'fan\s*fail|Lüfter|팬.{0,6}(고장|알람|경보)|fan\s*unit',
 'STEKOP8V':r'STEKOP.{0,40}8\s*V|8\s*V.{0,40}STEKOP',
 '110VAC':r'110\s*V\s*(AC|~)|AC\s*110',
 'D51.10x':r'D51\.10[12]|51_S[12]',
 'PowerSupplySDS':r'Power\s*supply.{0,20}SDS|SDS.{0,20}Power\s*supply',
 'FilterZ':r'Filter\s*Z\s*[1-4]|Line\s*Load\s*Filter',
 '단자40-49':r'단자\s*4\d',
}
docs=sorted(os.listdir(KB))
res=collections.defaultdict(lambda: collections.defaultdict(list))
ex={}
for d in docs:
    dp=os.path.join(KB,d)
    for f in sorted(os.listdir(dp)):
        if not f.endswith('.md'):continue
        pg=int(re.search(r'(\d+)',f).group(1))
        t=open(os.path.join(dp,f),encoding='utf-8',errors='ignore').read()
        tn=re.sub(r'\s+',' ',t)
        for k,rx in KW.items():
            m=re.search(rx,tn,re.I)
            if m:
                res[k][d].append(pg)
                if (k,d) not in ex:
                    s=max(0,m.start()-30);ex[(k,d)]=re.sub(r'\s+',' ',t[s:m.end()+50])[:90]
out=['# KB 키워드 검색 (문서별 쪽, 자동생성)\n']
for k in KW:
    out.append(f'\n## {k}')
    for d,pgs in res[k].items():
        out.append(f'- {d}: {len(pgs)}쪽 {pgs[:14]}{"…" if len(pgs)>14 else ""} | {ex[(k,d)]}')
open('kb_search_c_open_result.md','w',encoding='utf-8').write('\n'.join(out))
print({k:sum(len(v) for v in res[k].values()) for k in KW})
