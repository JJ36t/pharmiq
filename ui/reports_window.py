"""PharmIQ — Reports Window (Screen 6)"""
import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QHBoxLayout,QLabel,QMessageBox,QPushButton,QVBoxLayout,QWidget)
from reports.pdf_report import generate_drugs_pdf, generate_sales_pdf
from reports.excel_report import generate_drugs_excel, generate_sales_excel
from logic.rtl_helper import apply_rtl
from ui.style import BTN_BLUE, BTN_GREEN

class ReportsWindow(QWidget):
    def __init__(self, session):
        super().__init__()
        self.session = session
        apply_rtl(self)
        self.setWindowTitle("📊 التقارير")
        self.setGeometry(300, 200, 460, 340)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(25, 25, 25, 25)
        title = QLabel("📊 إنشاء التقارير")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #89b4fa; padding: 8px;")
        layout.addWidget(title)
        layout.addWidget(QLabel("اختر نوع التقرير:"))
        btns = [
            ("📄 تقرير الأدوية — PDF",     BTN_BLUE,  self._drugs_pdf),
            ("📄 تقرير المبيعات — PDF",    BTN_BLUE,  self._sales_pdf),
            ("📊 تقرير الأدوية — Excel",   BTN_GREEN, self._drugs_excel),
            ("📊 تقرير المبيعات — Excel",  BTN_GREEN, self._sales_excel),
        ]
        for label, style, slot in btns:
            btn = QPushButton(label)
            btn.setStyleSheet(style)
            btn.setMinimumHeight(42)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

    def _open(self, filename):
        QMessageBox.information(self,"✅ تم",f"تم حفظ الملف:\n{os.path.abspath(filename)}")
        try: os.startfile(filename)
        except: pass

    def _drugs_pdf(self):   self._open(generate_drugs_pdf(self.session))
    def _sales_pdf(self):   self._open(generate_sales_pdf(self.session))
    def _drugs_excel(self): self._open(generate_drugs_excel(self.session))
    def _sales_excel(self): self._open(generate_sales_excel(self.session))
