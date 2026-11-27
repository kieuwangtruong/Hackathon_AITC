# Run inside colab/shared.ipynb right after the "Tham số của đội" cell:
#   ROUND = 'v4'   (settings for each round are in colab/rounds.json)
#   !git -C /content/repo_r pull -q || git clone -q -b claude/project-thread-0ms80x https://github.com/kieuwangtruong/Hackathon_AITC /content/repo_r
#   exec(open('/content/repo_r/colab/round_cell.py').read())
# Archives the previous run's outputs to ket_qua/<PREV>, builds this round's zip, points the notebook at it.
import os, shutil, subprocess, json


def _run(cmd):
    pr = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in pr.stdout:
        if 'index created' not in line and 'loading annotations' not in line:
            print(line, end='', flush=True)
    if pr.wait():
        raise RuntimeError(f'failed: {cmd}')


_cfg = json.load(open('/content/repo_r/colab/rounds.json'))[ROUND]
PREV, BUILD_ARGS, EPOCHS_R = _cfg['prev'], _cfg['args'], _cfg['epochs']
from google.colab import drive
drive.mount('/content/drive')
_KQ = '/content/drive/MyDrive/Hackathon_AITC/ket_qua'
_prev = f'{_KQ}/{PREV}'
os.makedirs(_prev, exist_ok=True)
for _f in ('submission.zip', 'run_report.json'):
    if os.path.exists(f'{_KQ}/{_f}'):
        shutil.move(f'{_KQ}/{_f}', f'{_prev}/{_f}')
if os.path.exists('/content/work/runs/train/weights/best.pt') and not os.path.exists(f'{_prev}/best.pt'):
    shutil.copy('/content/work/runs/train/weights/best.pt', f'{_prev}/best.pt')
_run('pip install -q pycocotools remotezip ultralytics==8.4.214')
_zip = f'/content/du_lieu_{ROUND}.zip'
_args = BUILD_ARGS.replace('{PREV_BEST}', f'{_prev}/best.pt')
_run(f'python -u /content/repo_r/tools/build_round.py --out {_zip} --work /content/round_work {_args}')
shutil.copy(_zip, f'/content/drive/MyDrive/Hackathon_AITC/datasets/du_lieu_{ROUND}.zip')
shutil.rmtree('/content/work/dataset', ignore_errors=True)
shutil.rmtree('/content/work/raw', ignore_errors=True)
DATASET_PATH = _zip
DRIVE_OUTPUT_DIR = f'{_KQ}/{ROUND}'
os.makedirs(DRIVE_OUTPUT_DIR, exist_ok=True)
EPOCHS = EPOCHS_R
PARAMS['EPOCHS'] = EPOCHS
print(f'Round {ROUND}: data {DATASET_PATH}, results -> {DRIVE_OUTPUT_DIR}, epochs {EPOCHS}; previous run archived in {_prev}')
