import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'VideoConverter'
SUPPORTED = {'.mp4', '.mov', '.mkv', '.avi', '.webm', '.m4v'}

def binary(name):
    base = Path(getattr(sys, '_MEIPASS', ROOT))
    candidates = [base / 'tools' / f'{name}.exe']
    candidates += list((base / 'tools').glob(f'*/bin/{name}.exe'))
    for path in candidates:
        if path.is_file():
            return str(path)
    found = shutil.which(name)
    if found:
        return found
    raise RuntimeError(f'Thiếu {name}.exe. Đặt FFmpeg và FFprobe trong thư mục tools hoặc PATH.')

def setup_dirs():
    for name in ('input', 'output', 'temp', 'logs'):
        (DATA / name).mkdir(parents=True, exist_ok=True)
