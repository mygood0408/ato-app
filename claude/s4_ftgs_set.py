import pymupdf, sys
from stn import ST
from s4_find_pages import norm, lines, jac
P="C:/Users/김영추/Desktop/2호선 PDF 자료/"
ref=pymupdf.open(P+ST['SIN1']['sicas']); rs=[(norm(ref[i-1].get_text(),''),lines(ref[i-1])) for i in (109,113,117,121,125)]
R={'EUL':(105,135),'GCD':(176,194),'GYO':(72,96)}
for s,(a,b) in R.items():
    d=pymupdf.open(P+ST[s]['sicas']); res=[]
    for p in range(a,b+1):
        t=norm(d[p-1].get_text(),''); l=lines(d[p-1])
        best=max((jac(t,r[0]),len(l&r[1])/max(1,len(l|r[1]))) for r in rs)
        if best[0]>=.75: res.append((p,round(best[0],2),round(best[1],2)))
    print(s,res)
