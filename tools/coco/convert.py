"""COCO 2017 -> our 11 classes (YOLO-seg). Riders merged with their bike into one instance."""
import json, os, sys, collections
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from nbcheck import polygon_problem
from pycocotools.coco import COCO
OUT = sys.argv[1]
ch = json.load(open('coco/chosen.json'))
os.makedirs(f'{OUT}/images', exist_ok=True); os.makedirs(f'{OUT}/labels', exist_ok=True)
MAP = {'car': 0, 'bus': 1, 'truck': 2, 'motorcycle': 4, 'bicycle': 6, 'person': 8, 'traffic light': 10, 'stop sign': 9}
stats = collections.Counter(); dropped = collections.Counter()

def iob(p, b):  # intersection / area of p (bboxes xywh)
    x1, y1 = max(p[0], b[0]), max(p[1], b[1]); x2 = min(p[0]+p[2], b[0]+b[2]); y2 = min(p[1]+p[3], b[1]+b[3])
    return max(0, x2-x1)*max(0, y2-y1) / max(1e-6, p[2]*p[3])

def is_rider(p, b):
    px = p[0] + p[2]/2
    return (iob(p, b) >= 0.15 and b[0] - 0.1*b[2] <= px <= b[0] + 1.1*b[2]
            and p[1] < b[1] + 0.3*b[3] and p[1] + p[3] > b[1] + 0.25*b[3])

def mask_to_poly(m, min_area, eps=1.0, merge=True):
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cs = [cv2.approxPolyDP(c, eps, True).reshape(-1, 2) for c in cs]
    cs = [c for c in cs if len(c) >= 3 and cv2.contourArea(c.astype(np.float32)) >= 8]
    if not cs: return None
    cs.sort(key=lambda c: -cv2.contourArea(c.astype(np.float32)))
    if sum(cv2.contourArea(c.astype(np.float32)) for c in cs) < min_area: return None
    poly = list(map(tuple, cs[0]))
    for c in (cs[1:] if merge else []):
        if cv2.contourArea(c.astype(np.float32)) < 0.05 * cv2.contourArea(cs[0].astype(np.float32)): continue
        A = np.array(poly); d = ((A[:, None, :] - c[None, :, :])**2).sum(-1)
        i, j = np.unravel_index(d.argmin(), d.shape)
        part = list(map(tuple, np.roll(c, -j, axis=0))) + [tuple(c[j])]
        poly = poly[:i+1] + part + poly[i:]
    return np.array(poly, dtype=np.float32)

cocos = {}
for k in sorted(ch):
    split, fn = k.split('/')
    if split not in cocos: cocos[split] = COCO(f'coco/annotations/instances_{split}.json')
    c = cocos[split]; iid = int(fn[:-4]); info = c.imgs[iid]
    src = 'coco/raw/' + k.replace('/', '_')
    if not os.path.exists(src): dropped['missing'] += 1; continue
    H, W = info['height'], info['width']
    anns = [a for a in c.imgToAnns[iid] if c.cats[a['category_id']]['name'] in MAP and not a['iscrowd']]
    cls = [MAP[c.cats[a['category_id']]['name']] for a in anns]
    masks = [c.annToMask(a).astype(bool) for a in anns]
    bikes = [i for i, k_ in enumerate(cls) if k_ in (4, 6)]
    owner = {}
    for i, k_ in enumerate(cls):
        if k_ != 8: continue
        best = max(bikes, key=lambda b: iob(anns[i]['bbox'], anns[b]['bbox']), default=None)
        if best is not None and is_rider(anns[i]['bbox'], anns[best]['bbox']): owner[i] = best
    insts = []  # (cls, mask)
    for b in bikes:
        riders = [i for i, o in owner.items() if o == b]
        m = masks[b].copy()
        for r in riders: m |= masks[r]
        insts.append((cls[b] + 1 if riders else cls[b], m))
    veh = [masks[i] for i, k_ in enumerate(cls) if k_ in (0, 1, 2)]
    for i, k_ in enumerate(cls):
        if k_ in (4, 6) or i in owner: continue
        if k_ == 8 and veh and any((masks[i] & v).sum() > 0.5 * masks[i].sum() for v in veh):
            dropped['person_in_vehicle'] += 1; continue
        insts.append((k_, masks[i]))
    # no overlap: bigger first, smaller (usually in front) overwrites
    s = 640 / max(H, W); nh, nw = round(H*s), round(W*s)
    order = sorted(range(len(insts)), key=lambda i: -insts[i][1].sum())
    idmap = np.full((H, W), -1, np.int32)
    for i in order: idmap[insts[i][1]] = i
    lines = []
    for i in range(len(insts)):
        m = cv2.resize((idmap == i).astype(np.uint8), (nw, nh), interpolation=cv2.INTER_NEAREST)
        poly = None
        for eps, merge in ((1.0, True), (1.0, False), (2.0, False), (0.7, False), (3.0, False), ('hull', False)):
            if eps == 'hull':
                p = mask_to_poly(m, 64, 1.0, False)
                p = None if p is None else cv2.convexHull(p).reshape(-1, 2); dropped['hull'] += p is not None
            else:
                p = mask_to_poly(m, 64, eps, merge)
            if p is None: break
            p = p.copy(); p[:, 0] /= nw; p[:, 1] /= nh; p = np.round(p.clip(0, 1), 5)
            if polygon_problem(p.astype(np.float64), nw, nh) is None: poly = p; break
            dropped['retry'] += 1
        if poly is None: dropped['tiny_or_bad'] += 1; continue
        lines.append(f"{insts[i][0]} " + ' '.join(f'{v:.5f}' for v in poly.reshape(-1)))
        stats[insts[i][0]] += 1
    img = cv2.imread(src); img = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA)
    stem = f'coco_{fn[:-4]}'
    cv2.imwrite(f'{OUT}/images/{stem}.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    open(f'{OUT}/labels/{stem}.txt', 'w').write('\n'.join(lines) + ('\n' if lines else ''))
names = ['Car','Bus','Truck','Other vehicle','Motorcycle','Motorcyclist','Bicycle','Cyclist','Pedestrian','Sign','Traffic light']
print({names[k]: v for k, v in sorted(stats.items())}, dict(dropped))
json.dump({names[k]: v for k, v in sorted(stats.items())}, open(f'{OUT}/stats.json', 'w'))
