#!/usr/bin/env python3
"""Build du_lieu.zip for one training round, from the repo alone (runs on Colab).

VN images: datasets/pov_hard_ez + datasets/pov_med, val = configs/val_v1.txt (frozen),
resized from the squashed 640x640 back to 16:9 (640x360). Train VN images are repeated.
COCO: tools/coco pipeline, downloaded from the fast.ai S3 mirror.

  python tools/build_round.py --out du_lieu.zip --vn-repeat 3 --quota '{"moto":320}'
"""
import argparse, json, os, pathlib, shutil, subprocess, sys, zipfile
import cv2

ROOT = pathlib.Path(__file__).resolve().parents[1]
ANN = 'https://s3.amazonaws.com/fast-ai-coco/annotations_trainval2017.zip'


def vn_pairs():
    for img in sorted((ROOT / 'datasets').glob('*/images/**/*.jpg')):
        parts = list(img.parts); i = len(parts) - 1 - parts[::-1].index('images'); parts[i] = 'labels'
        yield img, pathlib.Path(*parts).with_suffix('.txt')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--work', default='/content/round_work')
    ap.add_argument('--vn-repeat', type=int, default=3)
    ap.add_argument('--quota', default='{}', help='COCO quota overrides, JSON')
    ap.add_argument('--no-coco', action='store_true')
    ap.add_argument('--coco-val', type=int, default=0, help='COCO images moved to val (bigger val = steadier best.pt pick)')
    ap.add_argument('--no-unsquash', action='store_true')
    ap.add_argument('--sign-model', help='earlier best.pt: pseudo-label Sign on COCO images')
    ap.add_argument('--sign-conf', type=float, default=0.5)
    a = ap.parse_args()
    work = pathlib.Path(a.work); work.mkdir(parents=True, exist_ok=True)
    val = set((ROOT / 'configs/val_v1.txt').read_text().split())
    ds = work / 'ds'
    shutil.rmtree(ds, ignore_errors=True)
    for s in ('train', 'val'):
        (ds / 'images' / s).mkdir(parents=True); (ds / 'labels' / s).mkdir(parents=True)
    n = {'train': 0, 'val': 0}
    for img, lab in vn_pairs():
        split = 'val' if img.name in val else 'train'
        im = cv2.imread(str(img))
        if not a.no_unsquash and im.shape[0] == im.shape[1]:
            im = cv2.resize(im, (im.shape[1], im.shape[1] * 9 // 16), interpolation=cv2.INTER_AREA)
        reps = 1 if split == 'val' else a.vn_repeat
        for k in range(reps):
            stem = img.stem if reps == 1 else f'{img.stem}_x{k + 1}'
            cv2.imwrite(str(ds / 'images' / split / f'{stem}.jpg'), im, [cv2.IMWRITE_JPEG_QUALITY, 95])
            shutil.copy(lab, ds / 'labels' / split / f'{stem}.txt'); n[split] += 1
    if not a.no_coco:
        env = dict(os.environ, QUOTA=a.quota)
        if not (work / 'coco/annotations').exists():
            (work / 'coco').mkdir(exist_ok=True)
            subprocess.check_call(['curl', '-sL', '-o', 'coco/ann.zip', ANN], cwd=work)
            subprocess.check_call(['unzip', '-q', '-o', 'ann.zip'], cwd=work / 'coco')
        for script in ('coco_select.py', 'pick.py', 'fetch.py'):
            if script == 'coco_select.py' and (work / 'coco/cands.json').exists():
                continue
            subprocess.check_call([sys.executable, '-u', str(ROOT / 'tools/coco' / script)], cwd=work, env=env)
        shutil.rmtree(work / 'coco_yolo', ignore_errors=True)
        subprocess.check_call([sys.executable, '-u', str(ROOT / 'tools/coco/convert.py'), str(work / 'coco_yolo')], cwd=work)
        if a.sign_model:
            subprocess.check_call([sys.executable, '-u', str(ROOT / 'tools/coco/add_signs.py'), str(work / 'coco_yolo'), a.sign_model, '--conf', str(a.sign_conf)])
        import hashlib
        cimgs = sorted((work / 'coco_yolo/images').iterdir(), key=lambda f: hashlib.md5(f.name.encode()).hexdigest())
        for i, f in enumerate(cimgs):
            split = 'val' if i < a.coco_val else 'train'
            shutil.copy(f, ds / 'images' / split / f.name)
            shutil.copy(work / 'coco_yolo/labels' / f'{f.stem}.txt', ds / 'labels' / split / f'{f.stem}.txt'); n[split] += 1
    with zipfile.ZipFile(a.out, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(ds.rglob('*')):
            if f.is_file():
                zf.write(f, f.relative_to(ds))
    print(json.dumps({'out': a.out, **n}))


if __name__ == '__main__':
    main()
