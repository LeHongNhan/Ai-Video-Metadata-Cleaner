import hashlib
import json
import threading
import zipfile
from pathlib import Path
import pytest
from config.settings import binary
from core.file_manager import output_name, plan_outputs
from core.video_processor import convert
from core.video_probe import probe
from core.zip_manager import create_zip
from utils.process import run, Cancelled

@pytest.fixture(scope='module')
def samples(tmp_path_factory):
    root = tmp_path_factory.mktemp('videos')
    for name, audio, fps in [('silent', False, '24'), ('sound', True, '30000/1001')]:
        args = [binary('ffmpeg'), '-v', 'error', '-f', 'lavfi', '-i', f'testsrc2=size=160x120:rate={fps}:duration=1.5']
        if audio:
            args += ['-f', 'lavfi', '-i', 'sine=frequency=440:duration=1.5', '-map', '0:v', '-map', '1:a', '-map', '1:a']
        args += ['-c:v', 'libx264', '-c:a', 'aac', str(root / (name+'.mp4'))]
        run(args)
    (root/'broken.mp4').write_bytes(b'corrupted video')
    return root

def test_names(tmp_path):
    assert output_name('video01.mov', '') == 'video01-clean.mp4'
    assert output_name('a.mp4', 'Tên mới.mp4') == 'Tên mới.mp4'
    for value in ['CON', 'a/b', 'a:b', 'bad.', 'LPT1.log', 'x'*256]:
        with pytest.raises(ValueError):
            output_name('a.mp4', value)
    with pytest.raises(ValueError):
        plan_outputs([('a.mp4','Same'), ('b.mp4','same')], tmp_path)
    (tmp_path/'used.mp4').touch()
    with pytest.raises(FileExistsError):
        plan_outputs([('a.mp4','used')], tmp_path)

def test_real_batch_and_zip(samples, tmp_path):
    successes = []
    originals = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in samples.iterdir()}
    failures = 0
    for name, custom in [('silent',''), ('broken','broken'), ('sound','Âm thanh mới')]:
        source = samples/(name+'.mp4')
        target = plan_outputs([(source, custom)], tmp_path)[0]
        try:
            info = convert(source, target)
            assert info.audio_count == (2 if name == 'sound' else 0)
            assert (info.width, info.height) == (160, 120)
            assert probe(source).fps == info.fps
            data = json.loads(run([binary('ffprobe'), '-v','error','-show_streams','-of','json',str(target)]))
            starts = [float(s.get('start_time',0)) for s in data['streams']]
            assert max(starts)-min(starts) < .05
            successes.append(target)
        except RuntimeError:
            failures += 1
    assert failures == 1 and len(successes) == 2
    assert successes[0].name == 'silent-clean.mp4'
    assert successes[1].name == 'Âm thanh mới.mp4'
    archive = tmp_path/'converted-videos.zip'
    create_zip(successes, archive)
    with zipfile.ZipFile(archive) as z:
        assert z.namelist() == [p.name for p in successes]
        assert z.testzip() is None
        for p in successes:
            assert z.read(p.name) == p.read_bytes()
    for p, digest in originals.items():
        assert hashlib.sha256(p.read_bytes()).hexdigest() == digest
    with pytest.raises(FileExistsError):
        convert(samples/'silent.mp4', successes[0])
    with pytest.raises(FileExistsError):
        create_zip(successes, archive)

def test_cancel(samples, tmp_path):
    stop = threading.Event()
    stop.set()
    with pytest.raises(Cancelled):
        convert(samples/'sound.mp4', tmp_path/'cancel.mp4', cancel=stop)
    with pytest.raises(Cancelled):
        create_zip([samples/'sound.mp4'], tmp_path/'cancel.zip', cancel=stop)
    assert not list(tmp_path.iterdir())

def test_zip_cancel_during_write(tmp_path):
    source = tmp_path/'large.mp4'
    source.write_bytes(b'x' * 4_000_000)
    stop = threading.Event()
    with pytest.raises(Cancelled):
        create_zip([source], tmp_path/'cancel.zip', cancel=stop, progress=lambda n: stop.set())
    assert list(tmp_path.iterdir()) == [source]

def test_publish_race(samples, tmp_path):
    target = tmp_path/'race.mp4'
    def progress(n):
        if n >= 96 and not target.exists():
            target.write_bytes(b'Another application created this file')
    with pytest.raises(FileExistsError):
        convert(samples/'silent.mp4', target, progress=progress)
    assert target.read_bytes() == b'Another application created this file'
    assert list(tmp_path.iterdir()) == [target]
