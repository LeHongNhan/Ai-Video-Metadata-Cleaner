import logging
import threading
from PySide6.QtCore import QThread, Signal
from core.video_probe import probe
from core.video_processor import convert
from core.zip_manager import create_zip
from utils.process import Cancelled

class Task(QThread):
    event = Signal(object)

    def __init__(self, mode, payload, parent=None):
        super().__init__(parent)
        self.mode, self.payload = mode, payload
        self.cancel = threading.Event()

    def run(self):
        try:
            if self.mode == 'probe':
                for key, path in self.payload:
                    if self.cancel.is_set():
                        break
                    try:
                        self.event.emit(('probed', key, probe(path, self.cancel)))
                    except Cancelled:
                        break
                    except Exception as exc:
                        self.event.emit(('probe_error', key, str(exc)))
            elif self.mode == 'convert':
                jobs, crf = self.payload
                for index, (key, source, target) in enumerate(jobs):
                    if self.cancel.is_set():
                        self.event.emit(('state', key, 'Đã hủy', ''))
                        continue
                    self.event.emit(('state', key, 'Đang xử lý', ''))
                    try:
                        def progress(value):
                            self.event.emit(('progress', key, value, int((index+value/100)/len(jobs)*100)))
                        info = convert(source, target, crf, self.cancel, progress)
                        self.event.emit(('success', key, target, info))
                    except Cancelled:
                        self.event.emit(('state', key, 'Đã hủy', ''))
                    except Exception as exc:
                        logging.exception('Conversion failed: %s', source)
                        self.event.emit(('state', key, 'Thất bại', str(exc)))
                    self.event.emit(('overall', int((index+1)/len(jobs)*100)))
            else:
                files, target = self.payload
                create_zip(files, target, self.cancel, lambda n: self.event.emit(('zip_progress', n)))
                self.event.emit(('zip_success', target))
        except Cancelled:
            self.event.emit(('notice', 'Đã hủy tác vụ. File tạm đã được dọn dẹp.'))
        except Exception as exc:
            logging.exception('Task failed')
            self.event.emit(('error', str(exc)))
