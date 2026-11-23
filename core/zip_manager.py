import tempfile
import zipfile
from pathlib import Path
from core.file_manager import publish
from utils.process import Cancelled

def create_zip(files, target, cancel=None, progress=lambda p: None):
    files = [Path(f) for f in files]
    target = Path(target)
    if not files:
        raise ValueError('Chưa có video hoàn thành để đóng gói.')
    if target.exists():
        raise FileExistsError('File ZIP đã tồn tại. Hãy chọn tên khác.')
    if len({p.name.casefold() for p in files}) != len(files):
        raise ValueError('Các video có tên trùng nhau; không thể giữ tên trong ZIP.')
    total = sum(p.stat().st_size for p in files)
    done = 0
    with tempfile.TemporaryDirectory(prefix='.videoconverter-zip-', dir=target.parent) as folder:
        temp = Path(folder) / 'archive.zip'
        with zipfile.ZipFile(temp, 'w', compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
            for path in files:
                with path.open('rb') as source, archive.open(path.name, 'w', force_zip64=True) as dest:
                    while chunk := source.read(1024*1024):
                        if cancel and cancel.is_set():
                            raise Cancelled()
                        dest.write(chunk)
                        done += len(chunk)
                        progress(int(done/max(total, 1)*99))
        if cancel and cancel.is_set():
            raise Cancelled()
        publish(temp, target)
    progress(100)
