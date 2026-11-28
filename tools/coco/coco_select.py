import json, collections, sys
from pycocotools.coco import COCO
OUR = {'person','bicycle','car','motorcycle','bus','truck','traffic light','stop sign'}
res = {}
for split in ['train2017','val2017']:
    c = COCO(f'coco/annotations/instances_{split}.json')
    name = {k: v['name'] for k, v in c.cats.items()}
    for iid, img in c.imgs.items():
        anns = [a for a in c.imgToAnns[iid] if name[a['category_id']] in OUR]
        if not anns: continue
        if any(a['iscrowd'] for a in anns): continue
        cnt = collections.Counter(name[a['category_id']] for a in anns if a['area'] > 150)
        veh = cnt['car']+cnt['bus']+cnt['truck']+cnt['motorcycle']+cnt['bicycle']+cnt['traffic light']
        if veh == 0: continue
        res[f'{split}/{img["file_name"]}'] = dict(cnt)
json.dump(res, open('coco/cands.json','w'))
tot = collections.Counter()
for v in res.values(): tot.update({k: 1 for k in v})
print(len(res), tot)
