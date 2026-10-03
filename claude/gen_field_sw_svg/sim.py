import itertools, collections
# 한 대(prefix 로 A/B 구분) 내부 연결: 단자 <-> 제어계전기/회로제어기 핀 (설치상세도 p.5 선 추적 결과)
def machine(p, jumpers):
    E=[]  # 항상 연결
    w=lambda a,b: E.append((p+a,p+b))
    # 단자 -> 핀
    w('T10','p10'); w('T10','R4'); w('T8','N3'); w('T8','p8'); w('T4','p4'); w('T6','p6'); w('T3','p3'); w('T5','p5'); w('T1','p1'); w('T2','p2')
    w('R3','R3c'); w('N4','N4c'); w('C3','p7'); w('C4','p9')
    # 내부 파선 연결
    w('p6','p7p'); w('p5','p9r'); w('G','Gp')
    for a,b in jumpers: w('T'+a if a[0].isdigit() else a, 'T'+b if b[0].isdigit() else b)
    return E
def contacts(p, relay, ctrl):
    """relay 'N'|'R'; ctrl in P_N,P_R,P_RUN -> 닫힌 접점 간선"""
    c=[]
    for k in ('3','4'):
        c.append((p+'C'+k, p+('N3' if k=='3' else 'N4c') if relay=='N' else p+('R3c' if k=='3' else 'R4')))
    closed={'N':['G-A','p1-p6','p9-p9r','p10-p4'],'R':['p3-p8','p7p-p7','p5-p2','p?'],}
    return c
def ctrl_edges(p, state):
    pairs={'NC1':('G','A'),'NC2':('p1','p6'),'N1':('p9','p9r'),'N2':('p10','p4'),'R1':('p3','p8'),'R2':('p7p','p7'),'RC1':('p5','p2'),'RC2':('B','Gp')}
    on={'N':['NC1','NC2','N1','N2'],'R':['R1','R2','RC1','RC2'],'RUN':['NC1','NC2','RC1','RC2']}[state]
    return [(p+pairs[k][0],p+pairs[k][1]) for k in on]
def relay_edges(p, st):
    s='N' if st=='N' else 'R'
    return [(p+'C3',p+('N3' if s=='N' else 'R3c')),(p+'C4',p+('N4c' if s=='N' else 'R4'))]
class UF:
    def __init__(s): s.p={}
    def f(s,x):
        s.p.setdefault(x,x)
        while s.p[x]!=x: s.p[x]=s.p[s.p[x]]; x=s.p[x]
        return x
    def u(s,a,b): s.p[s.f(a)]=s.f(b)
def conn(edges):
    u=UF()
    for a,b in edges: u.u(a,b)
    return u
def run(name, machines, links, relay, ctrl, probes):
    E=[]
    for p,j in machines:
        E+=machine(p,j); E+=ctrl_edges(p,ctrl); E+=relay_edges(p,relay)
    E+=links
    u=conn(E)
    print(name, relay, ctrl, {f'{a}~{b}':u.f(a)==u.f(b) for a,b in probes})
if __name__=='__main__':
    J_S=[('R3','N4'),('8','10'),('5','3'),('1','2'),('4','6')]
    J_A=[('R3','N4'),('8','10'),('3','1'),('2','4')]
    J_B=[('5','3'),('1','2'),('4','6')]
    # 단동: + = T10, - = N4 ; 외부 표시계전기 = T4(6) ~ T3(5)
    for relay,ctrl in (('N','N'),('R','R'),('N','R'),('N','RUN'),('R','N'),('R','RUN')):
        run('단동',[('',J_S)],[],relay,ctrl,[('T10','T4'),('T10','T3'),('T4','N4'),('T3','N4'),('T10','N4'),('T4','T3')])
