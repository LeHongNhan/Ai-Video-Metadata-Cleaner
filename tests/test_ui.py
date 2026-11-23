import time
from pathlib import Path
from PySide6.QtCore import QTimer, QSettings
from PySide6.QtWidgets import QApplication, QMessageBox
from ui.main_window import MainWindow
from utils.process import run
from config.settings import binary

def pump(app, condition, timeout=30):
    start = time.monotonic()
    while not condition():
        app.processEvents()
        time.sleep(.01)
        assert time.monotonic()-start < timeout
    app.processEvents()

def test_ui_actual_batch(tmp_path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    monkeypatch.setattr('ui.main_window.QSettings', lambda *args: QSettings(str(tmp_path/'prefs.ini'), QSettings.Format.IniFormat))
    monkeypatch.setattr(QMessageBox, 'information', lambda *a: None)
    source = tmp_path/'sample.mp4'
    run([binary('ffmpeg'), '-v','error','-f','lavfi','-i','testsrc2=size=640x360:rate=30:duration=3', '-c:v','libx264',str(source)])
    bad = tmp_path/'bad.mp4'
    bad.write_bytes(b'invalid')
    window = MainWindow()
    window.output.setText(str(tmp_path/'out'))
    window.show()
    window.add_paths([str(source), str(source), str(bad)])
    pump(app, lambda: window.task is None)
    assert len(window.records)==2
    assert window.records[0]['editor'].text()=='sample-clean'
    window.records[0]['editor'].setText('Tên tùy chỉnh')
    ticks = []
    timer = QTimer()
    timer.timeout.connect(lambda: ticks.append(time.monotonic()))
    timer.start(10)
    window.start_batch()
    assert not window.records[0]['editor'].isEnabled()
    pump(app, lambda: window.task is None)
    timer.stop()
    assert len(ticks)>5
    assert window.records[0]['state']=='Hoàn thành'
    assert window.records[1]['state']=='Thất bại'
    assert (tmp_path/'out'/'Tên tùy chỉnh.mp4').is_file()
    assert window.records[0]['editor'].text()=='Tên tùy chỉnh'
    assert window.results.rowCount()==1 and window.zip.isEnabled()
    window.dark.setChecked(False)
    app.processEvents()
    window.grab().save(str(Path('tests')/'ui-light.png'))
    window.dark.setChecked(True)
    app.processEvents()
    window.grab().save(str(Path('tests')/'ui-dark.png'))
    window.clear_all()
    assert window.queue.rowCount()==0
    window.close()

def test_large_input_cancel_responsive(tmp_path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    monkeypatch.setattr('ui.main_window.QSettings', lambda *args: QSettings(str(tmp_path/'prefs.ini'), QSettings.Format.IniFormat))
    monkeypatch.setattr(QMessageBox, 'information', lambda *a: None)
    source = tmp_path/'large.avi'
    # Over 150 MB of real uncompressed frames, not a mocked processor.
    run([binary('ffmpeg'), '-v','error','-f','lavfi','-i','testsrc2=size=1920x1080:rate=30:duration=2', '-c:v','rawvideo',str(source)])
    assert source.stat().st_size > 150_000_000
    window = MainWindow()
    window.output.setText(str(tmp_path/'out'))
    window.add_paths([str(source)])
    pump(app, lambda: window.task is None)
    ticks = []
    timer = QTimer()
    timer.timeout.connect(lambda: ticks.append(time.monotonic()))
    timer.start(10)
    window.start_batch()
    QTimer.singleShot(300, window.cancel_task)
    pump(app, lambda: window.task is None)
    timer.stop()
    assert len(ticks) >= 10
    assert window.records[0]['state'] == 'Đã hủy'
    assert not list((tmp_path/'out').iterdir())
    window.close()
