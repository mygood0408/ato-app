# 연결된 페이지만 kb_pages/<doc>/p0024.webp 로 축소 복사 (전체 복사 금지)
import json,os,collections
from PIL import Image
SRC=r'C:\Users\김영추\Desktop\2호선 PDF 자료\PDF_Knowledge_Base\02_page_images'
OUT='kb_pages'
need=collections.defaultdict(set)
def walk(o):
    if isinstance(o,dict):
        if 'doc' in o and 'pages' in o: need[o['doc']].update(o['pages'])
        if 'kbDoc' in o and 'pdfPages' in o: need[o['kbDoc']].update(o['pdfPages'])
        for v in o.values(): walk(v)
    elif isinstance(o,list):
        for v in o: walk(v)
for f in ('board-info.json','fault-cases.json','power-paths.json'): walk(json.load(open(f,encoding='utf-8')))
n=miss=0
for d,ps in need.items():
    os.makedirs(f'{OUT}/{d}',exist_ok=True)
    for p in ps:
        s=f'{SRC}/{d}/page_{p:04d}.png'
        if not os.path.exists(s): miss+=1; print('missing',s); continue
        im=Image.open(s).convert('RGB'); im.thumbnail((1400,2000))
        im.save(f'{OUT}/{d}/p{p:04d}.webp',quality=72); n+=1
print(n,'saved',miss,'missing')
