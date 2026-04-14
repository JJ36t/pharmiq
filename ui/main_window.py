"""
PharmIQ — Main Window (Screen 2: Inventory Management)
الشاشة الرئيسية — إدارة المخزون مع ألوان الحالة وشريط الإحصائيات
"""

import sys
from datetime import date

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QApplication, QHBoxLayout, QInputDialog, QLabel,
    QLineEdit, QMainWindow, QMessageBox, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from database.crud import (
    add_drug, delete_drug, get_all_drugs,
    search_drug, search_drug_by_barcode, update_drug,
)
from database.db import SessionLocal
from logic.alerts import check_alerts
from logic.rtl_helper import apply_rtl
from ui.style import (
    DARK_STYLE,
    BTN_BLUE, BTN_CYAN, BTN_GREEN, BTN_ORANGE,
    BTN_PURPLE, BTN_RED, BTN_TEAL, BTN_YELLOW,
)


class MainWindow(QMainWindow):
    def __init__(self, session, user):
        super().__init__()
        self.session      = session
        self.current_user = user

        apply_rtl(self)
        self.setWindowTitle(f"PharmIQ — {user.username} ({user.role})")
        self.setGeometry(80, 60, 1350, 720)
        self.setStyleSheet(DARK_STYLE)

        self._build_ui()
        self._connect_signals()
        self._apply_permissions()
        self._start_auto_refresh()
        self.load_data()

    # ══════════════════════════════════════════════════════════════════════════
    # بناء الواجهة
    # ══════════════════════════════════════════════════════════════════════════

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        # ── عنوان ─────────────────────────────────────────────────────────
        title = QLabel(f"💊 PharmIQ  —  مرحباً {self.current_user.username}  |  {self.current_user.role}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #89b4fa; padding: 6px;")
        layout.addWidget(title)

        # ── جدول الأدوية ──────────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { alternate-background-color: #242435; }")
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

        # ── صف أزرار 1 ────────────────────────────────────────────────────
        row1 = QHBoxLayout()
        row1.setSpacing(7)

        self.add_btn          = QPushButton("➕ إضافة دواء")
        self.edit_btn         = QPushButton("✏️ تعديل الدواء")
        self.delete_btn       = QPushButton("❌ حذف")
        self.alert_btn        = QPushButton("🔔 التنبيهات")
        self.pos_btn          = QPushButton("🛒 نظام البيع")
        self.reports_btn      = QPushButton("📊 التقارير")
        self.stats_btn        = QPushButton("📈 الإحصائيات")

        self.add_btn.setStyleSheet(BTN_GREEN)
        self.delete_btn.setStyleSheet(BTN_RED)
        self.pos_btn.setStyleSheet(BTN_BLUE)
        self.stats_btn.setStyleSheet(BTN_PURPLE)

        for btn in (self.add_btn, self.edit_btn, self.delete_btn,
                    self.alert_btn, self.pos_btn, self.reports_btn, self.stats_btn):
            row1.addWidget(btn)

        layout.addLayout(row1)

        # ── صف أزرار 2 ────────────────────────────────────────────────────
        row2 = QHBoxLayout()
        row2.setSpacing(7)

        self.barcode_btn      = QPushButton("🔍 الباركود")
        self.interact_btn     = QPushButton("⚠️ التفاعلات")
        self.suppliers_btn    = QPushButton("🏭 الموردين")
        self.backup_btn       = QPushButton("💾 النسخ الاحتياطي")
        self.change_pass_btn  = QPushButton("🔒 كلمة المرور")
        self.logout_btn       = QPushButton("🚪 خروج")

        self.barcode_btn.setStyleSheet(BTN_CYAN)
        self.interact_btn.setStyleSheet(BTN_ORANGE)
        self.suppliers_btn.setStyleSheet(BTN_TEAL)
        self.backup_btn.setStyleSheet(BTN_GREEN)
        self.logout_btn.setStyleSheet(BTN_RED)

        for btn in (self.barcode_btn, self.interact_btn, self.suppliers_btn,
                    self.backup_btn):
            row2.addWidget(btn)

        if self.current_user.role == "admin":
            self.users_btn = QPushButton("👥 المستخدمين")
            self.users_btn.setStyleSheet(BTN_YELLOW)
            row2.addWidget(self.users_btn)
            self.users_btn.clicked.connect(self._open_users)

        row2.addWidget(self.change_pass_btn)
        row2.addStretch()

        # بحث
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 بحث بالاسم أو الباركود (13 رقم)...")
        self.search_input.setMinimumWidth(260)
        self.search_btn = QPushButton("بحث")

        row2.addWidget(self.search_input)
        row2.addWidget(self.search_btn)
        row2.addWidget(self.logout_btn)
        layout.addLayout(row2)

        # ── شريط الحالة ───────────────────────────────────────────────────
        self.statusBar().setStyleSheet("background-color: #181825; color: #a6e3a1; padding: 3px;")

    # ══════════════════════════════════════════════════════════════════════════
    # ربط الإشارات
    # ══════════════════════════════════════════════════════════════════════════

    def _connect_signals(self):
        self.add_btn.clicked.connect(self._add_drug)
        self.edit_btn.clicked.connect(self._edit_drug)
        self.delete_btn.clicked.connect(self._delete_drug)
        self.alert_btn.clicked.connect(self._show_alerts)
        self.pos_btn.clicked.connect(self._open_pos)
        self.reports_btn.clicked.connect(self._open_reports)
        self.stats_btn.clicked.connect(self._open_stats)
        self.barcode_btn.clicked.connect(self._open_barcode)
        self.interact_btn.clicked.connect(self._open_interactions)
        self.suppliers_btn.clicked.connect(self._open_suppliers)
        self.backup_btn.clicked.connect(self._open_backup)
        self.change_pass_btn.clicked.connect(self._open_change_password)
        self.logout_btn.clicked.connect(self._logout)
        self.search_btn.clicked.connect(self._search)
        self.search_input.returnPressed.connect(self._search)

    # ══════════════════════════════════════════════════════════════════════════
    # صلاحيات الكاشير
    # ══════════════════════════════════════════════════════════════════════════

    def _apply_permissions(self):
        if self.current_user.role == "cashier":
            for btn in (self.add_btn, self.edit_btn, self.delete_btn, self.reports_btn):
                btn.setEnabled(False)

    # ══════════════════════════════════════════════════════════════════════════
    # تحديث تلقائي كل 3 ثواني
    # ══════════════════════════════════════════════════════════════════════════

    def _start_auto_refresh(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self._auto_refresh)
        self.timer.start(3000)

    def _auto_refresh(self):
        if not self.search_input.text():
            self.session.expire_all()
            self.load_data()

    # ══════════════════════════════════════════════════════════════════════════
    # تحميل الجدول
    # ══════════════════════════════════════════════════════════════════════════

    def load_data(self, drugs=None):
        if drugs is None:
            drugs = get_all_drugs(self.session)

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(drugs))
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "الاسم التجاري", "الاسم العلمي",
            "الفئة", "الكمية", "السعر (IQD)",
            "تاريخ الانتهاء", "الباركود",
        ])

        low_count = exp_count = expired_count = 0

        for row, drug in enumerate(drugs):
            self.table.setItem(row, 0, QTableWidgetItem(str(drug.id)))
            self.table.setItem(row, 1, QTableWidgetItem(drug.trade_name))
            self.table.setItem(row, 2, QTableWidgetItem(drug.scientific_name or ""))
            self.table.setItem(row, 3, QTableWidgetItem(drug.category or ""))
            self.table.setItem(row, 4, QTableWidgetItem(str(drug.quantity)))
            self.table.setItem(row, 5, QTableWidgetItem(f"{drug.price:,.0f}"))
            self.table.setItem(row, 6, QTableWidgetItem(str(drug.expiry_date) if drug.expiry_date else "—"))
            self.table.setItem(row, 7, QTableWidgetItem(drug.barcode or ""))

            # ألوان الحالة
            if drug.is_expired:
                color = QColor("#4a1020"); expired_count += 1
            elif drug.is_low_stock:
                color = QColor("#3d1f2a"); low_count += 1
            elif drug.is_expiring_soon:
                color = QColor("#3d2e1f"); exp_count += 1
            else:
                color = None

            if color:
                for col in range(8):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(color)

        self.table.setSortingEnabled(True)

        # شريط الحالة
        self.statusBar().showMessage(
            f"  {self.current_user.username}  |  "
            f"الأدوية: {len(drugs)}  |  "
            f"🔴 منتهية: {expired_count}  |  "
            f"⚠️ تنتهي قريباً: {exp_count}  |  "
            f"📦 مخزون قليل: {low_count}"
        )

    # ══════════════════════════════════════════════════════════════════════════
    # عمليات CRUD
    # ══════════════════════════════════════════════════════════════════════════

    def _add_drug(self):
        fields = [
            ("الاسم التجاري:",       "getText",  None),
            ("الاسم العلمي:",        "getText",  None),
            ("الفئة (مثل Antibiotics):", "getText", None),
            ("الكمية:",              "getInt",   (1, 0, 99999)),
            ("السعر (دينار):",       "getInt",   (0, 0, 9999999)),
            ("تاريخ الصلاحية (YYYY-MM-DD):", "getText", None),
        ]
        values = {}
        keys   = ["trade_name", "scientific_name", "category", "quantity", "price", "expiry_str"]

        for (label, method, args), key in zip(fields, keys):
            if method == "getText":
                val, ok = QInputDialog.getText(self, "إضافة دواء", label)
                if not ok:
                    return
                if key == "trade_name" and not val.strip():
                    QMessageBox.warning(self, "خطأ", "الاسم التجاري مطلوب")
                    return
            else:
                val, ok = QInputDialog.getInt(self, "إضافة دواء", label, *args)
                if not ok:
                    return
            values[key] = val

        try:
            expiry = date.fromisoformat(values["expiry_str"]) if values["expiry_str"] else None
        except ValueError:
            QMessageBox.warning(self, "خطأ", "صيغة التاريخ غير صحيحة (YYYY-MM-DD)")
            return

        add_drug(self.session, {
            "trade_name":      values["trade_name"].strip(),
            "scientific_name": values["scientific_name"].strip() or None,
            "category":        values["category"].strip() or "General",
            "quantity":        values["quantity"],
            "price":           values["price"],
            "expiry_date":     expiry,
        })
        self.session.expire_all()
        self.load_data()

    def _edit_drug(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "خطأ", "اختر دواء للتعديل من الجدول")
            return

        drug_id = int(self.table.item(row, 0).text())

        from database.models import Drug
        drug = self.session.get(Drug, drug_id)
        if not drug:
            QMessageBox.warning(self, "خطأ", "لم يُعثر على الدواء في قاعدة البيانات")
            return

        from ui.edit_drug_dialog import EditDrugDialog
        dialog = EditDrugDialog(self.session, drug, parent=self)
        dialog.setStyleSheet(self.styleSheet())

        if dialog.exec() == EditDrugDialog.DialogCode.Accepted:
            self.session.expire_all()
            self.load_data()
            self.statusBar().showMessage(f"✅ تم تعديل الدواء: {drug.trade_name}")

    def _delete_drug(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "خطأ", "اختر دواء للحذف")
            return
        drug_id   = int(self.table.item(row, 0).text())
        drug_name = self.table.item(row, 1).text()
        if QMessageBox.question(
            self, "تأكيد الحذف",
            f"هل تريد حذف الدواء:\n{drug_name}؟",
        ) == QMessageBox.StandardButton.Yes:
            delete_drug(self.session, drug_id)
            self.session.expire_all()
            self.load_data()

    def _show_alerts(self):
        self.session.expire_all()
        alerts = check_alerts(self.session)
        if not alerts:
            QMessageBox.information(self, "✅ التنبيهات", "كلشي تمام — لا توجد تنبيهات")
        else:
            QMessageBox.warning(self, "⚠️ تنبيهات مهمة", "\n".join(alerts))

    def _search(self):
        text = self.search_input.text().strip()
        if not text:
            self.session.expire_all()
            self.load_data()
            return
        self.session.expire_all()
        if text.isdigit() and len(text) == 13:
            drug  = search_drug_by_barcode(self.session, text)
            drugs = [drug] if drug else []
        else:
            drugs = search_drug(self.session, text)
        self.load_data(drugs)
        self.statusBar().showMessage(f"🔍 نتائج البحث عن '{text}': {len(drugs)} دواء")

    # ══════════════════════════════════════════════════════════════════════════
    # فتح النوافذ الأخرى
    # ══════════════════════════════════════════════════════════════════════════

    def _open_pos(self):
        from ui.pos_window import POSWindow
        self._pos = POSWindow(self.session, self.current_user)
        self._pos.setStyleSheet(DARK_STYLE)
        self._pos.show()

    def _open_reports(self):
        from ui.reports_window import ReportsWindow
        self._reports = ReportsWindow(self.session)
        self._reports.setStyleSheet(DARK_STYLE)
        self._reports.show()

    def _open_stats(self):
        from ui.stats_window import StatsWindow
        self._stats = StatsWindow(self.session)
        self._stats.setStyleSheet(DARK_STYLE)
        self._stats.show()

    def _open_barcode(self):
        from ui.barcode_window import BarcodeWindow
        self._barcode = BarcodeWindow(self.session)
        self._barcode.setStyleSheet(DARK_STYLE)
        self._barcode.show()

    def _open_interactions(self):
        from ui.interactions_window import InteractionsWindow
        self._interactions = InteractionsWindow(self.session)
        self._interactions.setStyleSheet(DARK_STYLE)
        self._interactions.show()

    def _open_suppliers(self):
        from ui.suppliers_window import SuppliersWindow
        self._suppliers = SuppliersWindow(self.session)
        self._suppliers.setStyleSheet(DARK_STYLE)
        self._suppliers.show()

    def _open_backup(self):
        from ui.backup_window import BackupWindow
        self._backup = BackupWindow()
        self._backup.setStyleSheet(DARK_STYLE)
        self._backup.show()

    def _open_users(self):
        from ui.users_window import UsersWindow
        self._users = UsersWindow(self.session)
        self._users.setStyleSheet(DARK_STYLE)
        self._users.show()

    def _open_change_password(self):
        from ui.change_password_window import ChangePasswordWindow
        self._chpass = ChangePasswordWindow(self.session, self.current_user)
        self._chpass.setStyleSheet(DARK_STYLE)
        self._chpass.show()

    def _logout(self):
        if QMessageBox.question(
            self, "تأكيد", "هل تريد تسجيل الخروج؟"
        ) == QMessageBox.StandardButton.Yes:
            self.timer.stop()
            self.close()
            from ui.login_window import LoginWindow

            def _on_success(user):
                self._new_win = MainWindow(self.session, user)
                self._new_win.show()

            self._login = LoginWindow(self.session, _on_success)
            self._login.show()
