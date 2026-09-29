"""S5: s5_pages.json -> stations.json(paths,dcab) -> 역별 make_power_paths(.py/_n_rest/_ftgs) 실행. 역당 3줄 출력. 사용: python s5_run.py 역..."""
import json, re, subprocess, sys
R = json.load(open('s5_pages.json', encoding='utf-8')); SP = '../stations.json'; S = json.load(open(SP, encoding='utf-8'))
def sets(F):  # 쪽 목록에서 4쪽 간격 세트 첫 쪽만 (인접쌍의 앞쪽)
    out = []
    for p in F:
        if not out or p - out[-1] >= 4: out.append(p)
    return out
def run(*a): return subprocess.run([sys.executable, 'claude/'+a[0], *a[1:]], cwd='..', capture_output=True, text=True, encoding='utf-8')
for s in sys.argv[1:]:
    r = R[s]; c = S[s]; pa = c['paths'] = {}
    if r['N'] and r['N'][0][0] >= .8: pa['N'] = r['N'][0][2]
    if r['F']: pa['FTGS'] = sets(r['F'])
    d = [k for k, _ in r['cab'] if k.startswith('+D')]
    if d: c['dcab'] = d[0][1:]
    json.dump(S, open(SP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    res = []
    if 'N' in pa:
        a = run('make_power_paths.py', '--station', s, 'power-paths.json'); b = run('make_power_paths_n_rest.py', '--station', s)
        res.append('N p.%d %s' % (pa['N'], 'ok' if a.returncode == 0 and b.returncode == 0 else 'FAIL ' + (a.stderr + b.stderr).strip().splitlines()[-1][:80]))
    else: res.append('N 해당없음(유사쪽 Jaccard<.8: %s)' % (r['N'][:1],))
    fs = ''
    if 'FTGS' in pa:
        f = run('make_power_paths_ftgs.py', '--station', s)
        L = [l for l in f.stdout.splitlines() if not l.startswith('parts')]
        ok = sum(' True ' in l for l in L); q = sum('?:' in l for l in L)
        fs = 'FTGS %s sameStructure %d/%d, ckt?=%d%s' % (pa['FTGS'], ok, len(L), q, '' if f.returncode == 0 else ' FAIL ' + f.stderr.strip().splitlines()[-1][:80])
    else: fs = 'FTGS 해당없음'
    print(s, '|', res[0], '\n ', fs, '\n  구조다름:', 'N' if 'N' not in pa or 'FAIL' in res[0] else '', 'FTGS' if fs.startswith('FTGS 해당') or 'FAIL' in fs or (L and ok < len(L)) else '', flush=True)
