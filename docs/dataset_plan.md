# Dataset plan v1 (RoboTaxi data-centric competition)

The model is fixed (`yolo26n-seg`, `imgsz=640`), so every point we gain comes from the data.
This document fixes how we label, how we validate, and which public data we pull in.
Items marked **GUESS** are my assumptions and still need a decision from the team.

## 1. Classes (fixed by the organizers, do not reorder)

| id | class | include | do not include / edge cases |
|---|---|---|---|
| 0 | Car | sedan, SUV, minivan, 7-seat, pickup, taxi, electric tourist cart, van ambulance, 9-15 seat vans | |
| 1 | Bus | buses and coaches with 16+ seats | 9-15 seat vans are Car |
| 2 | Truck | all trucks, tankers, dump trucks, fire trucks, tractor units | for a tractor unit, only the cabin + tractor body; the trailer is Other vehicle |
| 3 | Other vehicle | ba gac, xich lo, xe lam, construction machines, xe may cay, trailers and semi-trailers, anything that fits no other class | |
| 4 | Motorcycle | motorbike, scooter, 2-wheel e-scooter with **nobody seated** (parked or being walked) | |
| 5 | Motorcyclist | **one** instance covering the bike **and every person on it**, plus cargo they carry | never split the rider into Pedestrian |
| 6 | Bicycle | bicycle, e-bicycle with nobody on it | |
| 7 | Cyclist | **one** instance covering the bicycle and its rider | |
| 8 | Pedestrian | anyone not seated on a vehicle: walking, standing, sitting, children, people walking a bike | a person walking a bike = Pedestrian + Motorcycle/Bicycle |
| 9 | Sign | road signs, direction signs, roadwork signs: **sign face only** | never the pole |
| 10 | Traffic light | the **whole housing**, vehicle and pedestrian lights | not just the lit bulb |

