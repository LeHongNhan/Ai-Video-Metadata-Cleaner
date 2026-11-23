import logging
import sys
from logging.handlers import RotatingFileHandler
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer
from config.settings import DATA, setup_dirs
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName('AI Video Metadata Cleaner')
    app.setStyle('Fusion')
    try:
        setup_dirs()
        logging.basicConfig(level=logging.INFO,
            handlers=[RotatingFileHandler(DATA/'logs'/'app.log', maxBytes=2_000_000, backupCount=3, encoding='utf-8')],
            format='%(asctime)s %(levelname)s %(message)s')
        window = MainWindow()
    except Exception as exc:
        QMessageBox.critical(None, 'Không thể khởi động', str(exc))
        return 1
    window.show()
    if len(sys.argv) == 3 and sys.argv[1] == '--self-test':
        def check():
            from utils.self_test import self_test
            try:
                self_test(sys.argv[2])
                window.close()
                app.exit(0)
            except Exception:
                logging.exception('Packaged self-test failed')
                app.exit(1)
        QTimer.singleShot(100, check)
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
