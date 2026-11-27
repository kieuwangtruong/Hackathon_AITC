# Kaggle runner (GPU T4, Internet on). In a Kaggle notebook cell:
#   !git clone -q -b claude/project-thread-0ms80x https://github.com/kieuwangtruong/Hackathon_AITC /kaggle/working/repo_r
#   ROUND = 'v5'
#   exec(open('/kaggle/working/repo_r/kaggle/run_round.py').read())
# Builds the round's data (colab/rounds.json), then runs the official notebook colab/shared.ipynb cell by cell.
# Results: /kaggle/working/out/<ROUND>/submission.zip, run_report.json, best.pt (Output panel).
import json, os, re, shutil, subprocess

_R = '/kaggle/working/repo_r'


def _run(cmd):
    pr = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in pr.stdout:
        if 'index created' not in line and 'loading annotations' not in line:
            print(line, end='', flush=True)
    if pr.wait():
        raise RuntimeError(f'failed: {cmd}')


_cfg = json.load(open(f'{_R}/colab/rounds.json'))[ROUND]
_args = _cfg['args'].replace('/content/repo_r', _R)
_prev_best = f'{_R}/weights/{_cfg["prev"]}_best.pt'
if os.path.exists(_prev_best):
    _args = _args.replace('{PREV_BEST}', _prev_best)
else:
    _args = re.sub(r'--sign-(model|conf) \S+', '', _args)
    print('No earlier best.pt: building without sign pseudo-labels')
_run('pip install -q pycocotools remotezip')
_zip = f'/kaggle/temp/du_lieu_{ROUND}.zip'
os.makedirs('/kaggle/temp', exist_ok=True)
if not os.path.exists(_zip):
    _run(f'python -u {_R}/tools/build_round.py --out {_zip} --work /kaggle/temp/round_work {_args}')
shutil.rmtree('/kaggle/temp/round_work', ignore_errors=True)

_OUT = f'/kaggle/working/out/{ROUND}'
os.makedirs(_OUT, exist_ok=True)
_cells = [''.join(c['source']) for c in json.load(open(f'{_R}/colab/shared.ipynb'))['cells'] if c['cell_type'] == 'code']
for _src in _cells:
    exec(_src, globals())
    if 'TEAM_ID = 48' in _src:  # team parameters cell: point it at this round
        DATASET_PATH = _zip
        EPOCHS = _cfg['epochs']
        DRIVE_OUTPUT_DIR = _OUT
        WORK_DIR = '/kaggle/temp/work'
        PARAMS['EPOCHS'] = EPOCHS
        print(f'Round {ROUND}: data {DATASET_PATH}, epochs {EPOCHS}, results -> {_OUT}')
print('Xong:', os.listdir(_OUT))
