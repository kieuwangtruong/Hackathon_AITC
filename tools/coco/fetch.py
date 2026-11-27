import json, os, concurrent.futures as cf
from remotezip import RemoteZip
ch = json.load(open('coco/chosen.json'))
os.makedirs('coco/raw', exist_ok=True)
by = {}
for k in ch: by.setdefault(k.split('/')[0], []).append(k)
def job(split, names):
    z = RemoteZip(f'https://s3.amazonaws.com/fast-ai-coco/{split}.zip')
    for k in names:
        out = 'coco/raw/' + k.replace('/', '_')
        if not os.path.exists(out):
            open(out, 'wb').write(z.read(k))
tasks = []
with cf.ThreadPoolExecutor(8) as ex:
    for split, ks in by.items():
        for i in range(8):
            tasks.append(ex.submit(job, split, ks[i::8]))
    for t in tasks: t.result()
print('done', len(os.listdir('coco/raw')))
