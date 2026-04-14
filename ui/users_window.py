"""PharmIQ — Users Window (Screen 8: User Management)"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QComboBox,QHBoxLayout,QLabel,QLineEdit,QMessageBox,QPushButton,QTableWidget,QTableWidgetItem,QVBoxLayout,QWidget)
from database.crud import create_user, delete_user, get_all_users
from logic.rtl_helper import apply_rtl
from ui.style import BTN_GREEN, BTN_RED

class UsersWindow(QWidget):
    def __init__(self, session):
        super().__init__()
        self.session = session
        apply_rtl(self)
        self.setWindowTitle("👥 إدارة المستخدمين")
        self.setGeometry(250, 190, 660, 480)
        layout = QVBoxLayout(self)
        layout.setSpacing(10); layout.setContentsMargins(15,15,15,15)
        title = QLabel("👥 إدارة المستخدمين والصلاحيات")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial",15,QFont.Weight.Bold))
        title.setStyleSheet("color: #89b4fa; padding: 8px;")
        layout.addWidget(title)
        self.table = QTableWidget()
        self.table.setColumnCount(4); self.table.setHorizontalHeaderLabels(["ID","اسم المستخدم","الصلاحية","آخر دخول"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        form = QHBoxLayout()
        self.un_input = QLineEdit(); self.un_input.setPlaceholderText("اسم المستخدم")
        self.pw_input = QLineEdit(); self.pw_input.setPlaceholderText("كلمة المرور"); self.pw_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.role_cb  = QComboBox(); self.role_cb.addItems(["cashier","admin"])
        ab = QPushButton("➕ إضافة"); ab.setStyleSheet(BTN_GREEN); ab.clicked.connect(self._add)
        db = QPushButton("❌ حذف");  db.setStyleSheet(BTN_RED);   db.clicked.connect(self._delete)
        for w in (self.un_input,self.pw_input,self.role_cb,ab,db): form.addWidget(w)
        layout.addLayout(form)
        self._load()

    def _load(self):
        users = get_all_users(self.session)
        self.table.setRowCount(len(users))
        for r,u in enumerate(users):
            self.table.setItem(r,0,QTableWidgetItem(str(u.id)))
            self.table.setItem(r,1,QTableWidgetItem(u.username))
            self.table.setItem(r,2,QTableWidgetItem(u.role))
            ll = u.last_login.strftime("%Y-%m-%d %H:%M") if u.last_login else "—"
            self.table.setItem(r,3,QTableWidgetItem(ll))

    def _add(self):
        un=self.un_input.text().strip(); pw=self.pw_input.text().strip()
        if not un or not pw: QMessageBox.warning(self,"خطأ","أدخل الاسم وكلمة المرور"); return
        user,err=create_user(self.session,un,pw,self.role_cb.currentText())
        if err: QMessageBox.warning(self,"خطأ",err); return
        self.un_input.clear(); self.pw_input.clear(); self._load()
        QMessageBox.information(self,"✅ تم","تم إضافة المستخدم")

    def _delete(self):
        r=self.table.currentRow()
        if r==-1: return
        uid=int(self.table.item(r,0).text()); un=self.table.item(r,1).text()
        if un=="admin": QMessageBox.warning(self,"خطأ","لا يمكن حذف الأدمن الرئيسي"); return
        if QMessageBox.question(self,"تأكيد",f"حذف {un}؟")==QMessageBox.StandardButton.Yes:
            delete_user(self.session,uid); self._load()
