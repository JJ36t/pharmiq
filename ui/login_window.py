"""
PharmIQ — Login Window (Screen 8 partial / Auth)
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget,
)

from database.crud import create_user, get_all_users, login_user
from logic.rtl_helper import apply_rtl


class LoginWindow(QWidget):
    def __init__(self, session, on_login_success):
        super().__init__()
        self.session          = session
        self.on_login_success = on_login_success

        apply_rtl(self)
        self.setWindowTitle("PharmIQ — تسجيل الدخول")
        self.setGeometry(430, 260, 420, 500)
        self.setFixedSize(420, 500)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(45, 45, 45, 45)
        self.setLayout(layout)

        # ── شعار ────────────────────────────────────────────────────────────
        logo = QLabel("💊")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFont(QFont("Arial", 52))
        layout.addWidget(logo)

        title = QLabel("PharmIQ")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #89b4fa;")
        layout.addWidget(title)

        sub = QLabel("نظام إدارة الصيدلية الذكي")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet("color: #6c7086; font-size: 12px;")
        layout.addWidget(sub)

        layout.addSpacing(20)

        # ── حقل المستخدم ────────────────────────────────────────────────────
        layout.addWidget(self._label("👤 اسم المستخدم"))
        self.username_input = self._field("أدخل اسم المستخدم...")
        self.username_input.returnPressed.connect(self.login)
        layout.addWidget(self.username_input)

        # ── حقل كلمة المرور ─────────────────────────────────────────────────
        layout.addWidget(self._label("🔒 كلمة المرور"))
        self.password_input = self._field("أدخل كلمة المرور...")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.login)
        layout.addWidget(self.password_input)

        layout.addSpacing(10)

        # ── زر الدخول ───────────────────────────────────────────────────────
        self.login_btn = QPushButton("🚀 دخول")
        self.login_btn.setMinimumHeight(46)
        self.login_btn.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa; color: #1e1e2e;
                border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover   { background-color: #74c7ec; }
            QPushButton:pressed { background-color: #cba6f7; }
        """)
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)

        # ── رسالة الخطأ ─────────────────────────────────────────────────────
        self.error_lbl = QLabel("")
        self.error_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_lbl.setStyleSheet("color: #f38ba8; font-size: 12px;")
        layout.addWidget(self.error_lbl)

        layout.addStretch()

        # ── admin افتراضي ────────────────────────────────────────────────────
        if not get_all_users(self.session):
            create_user(self.session, "admin", "admin123", "admin")

    # ── helpers ─────────────────────────────────────────────────────────────
    @staticmethod
    def _label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #cdd6f4; font-size: 13px;")
        return lbl

    @staticmethod
    def _field(placeholder: str) -> QLineEdit:
        f = QLineEdit()
        f.setPlaceholderText(placeholder)
        f.setMinimumHeight(40)
        return f

    # ── منطق الدخول ─────────────────────────────────────────────────────────
    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.error_lbl.setText("⚠️ أدخل اسم المستخدم وكلمة المرور")
            return

        user, error = login_user(self.session, username, password)
        if error:
            self.error_lbl.setText(f"❌ {error}")
            self.password_input.clear()
            return

        self.on_login_success(user)
        self.close()
