from pathlib import Path

root = Path(SPECPATH)
executables = []
for name in ('ffmpeg', 'ffprobe'):
    choices = list((root/'tools').glob(f'{name}.exe')) + list((root/'tools').glob(f'*/bin/{name}.exe'))
    if not choices:
        raise RuntimeError(f'Place {name}.exe in tools before building.')
    executables.append((str(choices[0]), 'tools'))
licenses = [(str(p), 'licenses') for p in (root/'tools').glob('*/LICENSE')]
a = Analysis(['main.py'], pathex=[str(root)], binaries=executables, datas=licenses,
             hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[])
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='AI Video Metadata Cleaner',
          debug=False, bootloader_ignore_signals=False, strip=False, upx=False, console=False)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='AI Video Metadata Cleaner')
