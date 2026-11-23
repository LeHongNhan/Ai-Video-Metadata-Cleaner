import subprocess
import threading
import time

class Cancelled(Exception):
    pass

def run(args, cancel=None, line=None, timeout=None):
    cancel = cancel or threading.Event()
    if cancel.is_set():
        raise Cancelled()
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding='utf-8', errors='replace',
        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    lines = []
    def read():
        for value in process.stdout:
            lines.append(value)
            if line:
                line(value.strip())
    reader = threading.Thread(target=read, daemon=True)
    reader.start()
    start = time.monotonic()
    try:
        while process.poll() is None:
            if cancel.wait(.08):
                raise Cancelled()
            if timeout and time.monotonic() - start > timeout:
                raise RuntimeError('Quá thời gian đọc video. Kiểm tra file hoặc ổ đĩa.')
        reader.join()
        if cancel.is_set():
            raise Cancelled()
        result = ''.join(lines)
        if process.returncode:
            raise RuntimeError(result[-6000:] or 'FFmpeg không xử lý được file.')
        return result
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        reader.join(timeout=3)
        process.stdout.close()
