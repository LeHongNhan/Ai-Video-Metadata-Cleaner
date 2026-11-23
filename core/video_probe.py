import json
from dataclasses import dataclass
from pathlib import Path
from config.settings import binary
from utils.process import run

@dataclass
class VideoInfo:
    width: int
    height: int
    duration: float
    size: int
    audio_count: int
    fps: str

def probe(path, cancel=None):
    data = json.loads(run([binary('ffprobe'), '-v', 'error', '-show_format',
        '-show_streams', '-of', 'json', str(path)], cancel, timeout=60))
    videos = [s for s in data['streams'] if s['codec_type'] == 'video'
              and not s.get('disposition', {}).get('attached_pic')]
    if not videos:
        raise ValueError('File không có luồng hình ảnh video.')
    v = videos[0]
    duration = float(data.get('format', {}).get('duration') or v.get('duration') or 0)
    if duration <= 0:
        raise ValueError('Không đọc được thời lượng video.')
    return VideoInfo(v['width'], v['height'], duration, Path(path).stat().st_size,
        sum(s['codec_type'] == 'audio' for s in data['streams']), v.get('avg_frame_rate', '0/0'))
