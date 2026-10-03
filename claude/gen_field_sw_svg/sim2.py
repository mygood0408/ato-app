import itertools, sys
sys.path.insert(0, '.')
from sim import machine, ctrl_edges, relay_edges, UF

# 단자 번호 -> sim 노드: 'T'+번호, R3/N4 는 sim 에서 'R3','N4' 로 단자 노드 (machine 의 w('R3','R3c'), w('N4','N4c'))
def T(n):
    return 'T' + n if n[0].isdigit() else n

def unit_edges(p, jumpers, dotted, relay, ctrl):
    E = machine(p, jumpers)
    E += ctrl_edges(p, ctrl) + relay_edges(p, relay)
    for a, b in dotted:
        E.append((p + T(a), p + T(b)))
    return E

def groups(E):
    u = UF()
    for a, b in E:
        u.u(a, b)
    return u

J_A = [('R3', 'N4'), ('8', '10'), ('3', '1'), ('2', '4')]
J_B = [('5', '3'), ('1', '2'), ('4', '6')]
J_S = [('R3', 'N4'), ('8', '10'), ('5', '3'), ('1', '2'), ('4', '6')]

def report(name, p, J, dotted, relay, ctrl, plus='N4', minus='T10'):
    E = unit_edges(p, J, dotted, relay, ctrl)
    u = groups(E)
    P, M = u.f(p + plus), u.f(p + minus)
    print(name, 'relay', relay, 'ctrl', ctrl, 'SHORT' if P == M else 'ok',
          '+:', sorted(t[len(p):] for t in u.p if u.f(t) == P and t.startswith(p + 'T') or (u.f(t) == P and t.startswith(p) and t[len(p):] in ('N4', 'R3'))),
          '-:', sorted(t[len(p):] for t in u.p if u.f(t) == M and t.startswith(p + 'T') or (u.f(t) == M and t.startswith(p) and t[len(p):] in ('N4', 'R3'))))

if __name__ == '__main__':
    opts = {
        '205정위(RIGHT) A': [('N4', '6'), ('10', '3')],
        '205반위(RIGHT) A': [('N4', '5'), ('10', '4')],
    }
    for nm, dot in opts.items():
        for relay, ctrl in (('N', 'N'), ('R', 'R')):
            report(nm, '', J_A, dot, relay, ctrl)
    print('--- 점선 없이(기본 점퍼만)')
    for relay, ctrl in (('N', 'N'), ('R', 'R')):
        report('A점퍼만', '', J_A, [], relay, ctrl)
