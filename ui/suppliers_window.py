"""
PharmIQ — Suppliers Window (Screen 7)
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QSpinBox, QTabWidget, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)
from database.crud import (
    add_purchase_order, add_supplier, cancel_purchase_order,
    delete_supplier, get_all_purchase_orders, get_all_suppliers,
    receive_purchase_order, search_drug,
)
from logic.rtl_helper import apply_rtl
from ui.style import BTN_BLUE, BTN_GREEN, BTN_RED

class SuppliersWindow(QWidget):
    def __init__(self, session):
        super().__init__()
        self.session = session
        apply_rtl(self)
        self.setWindowTitle("🏭 إدارة الموردين")
        self.setGeometry(140, 90, 1050, 720)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(14, 14, 14, 14)
        title = QLabel("🏭 إدارة الموردين وطلبات التوريد")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #89b4fa; padding: 6px;")
        layout.addWidget(title)
        tabs = QTabWidget()
        layout.addWidget(tabs)
        t1 = QWidget(); apply_rtl(t1); tabs.addTab(t1, "🏭 الموردين"); self._build_sup_tab(t1)
        t2 = QWidget(); apply_rtl(t2); tabs.addTab(t2, "📦 طلبات التوريد"); self._build_ord_tab(t2)

    def _build_sup_tab(self, parent):
        layout = QVBoxLayout(parent)
        self.sup_table = QTableWidget()
        self.sup_table.setColumnCount(5)
        self.sup_table.setHorizontalHeaderLabels(["ID","الاسم","الهاتف","البريد","العنوان"])
        self.sup_table.horizontalHeader().setStretchLastSection(True)
        self.sup_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.sup_table)
        form = QHBoxLayout()
        self.sup_name=QLineEdit(); self.sup_name.setPlaceholderText("اسم المورد *")
        self.sup_phone=QLineEdit(); self.sup_phone.setPlaceholderText("الهاتف")
        self.sup_email=QLineEdit(); self.sup_email.setPlaceholderText("البريد")
        self.sup_addr=QLineEdit(); self.sup_addr.setPlaceholderText("العنوان")
        ab=QPushButton("➕ إضافة"); ab.setStyleSheet(BTN_GREEN); ab.clicked.connect(self._add_sup)
        db=QPushButton("❌ حذف"); db.setStyleSheet(BTN_RED); db.clicked.connect(self._del_sup)
        for w in (self.sup_name,self.sup_phone,self.sup_email,self.sup_addr,ab,db): form.addWidget(w)
        layout.addLayout(form)
        self._load_suppliers()

    def _load_suppliers(self):
        sups = get_all_suppliers(self.session)
        self.sup_table.setRowCount(len(sups))
        for r,s in enumerate(sups):
            self.sup_table.setItem(r,0,QTableWidgetItem(str(s.id)))
            self.sup_table.setItem(r,1,QTableWidgetItem(s.name))
            self.sup_table.setItem(r,2,QTableWidgetItem(s.phone or ""))
            self.sup_table.setItem(r,3,QTableWidgetItem(s.email or ""))
            self.sup_table.setItem(r,4,QTableWidgetItem(s.address or ""))

    def _add_sup(self):
        name=self.sup_name.text().strip()
        if not name: QMessageBox.warning(self,"خطأ","اسم المورد مطلوب"); return
        add_supplier(self.session,{"name":name,"phone":self.sup_phone.text().strip() or None,"email":self.sup_email.text().strip() or None,"address":self.sup_addr.text().strip() or None})
        for w in (self.sup_name,self.sup_phone,self.sup_email,self.sup_addr): w.clear()
        self._load_suppliers(); self._refresh_combo()

    def _del_sup(self):
        r=self.sup_table.currentRow()
        if r==-1: return
        sid=int(self.sup_table.item(r,0).text())
        if QMessageBox.question(self,"تأكيد","حذف المورد؟")==QMessageBox.StandardButton.Yes:
            delete_supplier(self.session,sid); self._load_suppliers(); self._refresh_combo()

    def _build_ord_tab(self, parent):
        layout = QVBoxLayout(parent)
        self.ord_table = QTableWidget()
        self.ord_table.setColumnCount(7)
        self.ord_table.setHorizontalHeaderLabels(["ID","المورد","الدواء","الكمية","السعر/وحدة","الكلي","الحالة"])
        self.ord_table.horizontalHeader().setStretchLastSection(True)
        self.ord_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.ord_table)
        layout.addWidget(QLabel("➕ طلب توريد جديد:"))
        form=QHBoxLayout()
        self.ord_cb=QComboBox(); self._refresh_combo()
        self.ord_drug=QLineEdit(); self.ord_drug.setPlaceholderText("اسم الدواء")
        self.ord_qty=QSpinBox(); self.ord_qty.setMinimum(1); self.ord_qty.setMaximum(99999)
        self.ord_cost=QLineEdit(); self.ord_cost.setPlaceholderText("سعر الوحدة")
        self.ord_notes=QLineEdit(); self.ord_notes.setPlaceholderText("ملاحظات")
        ab=QPushButton("📦 إرسال الطلب"); ab.setStyleSheet(BTN_BLUE); ab.clicked.connect(self._add_order)
        for w in (QLabel("المورد:"),self.ord_cb,self.ord_drug,QLabel("الكمية:"),self.ord_qty,QLabel("السعر:"),self.ord_cost,self.ord_notes,ab): form.addWidget(w)
        layout.addLayout(form)
        btns=QHBoxLayout(); btns.addStretch()
        rb=QPushButton("✅ استلام"); rb.setStyleSheet(BTN_GREEN); rb.clicked.connect(self._recv)
        cb=QPushButton("❌ إلغاء"); cb.setStyleSheet(BTN_RED); cb.clicked.connect(self._cancel)
        btns.addWidget(rb); btns.addWidget(cb); layout.addLayout(btns)
        self._load_orders()

    def _refresh_combo(self):
        if not hasattr(self,"ord_cb"): return
        self.ord_cb.clear()
        for s in get_all_suppliers(self.session): self.ord_cb.addItem(s.name,s.id)

    def _load_orders(self):
        orders=get_all_purchase_orders(self.session)
        self.ord_table.setRowCount(len(orders))
        colors={"pending":"#3d2a00","received":"#1a2e1a","cancelled":"#2a1020"}
        for r,o in enumerate(orders):
            sn=o.supplier.name if o.supplier else "—"
            dn=o.drug.trade_name if o.drug else "—"
            self.ord_table.setItem(r,0,QTableWidgetItem(str(o.id)))
            self.ord_table.setItem(r,1,QTableWidgetItem(sn))
            self.ord_table.setItem(r,2,QTableWidgetItem(dn))
            self.ord_table.setItem(r,3,QTableWidgetItem(str(o.quantity)))
            self.ord_table.setItem(r,4,QTableWidgetItem(f"{o.cost_per_unit:,.0f}"))
            self.ord_table.setItem(r,5,QTableWidgetItem(f"{o.total_cost:,.0f}"))
            self.ord_table.setItem(r,6,QTableWidgetItem(o.status))
            bg=colors.get(o.status,"#313244")
            for c in range(7):
                item=self.ord_table.item(r,c)
                if item: item.setBackground(QColor(bg))

    def _add_order(self):
        if self.ord_cb.count()==0: QMessageBox.warning(self,"خطأ","أضف موردين أولاً"); return
        dn=self.ord_drug.text().strip()
        if not dn: QMessageBox.warning(self,"خطأ","أدخل اسم الدواء"); return
        try: cost=float(self.ord_cost.text())
        except: QMessageBox.warning(self,"خطأ","أدخل سعراً صحيحاً"); return
        drugs=search_drug(self.session,dn)
        if not drugs: QMessageBox.warning(self,"خطأ",f"لم يُعثر على: {dn}"); return
        add_purchase_order(self.session,self.ord_cb.currentData(),drugs[0].id,self.ord_qty.value(),cost,self.ord_notes.text())
        self.ord_drug.clear(); self.ord_cost.clear(); self.ord_notes.clear()
        self._load_orders(); QMessageBox.information(self,"✅ تم","تم إرسال طلب التوريد")

    def _recv(self):
        r=self.ord_table.currentRow()
        if r==-1: return
        oid=int(self.ord_table.item(r,0).text())
        if receive_purchase_order(self.session,oid):
            QMessageBox.information(self,"✅ تم","تم الاستلام وإضافة الكمية للمخزون")
            self.session.expire_all(); self._load_orders()
        else: QMessageBox.warning(self,"خطأ","تعذّر الاستلام")

    def _cancel(self):
        r=self.ord_table.currentRow()
        if r==-1: return
        oid=int(self.ord_table.item(r,0).text())
        if cancel_purchase_order(self.session,oid): self._load_orders()
