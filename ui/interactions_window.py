"""
PharmIQ — Drug Interactions Window (Screen 4)
فاحص التفاعلات الدوائية — مع ترتيب حسب الخطورة ودعم recommendation
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from database.crud import (
    add_interaction, check_interactions,
    delete_interaction, get_all_interactions,
)
from logic.rtl_helper import apply_rtl
from ui.style import BTN_GREEN, BTN_RED, BTN_YELLOW


# ألوان مستويات الخطورة
SEVERITY_COLORS = {
    "High":   ("#4a1020", "#f38ba8"),   # (خلفية, نص)
    "Medium": ("#3d2a00", "#f9e2af"),
    "Low":    ("#1a2e1a", "#a6e3a1"),
}
SEVERITY_AR = {"High": "خطير 🔴", "Medium": "متوسط 🟠", "Low": "خفيف 🟡"}


class InteractionsWindow(QWidget):
    def __init__(self, session):
        super().__init__()
        self.session = session
        apply_rtl(self)

        self.setWindowTitle("⚠️ تفاعلات الأدوية")
        self.setGeometry(180, 110, 980, 700)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("⚠️ فاحص التفاعلات الدوائية")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #f38ba8; padding: 8px;")
        layout.addWidget(title)

        # ── فحص سريع ─────────────────────────────────────────────────────
        check_row = QHBoxLayout()
        self.d1_input = QLineEdit()
        self.d1_input.setPlaceholderText("الدواء الأول...")
        self.d2_input = QLineEdit()
        self.d2_input.setPlaceholderText("الدواء الثاني...")
        self.d3_input = QLineEdit()
        self.d3_input.setPlaceholderText("الدواء الثالث (اختياري)...")
        check_btn = QPushButton("🔍 فحص التفاعلات")
        check_btn.setStyleSheet(BTN_YELLOW)
        check_btn.clicked.connect(self._check)
        self.d1_input.returnPressed.connect(self._check)
        self.d2_input.returnPressed.connect(self._check)

        check_row.addWidget(QLabel("فحص سريع:"))
        check_row.addWidget(self.d1_input)
        check_row.addWidget(self.d2_input)
        check_row.addWidget(self.d3_input)
        check_row.addWidget(check_btn)
        layout.addLayout(check_row)

        # نتيجة الفحص
        self.check_result = QLabel("")
        self.check_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.check_result.setWordWrap(True)
        self.check_result.setStyleSheet(
            "font-size: 13px; padding: 8px; border-radius: 6px;"
        )
        layout.addWidget(self.check_result)

        # ── جدول التفاعلات ────────────────────────────────────────────────
        layout.addWidget(QLabel("📋 قاعدة بيانات التفاعلات الدوائية:"))
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["الدواء أ", "الدواء ب", "الخطورة", "الوصف", "التوصية"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        # ── نموذج الإضافة ────────────────────────────────────────────────
        layout.addWidget(QLabel("➕ إضافة تفاعل جديد:"))
        add_row = QHBoxLayout()
        self.new_d1   = QLineEdit(); self.new_d1.setPlaceholderText("الدواء أ")
        self.new_d2   = QLineEdit(); self.new_d2.setPlaceholderText("الدواء ب")
        self.sev_cb   = QComboBox(); self.sev_cb.addItems(["High", "Medium", "Low"])
        self.new_desc = QLineEdit(); self.new_desc.setPlaceholderText("وصف التفاعل...")
        self.new_rec  = QLineEdit(); self.new_rec.setPlaceholderText("التوصية...")

        add_btn = QPushButton("➕ إضافة")
        add_btn.setStyleSheet(BTN_GREEN)
        add_btn.clicked.connect(self._add)

        del_btn = QPushButton("❌ حذف المحدد")
        del_btn.setStyleSheet(BTN_RED)
        del_btn.clicked.connect(self._delete)

        for w in (self.new_d1, self.new_d2, self.sev_cb,
                  self.new_desc, self.new_rec, add_btn, del_btn):
            add_row.addWidget(w)
        layout.addLayout(add_row)

        self._load_table()

    def _load_table(self):
        interactions = get_all_interactions(self.session)
        self.table.setRowCount(len(interactions))
        for row, inter in enumerate(interactions):
            sev_ar = SEVERITY_AR.get(inter.severity, inter.severity)
            bg, fg = SEVERITY_COLORS.get(inter.severity, ("#313244", "#cdd6f4"))

            self.table.setItem(row, 0, QTableWidgetItem(inter.drug_a or ""))
            self.table.setItem(row, 1, QTableWidgetItem(inter.drug_b or ""))
            self.table.setItem(row, 2, QTableWidgetItem(sev_ar))
            self.table.setItem(row, 3, QTableWidgetItem(inter.description or ""))
            self.table.setItem(row, 4, QTableWidgetItem(inter.recommendation or ""))

            for col in range(5):
                item = self.table.item(row, col)
                if item:
                    item.setBackground(QColor(bg))
                    item.setForeground(QColor(fg))

    def _check(self):
        names = [
            self.d1_input.text().strip(),
            self.d2_input.text().strip(),
            self.d3_input.text().strip(),
        ]
        names = [n for n in names if n]
        if len(names) < 2:
            self.check_result.setText("أدخل دوائين على الأقل للفحص")
            self.check_result.setStyleSheet("color: #6c7086; padding: 8px;")
            return

        warnings = check_interactions(self.session, names)
        if not warnings:
            self.check_result.setText("✅ لا يوجد تفاعل معروف بين هذه الأدوية")
            self.check_result.setStyleSheet(
                "color: #a6e3a1; background-color: #1a2e1a; padding: 8px; border-radius: 6px;"
            )
        else:
            lines = []
            for w in warnings:
                sev_ar = SEVERITY_AR.get(w["severity"], w["severity"])
                lines.append(f"⚠️ {sev_ar}: {w['pair']}")
                lines.append(f"   📋 {w['description']}")
                if w.get("recommendation"):
                    lines.append(f"   💡 {w['recommendation']}")
                lines.append("")
            self.check_result.setText("\n".join(lines).strip())
            self.check_result.setStyleSheet(
                "color: #f38ba8; background-color: #2a1020; padding: 8px; border-radius: 6px;"
            )

    def _add(self):
        d1  = self.new_d1.text().strip()
        d2  = self.new_d2.text().strip()
        if not d1 or not d2:
            QMessageBox.warning(self, "خطأ", "أدخل اسمي الدوائين")
            return
        add_interaction(
            self.session, d1, d2,
            self.sev_cb.currentText(),
            self.new_desc.text().strip(),
            self.new_rec.text().strip(),
        )
        self.new_d1.clear(); self.new_d2.clear()
        self.new_desc.clear(); self.new_rec.clear()
        self._load_table()

    def _delete(self):
        row = self.table.currentRow()
        if row == -1:
            return
        interactions = get_all_interactions(self.session)
        if row < len(interactions):
            delete_interaction(self.session, interactions[row].id)
            self._load_table()
