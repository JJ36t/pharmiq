"""
PharmIQ — Edit Drug Dialog
نافذة تعديل شاملة لكل بيانات الدواء
"""

from datetime import date

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox, QDateEdit, QDialog, QDialogButtonBox,
    QDoubleSpinBox, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QMessageBox, QSpinBox, QVBoxLayout,
)

from database.crud import update_drug

# فئات الأدوية الشائعة
DRUG_CATEGORIES = [
    "Analgesics", "Antibiotics", "Antihistamines", "Cardiovascular",
    "Diabetes", "Gastrointestinal", "Neurology", "Psychiatry",
    "Respiratory", "Steroids", "Vitamins", "General", "Other",
]


class EditDrugDialog(QDialog):
    """
    نافذة تعديل كاملة لكل حقول الدواء:
    - الاسم التجاري والعلمي
    - الفئة الدوائية
    - الكمية والحد الأدنى
    - السعر
    - تاريخ الصلاحية
    - الباركود
    """

    def __init__(self, session, drug, parent=None):
        super().__init__(parent)
        self.session = session
        self.drug    = drug

        self.setWindowTitle(f"✏️ تعديل الدواء — {drug.trade_name}")
        self.setMinimumWidth(520)
        self.setModal(True)

        self._build_ui()
        self._populate_fields()

    # ══════════════════════════════════════════════════════════════════════════
    # بناء الواجهة
    # ══════════════════════════════════════════════════════════════════════════

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        # ── عنوان ─────────────────────────────────────────────────────────
        title = QLabel(f"✏️ تعديل: {self.drug.trade_name}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #89b4fa; padding: 6px;")
        layout.addWidget(title)

        # ── مجموعة: معلومات الدواء ────────────────────────────────────────
        info_group = QGroupBox("💊 معلومات الدواء")
        info_group.setStyleSheet("QGroupBox { color: #89b4fa; font-weight: bold; border: 1px solid #45475a; border-radius: 6px; padding-top: 10px; }")
        info_form = QFormLayout(info_group)
        info_form.setSpacing(10)
        info_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.trade_name_input = QLineEdit()
        self.trade_name_input.setMinimumHeight(36)
        self.trade_name_input.setPlaceholderText("الاسم التجاري للدواء...")

        self.scientific_name_input = QLineEdit()
        self.scientific_name_input.setMinimumHeight(36)
        self.scientific_name_input.setPlaceholderText("الاسم العلمي (INN)...")

        self.category_combo = QComboBox()
        self.category_combo.setMinimumHeight(36)
        self.category_combo.setEditable(True)
        self.category_combo.addItems(DRUG_CATEGORIES)

        self.barcode_input = QLineEdit()
        self.barcode_input.setMinimumHeight(36)
        self.barcode_input.setPlaceholderText("EAN-13 (13 رقم)...")
        self.barcode_input.setMaxLength(13)

        info_form.addRow(self._lbl("الاسم التجاري *:"),   self.trade_name_input)
        info_form.addRow(self._lbl("الاسم العلمي:"),       self.scientific_name_input)
        info_form.addRow(self._lbl("الفئة الدوائية:"),     self.category_combo)
        info_form.addRow(self._lbl("الباركود EAN-13:"),    self.barcode_input)
        layout.addWidget(info_group)

        # ── مجموعة: المخزون والسعر ────────────────────────────────────────
        stock_group = QGroupBox("📦 المخزون والسعر")
        stock_group.setStyleSheet("QGroupBox { color: #a6e3a1; font-weight: bold; border: 1px solid #45475a; border-radius: 6px; padding-top: 10px; }")
        stock_form = QFormLayout(stock_group)
        stock_form.setSpacing(10)
        stock_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimumHeight(36)
        self.quantity_spin.setRange(0, 999999)
        self.quantity_spin.setSuffix("  وحدة")

        self.min_quantity_spin = QSpinBox()
        self.min_quantity_spin.setMinimumHeight(36)
        self.min_quantity_spin.setRange(0, 9999)
        self.min_quantity_spin.setSuffix("  وحدة")

        self.price_spin = QDoubleSpinBox()
        self.price_spin.setMinimumHeight(36)
        self.price_spin.setRange(0, 99_999_999)
        self.price_spin.setDecimals(0)
        self.price_spin.setSingleStep(500)
        self.price_spin.setSuffix("  IQD")

        stock_form.addRow(self._lbl("الكمية الحالية:"),  self.quantity_spin)
        stock_form.addRow(self._lbl("الحد الأدنى:"),      self.min_quantity_spin)
        stock_form.addRow(self._lbl("السعر:"),            self.price_spin)
        layout.addWidget(stock_group)

        # ── مجموعة: تاريخ الصلاحية ────────────────────────────────────────
        exp_group = QGroupBox("📅 تاريخ الصلاحية")
        exp_group.setStyleSheet("QGroupBox { color: #fab387; font-weight: bold; border: 1px solid #45475a; border-radius: 6px; padding-top: 10px; }")
        exp_form = QFormLayout(exp_group)
        exp_form.setSpacing(10)
        exp_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.expiry_edit = QDateEdit()
        self.expiry_edit.setMinimumHeight(36)
        self.expiry_edit.setCalendarPopup(True)
        self.expiry_edit.setDisplayFormat("yyyy-MM-dd")
        self.expiry_edit.setMinimumDate(date.today().__class__(2020, 1, 1))

        # تلوين التحذير
        self.expiry_status = QLabel("")
        self.expiry_status.setStyleSheet("font-size: 12px; padding: 3px;")
        self.expiry_edit.dateChanged.connect(self._update_expiry_status)

        exp_h = QHBoxLayout()
        exp_h.addWidget(self.expiry_edit)
        exp_h.addWidget(self.expiry_status)

        exp_form.addRow(self._lbl("تاريخ الانتهاء:"), exp_h)
        layout.addWidget(exp_group)

        # ── أزرار ─────────────────────────────────────────────────────────
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("💾 حفظ التعديلات")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("إلغاء")
        buttons.button(QDialogButtonBox.StandardButton.Save).setStyleSheet(
            "background-color: #a6e3a1; color: #1e1e2e; font-weight: bold; padding: 6px 20px; border-radius: 6px;"
        )
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setStyleSheet(
            "background-color: #f38ba8; color: #1e1e2e; font-weight: bold; padding: 6px 20px; border-radius: 6px;"
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # ══════════════════════════════════════════════════════════════════════════
    # ملء الحقول بالبيانات الحالية
    # ══════════════════════════════════════════════════════════════════════════

    def _populate_fields(self):
        self.trade_name_input.setText(self.drug.trade_name or "")
        self.scientific_name_input.setText(self.drug.scientific_name or "")

        # الفئة
        cat = self.drug.category or "General"
        idx = self.category_combo.findText(cat)
        if idx >= 0:
            self.category_combo.setCurrentIndex(idx)
        else:
            self.category_combo.setCurrentText(cat)

        self.barcode_input.setText(self.drug.barcode or "")
        self.quantity_spin.setValue(self.drug.quantity or 0)
        self.min_quantity_spin.setValue(self.drug.min_quantity or 5)
        self.price_spin.setValue(self.drug.price or 0)

        # تاريخ الصلاحية
        if self.drug.expiry_date:
            from PyQt6.QtCore import QDate
            qd = QDate(self.drug.expiry_date.year,
                       self.drug.expiry_date.month,
                       self.drug.expiry_date.day)
            self.expiry_edit.setDate(qd)
        else:
            from PyQt6.QtCore import QDate
            self.expiry_edit.setDate(QDate.currentDate().addYears(1))

        self._update_expiry_status()

    # ══════════════════════════════════════════════════════════════════════════
    # تحديث حالة تاريخ الصلاحية
    # ══════════════════════════════════════════════════════════════════════════

    def _update_expiry_status(self):
        from PyQt6.QtCore import QDate
        today   = QDate.currentDate()
        expiry  = self.expiry_edit.date()
        days    = today.daysTo(expiry)

        if days <= 0:
            self.expiry_status.setText("🔴 منتهي الصلاحية!")
            self.expiry_status.setStyleSheet("color: #f38ba8; font-size: 12px;")
        elif days <= 30:
            self.expiry_status.setText(f"⚠️ ينتهي خلال {days} يوم")
            self.expiry_status.setStyleSheet("color: #fab387; font-size: 12px;")
        elif days <= 90:
            self.expiry_status.setText(f"📅 ينتهي خلال {days} يوم")
            self.expiry_status.setStyleSheet("color: #f9e2af; font-size: 12px;")
        else:
            self.expiry_status.setText(f"✅ صالح ({days} يوم)")
            self.expiry_status.setStyleSheet("color: #a6e3a1; font-size: 12px;")

    # ══════════════════════════════════════════════════════════════════════════
    # حفظ التعديلات
    # ══════════════════════════════════════════════════════════════════════════

    def _save(self):
        trade_name = self.trade_name_input.text().strip()
        if not trade_name:
            QMessageBox.warning(self, "خطأ", "الاسم التجاري مطلوب ولا يمكن أن يكون فارغاً")
            self.trade_name_input.setFocus()
            return

        # تحويل تاريخ QDate إلى Python date
        qd = self.expiry_edit.date()
        expiry = date(qd.year(), qd.month(), qd.day())

        # التحقق من الباركود
        barcode = self.barcode_input.text().strip() or None
        if barcode and len(barcode) != 13:
            QMessageBox.warning(self, "خطأ", "الباركود يجب أن يكون 13 رقماً بالضبط")
            self.barcode_input.setFocus()
            return

        data = {
            "trade_name":      trade_name,
            "scientific_name": self.scientific_name_input.text().strip() or None,
            "category":        self.category_combo.currentText().strip() or "General",
            "barcode":         barcode,
            "quantity":        self.quantity_spin.value(),
            "min_quantity":    self.min_quantity_spin.value(),
            "price":           self.price_spin.value(),
            "expiry_date":     expiry,
        }

        update_drug(self.session, self.drug.id, data)
        self.accept()

    # ── helper ───────────────────────────────────────────────────────────────
    @staticmethod
    def _lbl(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #cdd6f4; font-size: 13px;")
        return lbl
