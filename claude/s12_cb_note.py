# S12: board-info.json·HTML(BOARDINFO_RAW)에 C/B박스 혼합형·센터패드 표현 기준 코멘트와 OT 연결선 설명 추가.
import json, re
BJ = 'board-info.json'; H = '장비구성뷰_v3_시안.html'
b = json.load(open(BJ, encoding='utf-8'))
h = open(H, encoding='utf-8').read()
m = re.search(r'^var BOARDINFO_RAW = (\{.*?^\});\n', h, re.S | re.M)
assert json.loads(m.group(1)) == b, 'HTML BOARDINFO_RAW != board-info.json'
OT = ' [2026-10-03 S12] 보라색 점선은 기계실 OT반으로 나가는 선. 인터페이스 모듈은 번호 없는 단자=튜닝유니트 연결, 1~4번 단자=OT반 연결(좌측 튜닝유니트 1·2번, 우측 3·4번). 전환모듈은 3~6번=튜닝유니트 연결, 1·2번=OT반 연결.'
ADD = {
 'FTGS_CB_UNI': OT, 'FTGS_CB_BI': OT,
 'FTGS_CB_MIXED': OT + ' 그림은 단방향 궤도가 좌측에 있는 경우를 표현함(인터페이스 1·2번 사용). 단방향 궤도가 우측이면 인터페이스 3·4번 사용.',
 'FTGS_CB_CENTERPAD': OT + ' 그림은 튜닝유니트가 우측에 설치된 경우를 표현함(인터페이스 3·4번 사용). 좌측 설치면 1·2번, 튜닝유니트가 2개면 1~4번 사용.',
}
n = 0
for x in (y for lst in b['boards'].values() for y in lst):
    if x['id'] in ADD:
        assert ADD[x['id']] not in x.get('note', ''); x['note'] = (x.get('note', '') + ADD[x['id']]).strip(); n += 1
assert n == 4
b['changelog'].append('2026-10-03(S12): C/B박스 4종 보드 이미지에 기계실 OT반 연결선(쓰는 단자만) 추가, 혼합형·센터패드 표현 기준 코멘트 추가.')
open(BJ, 'w', encoding='utf-8', newline='\r\n').write(json.dumps(b, ensure_ascii=False, indent=2))
h = h[:m.start(1)] + json.dumps(b, ensure_ascii=False, indent=2) + h[m.end(1):]
open(H, 'w', encoding='utf-8', newline='\r\n').write(h)
print('ok')
