"""
PharmIQ — Stats Window (Screen 1: Dashboard)
لوحة الإحصائيات اللحظية مع تحديث تلقائي
"""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget,
)

from database.crud import (
    get_all_drugs, get_all_sales,
    get_today_revenue, get_today_sales,
)
from logic.rtl_helper import apply_rtl


class StatsWindow(QWidget):
    def __init__(self, session):
        super().__init__()
        self.session = session
        apply_rtl(self)

        self.setWindowTitle("📊 لوحة الإحصائيات — PharmIQ Dashboard")
        self.setGeometry(180, 120, 780, 560)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("📊 لوحة الإحصائيات اللحظية")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #89b4fa; padding: 8px;")
        layout.addWidget(title)

        self.grid = QGridLayout()
        self.grid.setSpacing(15)
        layout.addLayout(self.grid)

        self.load_stats()

        # تحديث كل 10 ثواني
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_stats)
        self.timer.start(10_000)

    def load_stats(self):
        # مسح الكاردات القديمة
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.session.expire_all()
        drugs         = get_all_drugs(self.session)
        all_sales     = get_all_sales(self.session)
        today_sales   = get_today_sales(self.session)
        today_rev     = get_today_revenue(self.session)
        total_rev     = sum(s.total_price for s in all_sales)
        inv_value     = sum(d.quantity * d.price for d in drugs)
        low_stock     = [d for d in drugs if d.is_low_stock]
        expiring_soon = [d for d in drugs if d.is_expiring_soon]
        expired       = [d for d in drugs if d.is_expired]

        cards = [
            # (عنوان, قيمة, لون, تفصيل)
            ("💊 إجمالي الأدوية",     str(len(drugs)),           "#89b4fa", "صنف دوائي"),
            ("🛒 مبيعات اليوم",       str(len(today_sales)),      "#a6e3a1", "عملية بيع"),
            ("💰 إيرادات اليوم",      f"{today_rev:,.0f}",        "#f9e2af", "دينار عراقي"),
            ("💵 الإيرادات الكلية",   f"{total_rev:,.0f}",        "#94e2d5", "دينار عراقي"),
            ("🏪 قيمة المخزون",       f"{inv_value:,.0f}",        "#cba6f7", "دينار عراقي"),
            ("📈 إجمالي المبيعات",    str(len(all_sales)),        "#89dceb", "عملية"),
            ("⚠️ مخزون قليل",        str(len(low_stock)),        "#fab387", "يحتاج طلب"),
            ("🔴 ينتهي قريباً",       str(len(expiring_soon)),    "#f38ba8", "خلال 30 يوم"),
            ("☠️ منتهي الصلاحية",    str(len(expired)),          "#f38ba8", "أزله فوراً"),
        ]

        for i, (title, value, color, sub) in enumerate(cards):
            card = self._make_card(title, value, color, sub)
            self.grid.addWidget(card, i // 3, i % 3)

    def _make_card(self, title: str, value: str, color: str, sub: str) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: #313244;
                border-radius: 12px;
                border: 2px solid {color};
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setSpacing(4)

        t = QLabel(title)
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t.setStyleSheet("color: #cdd6f4; font-size: 12px; border: none;")
        layout.addWidget(t)

        v = QLabel(value)
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        v.setStyleSheet(f"color: {color}; border: none;")
        layout.addWidget(v)

        s = QLabel(sub)
        s.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s.setStyleSheet("color: #6c7086; font-size: 10px; border: none;")
        layout.addWidget(s)

        return frame