Labeling rules we add on top (**GUESS**, change if the organizers' sample labels disagree):

- Occluded objects: label the visible part only, as one polygon if the visible part is connected. If an object is split into two visible pieces, use one polygon around the larger piece (YOLO-seg has one polygon per line, and multi-part instances are a known weak spot).
- Minimum size: skip objects smaller than about 8 x 8 px in the original image; at 640 they vanish anyway.
- Truncated by the image border: label what is visible.
- Reflections, posters, and vehicles on billboards: do not label.
- Back side of a sign: do not label (it has no face). **GUESS**
- Cargo on a motorbike (gas tanks, boxes, goods): part of the Motorcyclist mask.

We should check every rule against the organizers' sample data once we have it.

## 2. Label format

One `.txt` per image, with the same stem as the image. Each line is one instance:

```
<class_id> <x1> <y1> <x2> <y2> <x3> <y3> ...
```

Coordinates are normalized to `[0, 1]` by image width/height, at least 3 points. An image with no
objects gets an **empty** `.txt` (that is a useful negative). Zip layout:

```
dataset.zip
├── images/   (.jpg/.png)
├── labels/   (one .txt per image)
└── data.yaml (optional; template in configs/data.yaml)
```

`tools/check_labels.py` enforces this: class ids 0-10, even coord count, coords in range, a label
for every image. It also warns about 4-point rectangles, because a box pasted in as a polygon
trains the mask head on garbage.

## 3. Validation split

Goal: the val score should predict the private score. The private test set is presumably from
cameras, streets and times we never trained on (**GUESS**, the organizers have not said), so:

1. **Val is Vietnamese data only.** Public foreign datasets (Mapillary, IDD, BDD, COCO) go to train
   only (`--force-train` with a `source` column in the metadata CSV).
2. **Hold out whole groups, never single frames.** A group is a camera / video / location. Frames
   of one video are nearly identical; splitting them randomly leaks the answer into val.
   Near-duplicates across groups are found with a perceptual hash and merged into one group.
3. **Balance conditions.** Each time-of-day (and, if known, weather) stratum gets about 20% of its
   images in val, so night and rain are not missing from val by chance.
4. **Check class coverage.** The script warns if any of the 11 classes has zero val instances.
   Rare classes (Bicycle, Cyclist, Other vehicle, Bus) need their counts checked by hand.
5. **Freeze the split.** Once v1 is set, keep the same val list across rounds so scores are comparable.
   Add new data to train; only add to val in a new versioned split.

How to run:

```
python tools/check_labels.py --images datasets/v1/images --labels datasets/v1/labels
python tools/split_dataset.py --images datasets/v1/images --labels datasets/v1/labels \
    --meta datasets/v1/meta.csv --out splits/v1 --val-frac 0.2 --force-train mapillary,idd,bdd,coco
yolo segment train model=yolo26n-seg.pt data=splits/v1/data.yaml imgsz=640
```

`meta.csv` columns (all optional except `file`): `file, group, camera, location, time_of_day, weather, source`.
Without metadata, the group is the filename prefix before the frame number, and night is guessed
from brightness (threshold **GUESS**: mean grey < 70).

Suggested val size: 300-600 VN images from at least 8-10 groups (**GUESS**). Fewer groups make the
val score swing too much from one camera to the next.

## 4. Public datasets

Every dataset we use must be recorded in the report: name, link, license, number of images used,
and class mapping. Licenses below are from memory or a quick check and **must be confirmed on the
official page before use**.

| dataset | link | license (verify) | where / labels | why it helps | mapping to our 11 classes |
|---|---|---|---|---|---|
| Mapillary Vistas v2.0 | mapillary.com/dataset/vistas | CC BY-NC-SA 4.0 | worldwide street-level, includes SE Asia; instance masks | has `traffic-sign--front` (= sign face only) and traffic-light housings; riders as separate masks | car→0, bus→1, truck→2, caravan/trailer/other-vehicle/wheeled-slow→3, motorcycle (no rider)→4, motorcycle ∪ overlapping motorcyclist masks→5, bicycle→6, bicycle ∪ bicyclist→7, person→8, traffic-sign--front→9, traffic-light--*→10; drop sign back/pole |
| IDD Segmentation (India Driving Dataset) | idd.insaan.iiit.ac.in | IDD research-use terms | Indian roads; polygons | dense two-wheelers, autorickshaws, chaotic traffic: closest public match to VN | car→0, bus→1, truck→2, autorickshaw/caravan/trailer/vehicle-fallback→3, motorcycle (no rider)→4, motorcycle ∪ rider→5, bicycle→6, bicycle ∪ rider→7, person→8, traffic sign→9, traffic light→10 |
| BDD100K instance seg (10K) | bdd-data.berkeley.edu | BDD100K license (research) | US dashcam; masks | night, rain, dusk | car→0, bus→1, truck→2, motorcycle→4/5 and bicycle→6/7 by merging with overlapping rider, pedestrian→8, train dropped; signs/lights only boxes → need SAM 2 |
| COCO 2017 | cocodataset.org | annotations CC BY 4.0, images Flickr terms | general photos; masks | lots of people + motorbikes | car→0, bus→1, truck→2, motorcycle→4/5 and bicycle→6/7 with person merge, person (not on vehicle)→8, stop sign→9, traffic light→10 |
| Zalo AI 2020 Traffic Sign | datasetninja.com/zalo-traffic-sign | not stated | ~4.5k VN Street View images; boxes | Vietnamese signs | all 7 sign types→9 after SAM 2 box→mask |
| VN Vehicle Tracking (VnTraffic) | zenodo.org/records/18195750 | CC BY 4.0 | VN traffic video; boxes with track ids | real VN motorbike density | sample sparse frames, SAM 2 → masks, motorbike → 4/5 by hand |
| Roboflow Universe VN projects (e.g. vn_traffic) | universe.roboflow.com/projectxla/vn_traffic | per project, check each | VN cameras; mostly boxes | extra VN scenes for pre-labeling | per project |

Skipped for now: UIT-ADrone (drone view, does not match a car camera), VN-Traffic-Instance-Segmentation-YOLO11
on GitHub (data not published), Cityscapes (German, few two-wheelers, non-commercial).

Main risks: Vistas, IDD and BDD are non-commercial/research licenses. That should be fine for a
competition, but **the organizers should confirm**. Foreign data can also hurt: their "car" and
"truck" look different, and none of them have ba gac or xe lam. Add them in measured amounts
and keep only what improves the VN val score.

## 5. Pre-labeling with a large model, then human correction

1. Collect VN frames (own dashcam/phone video, VN YouTube traffic footage if the license allows, VN
   public sets). Sample about 1 frame per 2-3 s per video so frames differ.
2. Pre-label with a big model: COCO-pretrained `yolo11x-seg` / large `yolo26-seg` for vehicles and
   people, and Grounding DINO + SAM 2 with text prompts for "traffic sign", "traffic light",
   "cyclo", "three-wheeled cargo motorbike".
3. Convert to our classes automatically:
   - person whose box overlaps a motorcycle (person's lower half inside bike box) → union of masks = Motorcyclist (5); same for bicycle → Cyclist (7)
   - lone motorcycle/bicycle → 4/6; remaining people → Pedestrian (8)
   - bus with small size (9-15 seats) → Car: cannot be automated, flag for review
4. Fix by hand in CVAT or Label Studio (polygon mode, with SAM assist). Reviewers check only the
   classes the model gets wrong most (rare vehicles, merged riders, signs).
5. Re-run `check_labels.py`, then train, look at val errors, and label more of what fails (active learning).

## 6. Hard scenes to target

Night, rain, dense motorbike crowds, heavy occlusion, glare, wet roads, and rare classes (ba gac,
xich lo, xe lam, construction vehicles, bicycles). Track their counts in `split_report.json`.
Augmentations worth trying in training config (they do not change the model): mosaic, copy-paste
(good for rare classes in seg), HSV/brightness for night, and blur.

## 7. Open questions

- Do the organizers provide training data, or only the small sample? Does it come with camera, location or time metadata?
- Are research-only licenses (Vistas, IDD, BDD) allowed in the competition?
- Is the private test set from dashcams, CCTV or both? It changes which public data matters most.
