import logging
import tempfile
from pathlib import Path
from config.settings import binary
from core.video_probe import probe
from core.file_manager import publish
from utils.process import run, Cancelled

def convert(source, target, crf=18, cancel=None, progress=lambda p: None):
    if crf not in (18, 20, 23, 26):
        raise ValueError('CRF không hợp lệ.')
    target = Path(target)
    if target.exists():
        raise FileExistsError(f'File đã tồn tại: {target.name}')
    info = probe(source, cancel)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.videoconverter-', dir=target.parent) as folder:
        temp = Path(folder) / 'encoded.mp4'
        def update(line):
            if line.startswith('out_time_us='):
                try:
                    progress(min(94, int(float(line.split('=')[1]) / 1000000 / info.duration * 94)))
                except ValueError:
                    pass
        # Disable autorotation to preserve coded dimensions; FFmpeg carries display matrix.
        pixel = 'yuv420p' if info.width % 2 == 0 and info.height % 2 == 0 else 'yuv444p'
        args = [binary('ffmpeg'), '-hide_banner', '-nostdin', '-v', 'error', '-n',
            '-noautorotate', '-i', str(source), '-map', '0:V:0', '-map', '0:a?',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', str(crf), '-pix_fmt', pixel,
            '-fps_mode', 'passthrough', '-c:a', 'aac', '-b:a', '192k',
            '-movflags', '+faststart', '-progress', 'pipe:1', str(temp)]
        logging.info('Convert %s -> %s', source, target)
        run(args, cancel, update)
        out = probe(temp, cancel)
        if (out.width, out.height, out.audio_count) != (info.width, info.height, info.audio_count):
            raise RuntimeError('File xuất không khớp độ phân giải hoặc số luồng âm thanh.')
        if abs(out.duration-info.duration) > max(.5, info.duration*.01):
            raise RuntimeError('Thời lượng file xuất không khớp video gốc.')
        progress(96)
        run([binary('ffmpeg'), '-v', 'error', '-xerror', '-nostdin', '-i', str(temp),
             '-map', '0:v', '-map', '0:a?', '-f', 'null', '-'], cancel)
        if cancel and cancel.is_set():
            raise Cancelled()
        publish(temp, target)
        progress(100)
        return out
