import os
import re
from pathlib import Path

def output_name(source, value):
    value = value.strip() or (Path(source).stem + '-clean')
    if value.lower().endswith('.mp4'):
        value = value[:-4]
    if not value or re.search(r'[<>:"/\\|?*\x00-\x1f]', value) or value.endswith(('.', ' ')):
        raise ValueError('Tên file chứa ký tự không hợp lệ trên Windows.')
    reserved = {'CON','PRN','AUX','NUL','CONIN$','CONOUT$'} | {f'{p}{i}' for p in ('COM','LPT') for i in '123456789¹²³'}
    if value.split('.')[0].upper() in reserved or len((value+'.mp4').encode('utf-16-le')) > 510:
        raise ValueError('Tên file quá dài hoặc là tên dành riêng của Windows.')
    return value + '.mp4'

def plan_outputs(entries, directory):
    directory = Path(directory).resolve()
    seen, result = set(), []
    for source, value in entries:
        name = output_name(source, value)
        if name.casefold() in seen:
            raise ValueError(f'Trùng tên đầu ra: {name}. Hãy đặt tên khác.')
        seen.add(name.casefold())
        target = directory / name
        if target.exists():
            raise FileExistsError(f'File đã tồn tại: {target}. Hãy đặt tên khác.')
        result.append(target)
    return result

def publish(temp, target):
    # Atomic, exclusive publication on the same filesystem; never overwrite.
    if os.name == 'nt':
        os.rename(temp, target)
    else:
        os.link(temp, target)
        Path(temp).unlink()
