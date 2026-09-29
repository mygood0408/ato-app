"""S2: 근거 재조사 결과를 power-paths.json + HTML POWER_PATHS 의 continues 문구에만 반영 (id 기준)."""
import json,re
J='power-paths.json'; H='장비구성뷰_v3_시안.html'
P=json.load(open(J,encoding='utf-8')); dump=lambda x: json.dumps(x,ensure_ascii=False,separators=(',',':'))
h=open(H,encoding='utf-8').read()
m=re.search(r'^var POWER_PATHS = (.*);$',h,re.M)
assert m.group(1)==dump(P),'JSON/HTML 불일치 — 중단'
fan=lambda a,b,c:f"fan failure 신호는 S5x 단자 76~81(fan1/fan2 fail) → 케이블 S5x.05/.07 → ID캐비닛 D51 입력으로 이어짐(=SIN·/03.13.02 p.{a}, 보드 배정 p.{b}·색인 p.{c}, S2 재조사). 단자 66~81 안쪽 팬 유닛 결선은 도면에 없음(확인필요)"
NEW={
 'PWR_SICAS_T52_60V':"Filter Z1~Z4 → SV2602 전원장치 프레임 X1(채널1·2) 결선은 SICAS 유지보수 매뉴얼 p.78 「그림 35 60V/8V 배전 배선」에 있음(일반 도면, 이 T52 도면과 직접 대응은 미검증). 랙 배치 p.224·매뉴얼 p.81(채널1·1·2·2). 8V는 매뉴얼 상 X200/X201/X202 플러그로 분배, 상대 캐비닛 X203 접속은 T51 p.206 주석뿐이고 상세도 A25140-J209-A3-*-11은 참조만 있어 PDF에 없음",
 'PWR_SICAS_T52_STEKOP_PS':"PSM-K91 접점(24/21)→STEKOP-PLATTER X3(1/7)은 8V 유무 신호 회로. 8V 자체는 SV2602가 60V를 변환해 만든다(유지보수 매뉴얼 p.81·103·137, 결선 p.78; S2 재조사). 24V 인입 원천은 p.230(=SIN1/08.02.21 9/11) 참조",
 'PWR_SICAS_N_230V':fan(179,196,270).replace('SIN·','SIN1').replace('S5x','S51'),
 'PWR_SICAS_N_230V_SIN2':fan(100,115,134).replace('SIN·','SIN2').replace('S5x','S52'),
 'PWR_SICAS_D51_24V':"인입 케이블 D51.101/102의 원천은 'Power supply SDS-Part' 표기까지만 확인(p.127·128·258). 원천 단자는 KB 전체에서 못 찾음(확인필요). MELDE2 이후 각 보드 전원은 03.13.01(p.129~)·03.13.02(p.177~)",
}
for p in P:
    if p['id'] in NEW:
        for s in p['steps']: s['continues']=NEW[p['id']]
new=dump(P); open(J,'w',encoding='utf-8').write(new)
open(H,'w',encoding='utf-8').write(h[:m.start(1)]+new+h[m.end(1):])
print('updated',[i for i in NEW])
