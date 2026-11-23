def stylesheet(dark=True):
    bg, panel, text, muted, border = ('#171b20','#22282f','#edf1f5','#b7c2ce','#3c4753') if dark else ('#f3f5f7','#ffffff','#18232e','#526170','#b8c3cf')
    return f'''
    QWidget {{ background: {bg}; color: {text}; font-family: 'Segoe UI'; font-size: 13px; }}
    QLabel#title {{ font-size: 25px; font-weight: 650; }}
    QLabel#subtitle {{ color: {muted}; }}
    QLabel#section {{ font-size: 16px; font-weight: 600; margin-top: 6px; }}
    QPushButton {{ background: {panel}; border: 1px solid {border}; border-radius: 6px; padding: 9px 15px; min-height: 18px; }}
    QPushButton:hover {{ border-color: #56b5eb; }}
    QPushButton:pressed {{ background: {border}; }}
    QPushButton:focus, QLineEdit:focus, QComboBox:focus {{ border: 2px solid #56b5eb; }}
    QPushButton:disabled {{ color: {muted}; background: {bg}; border-color: {border}; }}
    QPushButton#primary {{ background: #137cb1; color: white; border: none; font-weight: 600; padding: 12px 20px; }}
    QPushButton#primary:hover {{ background: #086797; }}
    QPushButton#primary:disabled {{ background: {border}; color: {muted}; }}
    QLineEdit, QComboBox {{ background: {panel}; border: 1px solid {border}; border-radius: 4px; padding: 7px; }}
    QTableWidget {{ background: {panel}; border: 1px solid {border}; border-radius: 6px; gridline-color: {border}; selection-background-color: #235c7b; }}
    QTableWidget::item {{ padding: 5px; }}
    QHeaderView::section {{ background: {bg}; color: {muted}; border: none; border-bottom: 1px solid {border}; padding: 10px 6px; font-weight: 600; }}
    QProgressBar {{ background: {panel}; border: 1px solid {border}; border-radius: 4px; text-align: center; min-height: 20px; }}
    QProgressBar::chunk {{ background: #137cb1; border-radius: 3px; }}
    QCheckBox {{ spacing: 8px; }}
    QToolTip {{ background: {panel}; color: {text}; border: 1px solid {border}; }}
    '''
