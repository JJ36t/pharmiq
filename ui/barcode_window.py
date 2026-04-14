"""PharmIQ — Barcode Window (EAN-13)"""
import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QHBoxLayout,QLabel,QLineEdit,QMessageBox,QPushButton,QTableWidget,QTableWidgetItem,QVBoxLayout,QWidget)
from database.crud import get_all_drugs, search_drug_by_barcode, update_drug
from logic.barcode_manager import barcode_exists, generate_barcode, generate_barcode_number, validate_barcode
from logic.rtl_helper import apply_rtl
from ui.style import BTN_BLUE, BTN_GREEN

class BarcodeWindow(QWidget):
    def __init__(self, session):
        super().__init__()
        self.session = session
        apply_rtl(self)
        self.setWindowTitle("🔍 إدارة الباركود EAN-13")
        self.setGeometry(200, 140, 820, 620)
        layout = QVBoxLayout(self)
        layout.setSpacing(10); layout.setContentsMargins(15,15,15,15)
        title = QLabel("🔍 إدارة الباركود EAN-13")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial",15,QFont.Weight.Bold))
        title.setStyleSheet("color: #89b4fa; padding: 8px;")
        layout.addWidget(title)
        sr = QHBoxLayout()
        self.bc_input = QLineEdit(); self.bc_input.setPlaceholderText("أدخل رقم الباركود EAN-13 (13 رقم)...")
        self.bc_input.setMinimumHeight(40); self.bc_input.returnPressed.connect(self._search)
        sb = QPushButton("🔍 بحث"); sb.clicked.connect(self._search)
        sr.addWidget(self.bc_input); sr.addWidget(sb); layout.addLayout(sr)
        self.result_lbl = QLabel(""); self.result_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_lbl.setStyleSheet("font-size: 14px; padding: 5px;"); layout.addWidget(self.result_lbl)
        layout.addWidget(QLabel("📋 كل الأدوية وأرقام الباركود:"))
        self.table = QTableWidget()
        self.table.setColumnCount(4); self.table.setHorizontalHeaderLabels(["ID","الاسم التجاري","الباركود","الحالة"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        br = QHBoxLayout()
        gb = QPushButton("⚡ توليد باركود للمحدد"); gb.setStyleSheet(BTN_BLUE); gb.clicked.connect(self._generate)
        pb = QPushButton("🖨️ فتح صورة الباركود"); pb.clicked.connect(self._print)
        br.addWidget(gb); br.addWidget(pb); layout.addLayout(br)
        self._load()

    def _load(self):
        drugs = get_all_drugs(self.session)
        self.table.setRowCount(len(drugs))
        for r,d in enumerate(drugs):
            self.table.setItem(r,0,QTableWidgetItem(str(d.id)))
            self.table.setItem(r,1,QTableWidgetItem(d.trade_name))
            self.table.setItem(r,2,QTableWidgetItem(d.barcode or "—"))
            self.table.setItem(r,3,QTableWidgetItem("✅ موجود" if d.barcode else "❌ غير محدد"))

    def _search(self):
        num = self.bc_input.text().strip()
        if not num: return
        if not validate_barcode(num):
            self.result_lbl.setText("❌ رقم غير صحيح — يجب أن يكون 13 رقم بـ Check Digit صحيح")
            self.result_lbl.setStyleSheet("color: #f38ba8; padding: 5px;"); return
        drug = search_drug_by_barcode(self.session, num)
        if drug:
            self.result_lbl.setText(f"✅ وُجد: {drug.trade_name} | كمية: {drug.quantity} | سعر: {drug.price:,.0f} IQD")
            self.result_lbl.setStyleSheet("color: #a6e3a1; padding: 5px;")
        else:
            self.result_lbl.setText("❌ لا يوجد دواء بهذا الباركود")
            self.result_lbl.setStyleSheet("color: #f38ba8; padding: 5px;")

    def _generate(self):
        r = self.table.currentRow()
        if r == -1: QMessageBox.warning(self,"خطأ","اختر دواء من الجدول"); return
        did = int(self.table.item(r,0).text())
        dname = self.table.item(r,1).text()
        num = generate_barcode_number(did)
        filepath = generate_barcode(num, f"drug_{did}")
        update_drug(self.session, did, {"barcode": num})
        self._load()
        QMessageBox.information(self,"✅ تم",f"تم توليد الباركود:\n{dname}\nالرقم: {num}\nالملف: {filepath}")

    def _print(self):
        r = self.table.currentRow()
        if r == -1: QMessageBox.warning(self,"خطأ","اختر دواء"); return
        did = int(self.table.item(r,0).text())
        if barcode_exists(did):
            try: os.startfile(f"barcodes/drug_{did}.png")
            except: pass
        else: QMessageBox.warning(self,"خطأ","ولّد الباركود أولاً")
