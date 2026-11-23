"""Explicit offline smoke test for the packaged executable."""
import json
import tempfile
import zipfile
from pathlib import Path
from config.settings import binary
from core.video_processor import convert
from core.zip_manager import create_zip
from utils.process import run

def self_test(report):
    with tempfile.TemporaryDirectory(prefix='video-converter-test-') as folder:
        root = Path(folder)
        source, target = root/'input.mp4', root/'output.mp4'
        run([binary('ffmpeg'), '-v','error','-f','lavfi','-i',
             'testsrc2=size=128x96:rate=24:duration=0.5', '-c:v','libx264', str(source)])
        info = convert(source, target)
        create_zip([target], root/'result.zip')
        with zipfile.ZipFile(root/'result.zip') as archive:
            assert archive.testzip() is None
            assert archive.namelist() == ['output.mp4']
        Path(report).write_text(json.dumps({'ok': True, 'width': info.width,
            'height': info.height, 'ffmpeg': binary('ffmpeg'), 'ffprobe': binary('ffprobe')}, indent=2), encoding='utf-8')
