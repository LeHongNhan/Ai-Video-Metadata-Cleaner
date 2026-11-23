import os
import uuid
from pathlib import Path
from PySide6.QtCore import Qt, QUrl, QSettings
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QFileDialog, QMessageBox, QProgressBar, QComboBox, QCheckBox)
from config.settings import DATA, SUPPORTED, binary
from core.file_manager import plan_outputs
from workers.tasks import Task
from ui.theme import stylesheet

def size_text(size):
    return f'{size / 1024**2:,.1f} MB' if size < 1024**3 else f'{size / 1024**3:,.2f} GB'

def duration_text(seconds):
    seconds = round(seconds)
    return f'{seconds//3600:02}:{seconds//60%60:02}:{seconds%60:02}'

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('AI Video Metadata Cleaner')
        self.resize(1250, 880)
        self.setMinimumSize(1020, 720)
        self.setAcceptDrops(True)
        self.records = []
        self.task = None
        self.last_zip = None
        self.settings = QSettings('VideoConverter', 'AI Video Metadata Cleaner')
        body = QWidget()
        self.setCentralWidget(body)
        layout = QVBoxLayout(body)
        layout.setContentsMargins(28, 22, 28, 22)
        layout.setSpacing(12)
        header = QHBoxLayout()
        title = QLabel('AI Video Metadata Cleaner')
        title.setObjectName('title')
        header.addWidget(title)
        header.addStretch()
        self.dark = QCheckBox('Giao diện tối')
        self.dark.setChecked(self.settings.value('dark', True, type=bool))
        self.dark.toggled.connect(self.apply_theme)
        header.addWidget(self.dark)
        layout.addLayout(header)
        subtitle = QLabel('Chuyển đổi video trên máy tính của bạn • Không tải lên máy chủ')
        subtitle.setObjectName('subtitle')
        layout.addWidget(subtitle)

        row = QHBoxLayout()
        self.count = QLabel('Hàng đợi · 0 video')
        self.count.setObjectName('section')
        row.addWidget(self.count)
        row.addStretch()
        self.add = self.button('Thêm video…', self.choose_files, row)
        self.remove = self.button('Xóa đã chọn', self.remove_selected, row)
        self.clear = self.button('Xóa danh sách', self.clear_all, row)
        layout.addLayout(row)
        self.hint = QLabel('Kéo thả MP4, MOV, MKV, AVI, WEBM hoặc M4V vào đây. Sửa tên đầu ra ngay trên từng dòng.')
        self.hint.setObjectName('subtitle')
        layout.addWidget(self.hint)
        self.queue = self.table(['File gốc', 'Định dạng', 'Độ phân giải', 'Thời lượng', 'Dung lượng', 'Tên đầu ra (.mp4)', 'Trạng thái'])
        self.queue.setAcceptDrops(False)
        layout.addWidget(self.queue, 3)
        self.queue.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.queue.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)

        settings = QHBoxLayout()
        settings.addWidget(QLabel('MP4  /  H.264  /  AAC'))
        settings.addSpacing(20)
        settings.addWidget(QLabel('Chất lượng'))
        self.crf = QComboBox()
        self.crf.addItems(['CRF 18 · Cao', 'CRF 20', 'CRF 23', 'CRF 26 · Nhỏ hơn'])
        self.crf.setAccessibleName('Chất lượng CRF')
        settings.addWidget(self.crf)
        settings.addStretch()
        settings.addWidget(QLabel('Giữ độ phân giải, FPS và các luồng âm thanh'))
        layout.addLayout(settings)
        folder = QHBoxLayout()
        folder.addWidget(QLabel('Lưu video tại'))
        self.output = QLineEdit(self.settings.value('output', str(DATA/'output')))
        self.output.setAccessibleName('Thư mục đầu ra')
        folder.addWidget(self.output, 1)
        self.browse = self.button('Chọn thư mục…', self.choose_output, folder)
        self.button('Mở thư mục đầu ra', self.open_output, folder)
        layout.addLayout(folder)
        actions = QHBoxLayout()
        self.start = self.button('Bắt đầu chuyển đổi', lambda: self.start_batch(False), actions, True)
        self.retry = self.button('Xử lý lại video thất bại', lambda: self.start_batch(True), actions)
        self.cancel = self.button('Hủy tác vụ', self.cancel_task, actions)
        self.cancel.setEnabled(False)
        self.overall = QProgressBar()
        self.overall.setValue(0)
        actions.addWidget(self.overall, 1)
        layout.addLayout(actions)
        self.message = QLabel('Sẵn sàng. File gốc luôn được giữ nguyên.')
        self.message.setWordWrap(True)
        layout.addWidget(self.message)

        label = QLabel('Video đã xuất')
        label.setObjectName('section')
        layout.addWidget(label)
        self.results = self.table(['Tên file đầu ra', 'Dung lượng', 'Thời lượng', 'Trạng thái', 'Vị trí'])
        self.results.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.results.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.results.setColumnWidth(4, 145)
        layout.addWidget(self.results, 2)
        bottom = QHBoxLayout()
        self.zip = self.button('TẢI TẤT CẢ (.ZIP)', self.save_zip, bottom, True)
        self.zip_folder = self.button('Mở thư mục chứa ZIP', self.open_zip, bottom)
        self.zip.setEnabled(False)
        self.zip_folder.setEnabled(False)
        bottom.addStretch()
        note = QLabel('Tái mã hóa thông thường; không cam kết xóa dấu chìm\nhoặc né hệ thống nhận diện nội dung AI.')
        note.setObjectName('subtitle')
        bottom.addWidget(note)
        layout.addLayout(bottom)
        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet(stylesheet(self.dark.isChecked()))
        self.settings.setValue('dark', self.dark.isChecked())

    def button(self, text, slot, layout, primary=False):
        button = QPushButton(text)
        if primary:
            button.setObjectName('primary')
        button.clicked.connect(slot)
        layout.addWidget(button)
        return button

    def table(self, headers):
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().hide()
        table.verticalHeader().setDefaultSectionSize(46)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setShowGrid(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        return table

    def warn(self, message):
        QMessageBox.warning(self, 'Không thể thực hiện', str(message))

    def choose_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, 'Chọn video', '', 'Video (*.mp4 *.mov *.mkv *.avi *.webm *.m4v)')
        self.add_paths(paths)

    def add_paths(self, paths):
        if self.task:
            return
        known = {os.path.normcase(str(r['path'])) for r in self.records}
        jobs, skipped = [], 0
        for value in paths:
            path = Path(value).resolve()
            keypath = os.path.normcase(str(path))
            if not path.is_file() or path.suffix.lower() not in SUPPORTED or keypath in known:
                skipped += 1
                continue
            known.add(keypath)
            key = uuid.uuid4().hex
            editor = QLineEdit(path.stem+'-clean')
            editor.setAccessibleName(f'Tên đầu ra cho {path.name}')
            editor.setPlaceholderText(path.stem+'-clean')
            record = dict(key=key, path=path, editor=editor, state='Chờ xử lý', info=None, target=None)
            self.records.append(record)
            row = self.queue.rowCount()
            self.queue.insertRow(row)
            for col, text in enumerate([path.name, path.suffix[1:].upper(), '—', '—', size_text(path.stat().st_size), '', 'Đang đọc…']):
                self.queue.setItem(row, col, QTableWidgetItem(text))
            self.queue.item(row, 0).setToolTip(str(path))
            self.queue.setCellWidget(row, 5, editor)
            jobs.append((key, path))
        self.count.setText(f'Hàng đợi · {len(self.records)} video')
        self.message.setText(f'Đã thêm {len(jobs)} video. Bỏ qua {skipped} file trùng hoặc không hỗ trợ.')
        if jobs:
            self.launch('probe', jobs)

    def dragEnterEvent(self, event):
        if not self.task and event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.add_paths([url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()])
        event.acceptProposedAction()

    def remove_selected(self):
        for row in sorted({i.row() for i in self.queue.selectedIndexes()}, reverse=True):
            self.queue.removeRow(row)
            self.records.pop(row)
        self.count.setText(f'Hàng đợi · {len(self.records)} video')
        self.refresh_results()

    def clear_all(self):
        self.records.clear()
        self.queue.setRowCount(0)
        self.count.setText('Hàng đợi · 0 video')
        self.refresh_results()
        self.overall.setValue(0)

    def choose_output(self):
        folder = QFileDialog.getExistingDirectory(self, 'Thư mục đầu ra', self.output.text())
        if folder:
            self.output.setText(folder)

    def open_folder(self, path):
        if not Path(path).is_dir():
            self.warn('Thư mục chưa tồn tại hoặc đã bị di chuyển.')
        elif not QDesktopServices.openUrl(QUrl.fromLocalFile(str(path))):
            self.warn('Không mở được thư mục. Hãy mở bằng File Explorer.')

    def open_output(self):
        self.open_folder(self.output.text())

    def open_zip(self):
        if self.last_zip:
            self.open_folder(self.last_zip.parent)

    def start_batch(self, retry=False):
        if self.task:
            return
        selected = [r for r in self.records if r['state'] == 'Thất bại' or (not retry and r['state'] in ('Chờ xử lý','Đã hủy'))]
        if not selected:
            self.warn('Không có video cần xử lý. Hãy thêm video vào danh sách.')
            return
        try:
            binary('ffmpeg')
            binary('ffprobe')
            if not self.output.text().strip():
                raise ValueError('Hãy chọn thư mục đầu ra.')
            targets = plan_outputs([(r['path'], r['editor'].text()) for r in selected], self.output.text())
            Path(self.output.text()).mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            self.warn(exc)
            return
        self.settings.setValue('output', self.output.text())
        jobs = [(r['key'], r['path'], target) for r, target in zip(selected, targets)]
        for r in selected:
            r['state'] = 'Chờ xử lý'
        self.overall.setValue(0)
        self.message.setText(f'Đang chuyển đổi {len(jobs)} video…')
        self.launch('convert', (jobs, (18,20,23,26)[self.crf.currentIndex()]))

    def launch(self, mode, payload):
        self.task = Task(mode, payload, self)
        self.task.event.connect(self.on_event)
        self.task.finished.connect(self.task_finished)
        self.set_busy(True)
        self.task.start()

    def set_busy(self, busy):
        for widget in (self.add, self.remove, self.clear, self.start, self.retry, self.output, self.browse, self.crf):
            widget.setEnabled(not busy)
        for r in self.records:
            r['editor'].setEnabled(not busy and r['state'] != 'Hoàn thành')
        self.cancel.setEnabled(busy)
        self.zip.setEnabled(not busy and any(r['target'] for r in self.records))

    def cancel_task(self):
        if self.task:
            self.task.cancel.set()
            self.cancel.setEnabled(False)
            self.message.setText('Đang hủy và dọn dẹp file tạm…')

    def task_finished(self):
        task = self.task
        self.task = None
        self.set_busy(False)
        if task.mode == 'convert':
            done = sum(r['state']=='Hoàn thành' for r in self.records)
            failed = sum(r['state']=='Thất bại' for r in self.records)
            cancelled = sum(r['state']=='Đã hủy' for r in self.records)
            text = f'Kết thúc lượt xử lý: {done} hoàn thành · {failed} thất bại · {cancelled} đã hủy.'
            self.message.setText(text)
            QMessageBox.information(self, 'Kết quả chuyển đổi', text)
        elif task.mode == 'probe' and task.cancel.is_set():
            self.message.setText('Đã dừng đọc thông tin. Các video vẫn có thể được chuyển đổi.')
        task.deleteLater()

    def on_event(self, event):
        kind = event[0]
        if kind in ('probed', 'probe_error', 'state', 'progress', 'success'):
            match = next(((i,r) for i,r in enumerate(self.records) if r['key']==event[1]), None)
            if not match:
                return
            row, record = match
            if kind == 'probed':
                info = event[2]
                record['info'] = info
                self.queue.item(row,2).setText(f'{info.width} × {info.height}')
                self.queue.item(row,3).setText(duration_text(info.duration))
                self.queue.item(row,6).setText(record['state'])
            elif kind == 'probe_error':
                record['state'] = 'Thất bại'
                self.queue.item(row,6).setText('Thất bại · đọc file')
                self.queue.item(row,6).setToolTip(event[2])
                self.message.setText('Có file không đọc được. Di chuột vào trạng thái để xem chi tiết; bạn có thể xử lý các file còn lại.')
            elif kind == 'state':
                record['state'] = event[2]
                self.queue.item(row,6).setText(event[2])
                self.queue.item(row,6).setToolTip(event[3])
            elif kind == 'progress':
                self.queue.item(row,6).setText(f'Đang xử lý · {event[2]}%')
                self.overall.setValue(event[3])
            else:
                record.update(state='Hoàn thành', target=Path(event[2]), result_info=event[3])
                self.queue.item(row,6).setText('Hoàn thành')
                self.refresh_results()
        elif kind in ('overall','zip_progress'):
            self.overall.setValue(event[1])
        elif kind == 'zip_success':
            self.last_zip = Path(event[1])
            self.zip_folder.setEnabled(True)
            self.message.setText(f'Đã lưu ZIP: {self.last_zip}')
        elif kind == 'error':
            self.message.setText('Tác vụ thất bại. Xem thông báo để biết chi tiết.')
            self.warn(event[1])
        elif kind == 'notice':
            self.message.setText(event[1])

    def refresh_results(self):
        self.results.setRowCount(0)
        for record in self.records:
            if not record['target']:
                continue
            path, info = record['target'], record['result_info']
            row = self.results.rowCount()
            self.results.insertRow(row)
            for col, text in enumerate([path.name, size_text(info.size), duration_text(info.duration), 'Hoàn thành']):
                self.results.setItem(row, col, QTableWidgetItem(text))
            button = QPushButton('Mở vị trí file')
            button.clicked.connect(lambda checked=False, p=path: self.open_folder(p.parent))
            self.results.setCellWidget(row,4,button)
        self.zip.setEnabled(self.task is None and self.results.rowCount()>0)

    def save_zip(self):
        files = [r['target'] for r in self.records if r['state']=='Hoàn thành' and r['target']]
        target, _ = QFileDialog.getSaveFileName(self, 'Lưu tất cả video', str(Path(self.output.text())/'converted-videos.zip'), 'ZIP (*.zip)', options=QFileDialog.Option.DontConfirmOverwrite)
        if not target:
            return
        if not target.lower().endswith('.zip'):
            target += '.zip'
        if Path(target).exists():
            self.warn('File ZIP đã tồn tại. Hãy chọn tên khác; file cũ không bị ghi đè.')
            return
        self.overall.setValue(0)
        self.message.setText('Đang đóng gói video thành công vào ZIP…')
        self.launch('zip', (files, Path(target)))

    def closeEvent(self, event):
        if self.task:
            self.cancel_task()
            self.message.setText('Đang dừng tác vụ. Vui lòng đóng cửa sổ lại sau khi dọn dẹp xong.')
            event.ignore()
        else:
            event.accept()
