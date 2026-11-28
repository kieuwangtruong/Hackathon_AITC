"""Pseudo-label Sign (class 9) on converted COCO images with an earlier model (COCO has no sign labels).

  python tools/coco/add_signs.py coco_yolo best.pt --conf 0.5
"""
import argparse, pathlib, sys
import numpy as np, cv2
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from nbcheck import polygon_problem
from ultralytics import YOLO

ap = argparse.ArgumentParser()
ap.add_argument('dir'); ap.add_argument('model'); ap.add_argument('--conf', type=float, default=0.5)
ap.add_argument('--classes', default='9')
a = ap.parse_args()
d = pathlib.Path(a.dir); m = YOLO(a.model); cls = [int(c) for c in a.classes.split(',')]
imgs = sorted((d / 'images').glob('coco_*.jpg')); added = 0
for i in range(0, len(imgs), 32):
    for r in m.predict([str(p) for p in imgs[i:i + 32]], conf=a.conf, classes=cls, imgsz=640, retina_masks=True, verbose=False):
        if r.masks is None: continue
        h, w = r.orig_shape; lab = d / 'labels' / (pathlib.Path(r.path).stem + '.txt')
        lines = [l for l in lab.read_text().splitlines() if l.strip()]
        taken = np.zeros((h, w), bool)
        for l in lines:
            p = (np.array(l.split()[1:], float).reshape(-1, 2) * [w, h]).astype(np.int32)
            cv2.fillPoly(taken.view(np.uint8), [p], 1)
        for k, mk in zip(r.boxes.cls.int().tolist(), r.masks.data.cpu().numpy() > 0.5):
            mk = mk & ~taken
            if mk.sum() < 64: continue
            cs, _ = cv2.findContours(mk.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            c = max(cs, key=cv2.contourArea)
            c = cv2.approxPolyDP(c, 1.0, True).reshape(-1, 2).astype(np.float64)
            if len(c) < 3: continue
            c[:, 0] /= w; c[:, 1] /= h; c = np.round(c.clip(0, 1), 5)
            if polygon_problem(c, w, h): continue
            lines.append(f'{k} ' + ' '.join(f'{v:.5f}' for v in c.reshape(-1))); taken |= mk; added += 1
        lab.write_text('\n'.join(lines) + '\n')
print('pseudo-labels added:', added)
