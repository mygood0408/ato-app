"""C5: powerFlow stage drawings + SIN2 board links. Text-insert into JSON and HTML (kept in sync)."""
import json, re, sys
S1, S2 = 'SICAS_HW_Design_SIN1', 'SICAS_HW_Design_SIN2'
def d(doc, pages, note): return {'doc': doc, 'pages': pages, 'note': note}
N = '전원 경로 ⚡ 있음, 확인필요'
STAGES = {  # stage title prefix -> drawings
 'N레벨 배전반 (후면 K행)': [d(S1,[188],'직접 확인 — '+N), d(S2,[107],'SIN2 대응 도면 — '+N)],
 '24V 퓨즈 (N레벨': [d(S1,[188],'직접 확인 — '+N), d(S2,[107],'SIN2 — '+N)],
 '220V AC → FAN (N레벨': [d(S1,[188],'직접 확인 — '+N), d(S2,[107],'SIN2 — '+N)],
 '60V 퓨즈(4A) → 필터': [d(S1,[230],'T52 G단자 도면 직접 확인 — '+N)],
 '전원공급장치 SV2602': [d(S1,[230,206,224],'p.230 직접 확인 — '+N+' (Filter→SV2602 배선은 도면에 없음)')],
 'Platter (-X4': [d(S1,[106],'STEKOP 8V 공급 조건 회로(8V 생성 회로는 아님) — 확인필요')],
 '퓨즈 레일 (전면 L행': [d(S1,[109,113,117,121,125],'FTGS 궤도회로 전원 — '+N), d(S2,[36,40,44,48],'SIN2 F56~F59 — '+N)],
}
BOARDS = {  # existing unique line -> extra SIN2 line
 '{"doc": "SICAS_HW_Design_SIN1", "pages": [188], "note": "S51 캐비닛 N레벨 전원 도면 직접 확인(전원 경로 ⚡ 있음, 확인필요)"}':
   d(S2,[107],'SIN2 S52 N레벨 대응 도면(전원 경로 ⚡ 있음, 확인필요)'),
 '{"doc": "SICAS_HW_Design_SIN1", "pages": [109, 113, 117, 121, 125], "note": "FTGS 궤도회로 전원(ID캐비닛 24V→퓨즈→릴레이접점→TR) F51~F55 도면(전원 경로 ⚡ 있음, 확인필요; 보드 대응 관계 미확인)"}':
   d(S2,[36,40,44,48],'SIN2 F56~F59 도면(전원 경로 ⚡ 있음, 확인필요; 보드 대응 관계 미확인)'),
}
dump = lambda o: json.dumps(o, ensure_ascii=False)
def patch(path):
    t = open(path, encoding='utf-8').read(); n = 0
    for pre, dr in STAGES.items():
        pat = re.compile(r'^(\s*)"stage": "' + re.escape(pre) + r'[^\n]*\n', re.M)
        def rep(m):
            nonlocal n; n += 1
            return m.group(0) + m.group(1) + '"drawings": ' + dump(dr) + ',\n'
        if '"drawings": ' in t and pre in t and re.search(re.escape(pre)+r'[^\n]*\n\s*"drawings"', t): continue
        t = pat.sub(rep, t, count=1)
    for old, new in BOARDS.items():
        if dump(new) in t or old not in t: continue
        assert t.count(old) == 1, (path, old[:40], t.count(old))
        i = t.index(old); ind = t.rfind('\n', 0, i) + 1; sp = t[ind:i]
        t = t.replace(old, old + ',\n' + sp + dump(new), 1); n += 1
    open(path, 'w', encoding='utf-8', newline='').write(t); print(path, n)
patch('rack-layout.json'); patch('board-info.json'); patch('장비구성뷰_v3_시안.html')
for p in ('rack-layout.json','board-info.json'): json.load(open(p, encoding='utf-8'))
