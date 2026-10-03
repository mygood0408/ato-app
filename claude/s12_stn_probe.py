import re,glob,json,os
B="C:/Users/김영추/Desktop/2호선 PDF 자료/PDF_Knowledge_Base/01_pages/"
def body(f): return re.sub(r'\s+',' ',open(f,encoding='utf-8',errors='ignore').read().split('## 추출 텍스트')[-1])
def scan(k):
    r={x:[] for x in ['G','M','SV','STK_FRAME','STK_ALLOC','DEW','S_OLM','S_SVK','S_VEN','ECDCABS']}
    cabs=set()
    for f in sorted(glob.glob(B+f"SICAS_HW_Design_{k}/page_*.md")):
        p=int(re.search(r'(\d+)\.md',f).group(1)); t=body(f)
        ec=re.search(r'EC/DSTT Cabinet (T\d+) cabinet construction plan',t)
        sc=re.search(r'SICAS[- ]Cabinet (S\d+) cabinet construction plan',t)
        if ec:
            cabs.add(ec.group(1))
            if '+24V1' in t and '+24V2' in t: r['G'].append(p)
            if 'Line Load Filter' in t: r['M'].append(p)
            if 'SV 2602' in t: r['SV'].append(p)
            if 'STEKOP S25140' in t: r['STK_FRAME'].append(p)
            if 'DEWEMO' in t or 'DESIMO' in t: r['DEW'].append(p)
        if re.search(r'Alloc\. STEKOP-Platter',t): r['STK_ALLOC'].append(p)
        if sc:
            if 'OLM' in t: r['S_OLM'].append(p)
            if 'SVK 2102' in t: r['S_SVK'].append(p)
            if 'VENUS3' in t: r['S_VEN'].append(p)
    r['ECDCABS']=sorted(cabs)
    return r
if __name__=='__main__':
    for k in json.load(open('stations.json',encoding='utf-8')):
        r=scan(k); print(k,{a:(b if a=='ECDCABS' else len(b)) for a,b in r.items()})
