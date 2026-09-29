"""S5 검증: 역별 N 경로 세그먼트 수 + ckt '?' 회로(단자 있는 것만 = 추출 실패 후보)."""
import json
P = json.load(open('power-paths.json', encoding='utf-8'))
for st in ('SIN1', 'EUL', 'HON', 'SNU1', 'SNU2', 'SOL', 'SON1', 'SON2', 'SPO1', 'SPO2', 'YAN'):
    r = [(x['id'].replace('PWR_SICAS_N_', '').replace('_' + st, ''), sum(len(s['segments']) for s in x['steps'])) for x in P if x['station'] == st and 'SICAS_N' in x['id']]
    print(st, r)
for x in P:
    if x['id'].startswith('PWR_FTGS') and x['station'] in ('HON', 'SCD', 'SNU1', 'SNU2', 'SOL', 'SON1', 'SON2', 'SPO1', 'SPO2', 'YAN'):
        for pn, i in x['steps'][0]['instances'].items():
            for c in i['circuits']:
                if c['ckt'] == '?': print('ckt?', x['station'], pn, c['fuse'], c['term'])
