import json, os, random
c = json.load(open('coco/cands.json'))
random.seed(48)
keys = sorted(c); random.shuffle(keys)
g = lambda k, n: c[k].get(n, 0)
street = lambda k: g(k,'car')+g(k,'bus')+g(k,'truck')+g(k,'traffic light') > 0
quota = [('moto', 320, lambda k: g(k,'motorcycle') and street(k)),
         ('bike', 280, lambda k: g(k,'bicycle') and street(k)),
         ('ped', 220, lambda k: g(k,'person') >= 2 and street(k) and (g(k,'traffic light') or g(k,'car')>=2)),
         ('tl', 120, lambda k: g(k,'traffic light') >= 2),
         ('stop', 60, lambda k: g(k,'stop sign') and street(k)),
         ('bus', 0, lambda k: g(k,'bus')),
         ('truck', 0, lambda k: g(k,'truck'))]
# QUOTA='{"moto":320,...}' overrides the counts above
over = json.loads(os.environ.get('QUOTA', '{}'))
quota = [(n, over.get(n, q), f) for n, q, f in quota]
chosen = {}
for name, n, f in quota:
    got = 0
    for k in keys:
        if got >= n: break
        if k in chosen or not f(k): continue
        chosen[k] = name; got += 1
    print(name, got)
json.dump(chosen, open('coco/chosen.json','w'), indent=0)
print(len(chosen))
