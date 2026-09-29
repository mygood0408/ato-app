"""일반화 회귀 확인: git HEAD 스크립트(old) vs 작업본(new)을 임시 폴더에서 SIN1/SIN2 로 돌려 산출물 diff.
사용: python claude/s4_regress.py  -> 각 파일 'same'/'DIFF' 한 줄."""
import subprocess, shutil, os, sys, tempfile, filecmp
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SC = ['make_power_paths.py', 'make_power_paths_n_rest.py', 'make_power_paths_ftgs.py', 'sync_related_drawings.py']
D = tempfile.mkdtemp()
def setup(tag):
    d = os.path.join(D, tag); os.makedirs(d + '/claude')
    for f in ('power-paths.json', 'board-info.json', '장비구성뷰_v3_시안.html', 'stations.json'): shutil.copy(os.path.join(R, f), d)
    for f in SC + ['stn.py']:
        if tag == 'old' and f != 'stn.py':
            open(d + '/claude/' + f, 'wb').write(subprocess.check_output(['git', '-C', R, 'show', 'HEAD:claude/' + f]))
        elif os.path.exists(os.path.join(R, 'claude', f)): shutil.copy(os.path.join(R, 'claude', f), d + '/claude/')
    return d
def run(d, tag):
    py = lambda s, *a, **e: subprocess.run([sys.executable, d + '/claude/' + s, *a], cwd=d, env={**os.environ, **e}, capture_output=True, text=True, encoding='utf-8')
    new = tag == 'new'
    for s in ('SIN1', 'SIN2'):
        py('make_power_paths.py', 'p_%s.json' % s, **({} if new and False else {'STN': s}))
        py('make_power_paths_n_rest.py', **{'STN': s})
        py('make_power_paths_ftgs.py', s)
    py('sync_related_drawings.py')
o, n = setup('old'), setup('new')
for tag, d in (('old', o), ('new', n)): run(d, tag)
bad = 0
for f in ('p_SIN1.json', 'p_SIN2.json', 'power-paths.json', 'board-info.json', '장비구성뷰_v3_시안.html'):
    ok = filecmp.cmp(os.path.join(o, f), os.path.join(n, f), shallow=False); bad += not ok
    print(f, 'same' if ok else 'DIFF')
print('diff 0' if not bad else 'DIFF FOUND', D)
