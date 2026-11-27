import json, os, concurrent.futures as cf
from remotezip import RemoteZip
ch = json.load(open('coco/chosen.json'))
os.makedirs('coco/raw', exist_ok=True)
by = {}
for k in ch: by.setdefault(k.split('/')[0], []).append(k)
def job(split, names):
    import time
    for k in names:
        out = 'coco/raw/' + k.replace('/', '_')
        for attempt in range(5):
            if os.path.exists(out): break
            try:
                z = RemoteZip(f'https://s3.amazonaws.com/fast-ai-coco/{split}.zip')
                data = z.read(k); open(out + '.part', 'wb').write(data); os.replace(out + '.part', out)
            except Exception as e:
                print('retry', k, e); time.sleep(2 * (attempt + 1))
tasks = []
with cf.ThreadPoolExecutor(8) as ex:
    for split, ks in by.items():
        for i in range(8):
            tasks.append(ex.submit(job, split, ks[i::8]))
    for t in tasks: t.result()
print('done', len(os.listdir('coco/raw')))
