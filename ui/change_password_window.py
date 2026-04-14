"""PharmIQ — Change Password Window"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QLabel,QLineEdit,QMessageBox,QPushButton,QVBoxLayout,QWidget)
from database.models import User
from logic.rtl_helper import apply_rtl
from ui.style import BTN_BLUE

class ChangePasswordWindow(QWidget):
    def __init__(self, session, user):
        super().__init__()
        self.session=session; self.user=user
        apply_rtl(self)
        self.setWindowTitle("🔒 تغيير كلمة المرور")
        self.setGeometry(450,290,390,340); self.setFixedSize(390,340)
        layout=QVBoxLayout(self)
        layout.setSpacing(12); layout.setContentsMargins(30,30,30,30)
        title=QLabel("🔒 تغيير كلمة المرور")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial",14,QFont.Weight.Bold))
        title.setStyleSheet("color: #89b4fa; padding: 8px;")
        layout.addWidget(title)
        def lbl(t): l=QLabel(t); l.setStyleSheet("color:#cdd6f4;"); return l
        def fld(ph,pw=False):
            f=QLineEdit(); f.setPlaceholderText(ph); f.setMinimumHeight(38)
            if pw: f.setEchoMode(QLineEdit.EchoMode.Password)
            return f
        layout.addWidget(lbl("كلمة المرور الحالية:"))
        self.old=fld("أدخل كلمة المرور الحالية",True); layout.addWidget(self.old)
        layout.addWidget(lbl("كلمة المرور الجديدة:"))
        self.new=fld("6 أحرف على الأقل",True); layout.addWidget(self.new)
        layout.addWidget(lbl("تأكيد كلمة المرور الجديدة:"))
        self.conf=fld("أعد كتابة كلمة المرور الجديدة",True)
        self.conf.returnPressed.connect(self._save); layout.addWidget(self.conf)
        btn=QPushButton("💾 حفظ")
        btn.setMinimumHeight(42); btn.setStyleSheet(BTN_BLUE); btn.clicked.connect(self._save); layout.addWidget(btn)
        self.msg=QLabel(""); self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg.setStyleSheet("color:#f38ba8; font-size:12px;"); layout.addWidget(self.msg)

    def _save(self):
        o=self.old.text(); n=self.new.text(); c=self.conf.text()
        if not o or not n or not c: self.msg.setText("⚠️ أكمل جميع الحقول"); return
        if not self.user.check_password(o): self.msg.setText("❌ كلمة المرور الحالية غير صحيحة"); return
        if len(n)<6: self.msg.setText("⚠️ كلمة المرور لازم تكون 6 أحرف على الأقل"); return
        if n!=c: self.msg.setText("❌ كلمتا المرور غير متطابقتين"); return
        self.user.password=User.hash_password(n); self.session.commit()
        QMessageBox.information(self,"✅ تم","تم تغيير كلمة المرور بنجاح"); self.close()
