"""PharmIQ — Backup Window (Screen 8 partial)"""
import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QHBoxLayout,QLabel,QListWidget,QMessageBox,QPushButton,QVBoxLayout,QWidget)
from logic.backup_manager import create_backup, get_all_backups, restore_backup
from logic.rtl_helper import apply_rtl
from ui.style import BTN_GREEN, BTN_YELLOW

class BackupWindow(QWidget):
    def __init__(self):
        super().__init__()
        apply_rtl(self)
        self.setWindowTitle("💾 النسخ الاحتياطي")
        self.setGeometry(300, 200, 620, 460)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        title = QLabel("💾 إدارة النسخ الاحتياطي")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #89b4fa; padding: 8px;")
        layout.addWidget(title)
        info = QLabel("📌 نسخ تلقائي يومي الساعة 02:00 — يُحتفظ بآخر 7 نسخ")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: #6c7086; font-size: 12px;")
        layout.addWidget(info)
        layout.addWidget(QLabel("📂 النسخ الاحتياطية المتاحة:"))
        self.backup_list = QListWidget()
        self.backup_list.setStyleSheet("background-color: #181825; color: #cdd6f4; border-radius: 6px;")
        layout.addWidget(self.backup_list)
        btns = QHBoxLayout()
        nb = QPushButton("💾 نسخ احتياطي الآن")
        nb.setStyleSheet(BTN_GREEN); nb.setMinimumHeight(38); nb.clicked.connect(self._backup)
        rb = QPushButton("🔄 استعادة النسخة المحددة")
        rb.setStyleSheet(BTN_YELLOW); rb.setMinimumHeight(38); rb.clicked.connect(self._restore)
        ob = QPushButton("📁 فتح المجلد"); ob.clicked.connect(self._open_folder)
        btns.addWidget(nb); btns.addWidget(rb); btns.addWidget(ob)
        layout.addLayout(btns)
        self.status_lbl = QLabel("")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet("color: #a6e3a1; font-size: 12px;")
        layout.addWidget(self.status_lbl)
        self._load()

    def _load(self):
        self.backup_list.clear()
        backups = get_all_backups()
        if not backups: self.backup_list.addItem("لا توجد نسخ احتياطية بعد")
        for b in backups: self.backup_list.addItem(b)

    def _backup(self):
        path = create_backup()
        if path: self.status_lbl.setText(f"✅ تم: {os.path.basename(path)}"); self._load()
        else: self.status_lbl.setText("❌ فشل — تأكد من وجود pharmiq.db")

    def _restore(self):
        sel = self.backup_list.currentItem()
        if not sel or sel.text() == "لا توجد نسخ احتياطية بعد":
            QMessageBox.warning(self,"خطأ","اختر نسخة من القائمة"); return
        if QMessageBox.question(self,"تأكيد",f"استعادة:\n{sel.text()}\n\nسيُستبدل قاعدة البيانات الحالية!")==QMessageBox.StandardButton.Yes:
            if restore_backup(sel.text()): QMessageBox.information(self,"✅ تم","أعد تشغيل البرنامج")
            else: QMessageBox.warning(self,"خطأ","فشلت الاستعادة")

    def _open_folder(self):
        os.makedirs("backups",exist_ok=True)
        try: os.startfile("backups")
        except: pass
