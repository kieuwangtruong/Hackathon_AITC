# COCO → 11 lớp (bộ dữ liệu v2)

Thêm ảnh đường phố từ COCO 2017 để vá các lớp yếu (Người đi bộ, Xe đạp, Người đi xe đạp, Xe máy, Đèn giao thông).

```bash
pip install pycocotools opencv-python-headless remotezip
mkdir -p coco && cd coco && curl -LO https://s3.amazonaws.com/fast-ai-coco/annotations_trainval2017.zip && unzip annotations_trainval2017.zip && cd ..
python tools/coco/coco_select.py   # ảnh có xe/đèn, bỏ ảnh có nhãn crowd
python tools/coco/pick.py          # chọn 1000 ảnh theo hạn mức, seed 48
python tools/coco/fetch.py         # tải đúng các ảnh đã chọn (đọc từng phần zip)
python tools/coco/convert.py coco_yolo
```

Ánh xạ: car→Car, bus→Bus, truck→Truck, motorcycle→Motorcycle, bicycle→Bicycle, person→Pedestrian, traffic light→Traffic light, stop sign→Sign.
Người ngồi trên xe máy/xe đạp được gộp với xe thành một đối tượng Motorcyclist/Cyclist. Người nằm >50% trong mask ô tô/bus/tải bị bỏ (người trong xe).
Mask chồng nhau: vật nhỏ hơn giữ điểm ảnh. Bỏ vật < 64 px ở thang 640. Ảnh thu về cạnh dài 640.
Đa giác được kiểm tra bằng đúng hàm của notebook chung (`nbcheck.py`).

Lưu ý: COCO không gán biển báo (trừ biển STOP), nên tập train v2 lặp ảnh Việt Nam 3 lần để giữ trọng số.
