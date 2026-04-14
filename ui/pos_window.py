"""
PharmIQ — POS Window (Screen 3: Point of Sale)
نظام البيع — بحث + سلة + فاتورة PDF تلقائية
"""

import os

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from database.crud import get_all_sales, search_drug, search_drug_by_barcode, sell_drug
from logic.rtl_helper import apply_rtl
from reports.invoice import generate_invoice
from ui.style import BTN_GREEN, BTN_RED


class POSWindow(QWidget):
    def __init__(self, session, user=None):
        super().__init__()
        self.session = session
        self.user    = user
        self.cart    = []
        self.total   = 0.0

        apply_rtl(self)
        self.setWindowTitle("🛒 نظام البيع — POS")
        self.setGeometry(140, 100, 1000, 680)

        layout = QVBoxLayout(self)
        layout.setSpacing(9)
        layout.setContentsMargins(14, 14, 14, 14)

        title = QLabel("🛒 نظام البيع — Point of Sale")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #89b4fa; padding: 6px;")
        layout.addWidget(title)

        # بحث
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 ابحث عن دواء بالاسم أو الباركود...")
        self.search_input.setMinimumHeight(38)
        self.search_input.returnPressed.connect(self._search)
        s_btn = QPushButton("🔍 بحث")
        s_btn.clicked.connect(self._search)
        search_row.addWidget(self.search_input)
        search_row.addWidget(s_btn)
        layout.addLayout(search_row)

        layout.addWidget(QLabel("📋 نتائج البحث:"))
        self.search_table = QTableWidget()
        self.search_table.setColumnCount(5)
        self.search_table.setHorizontalHeaderLabels(
            ["ID", "الاسم التجاري", "الفئة", "الكمية المتوفرة", "السعر (IQD)"]
        )
        self.search_table.setMaximumHeight(170)
        self.search_table.horizontalHeader().setStretchLastSection(True)
        self.search_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.search_table)

        # إضافة للسلة
        add_row = QHBoxLayout()
        add_row.addWidget(QLabel("الكمية:"))
        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("1")
        self.qty_input.setMaximumWidth(120)
        self.qty_input.setMinimumHeight(36)
        self.qty_input.returnPressed.connect(self._add_to_cart)
        add_btn = QPushButton("➕ أضف للسلة")
        add_btn.setStyleSheet(BTN_GREEN)
        add_btn.setMinimumHeight(36)
        add_btn.clicked.connect(self._add_to_cart)
        add_row.addWidget(self.qty_input)
        add_row.addWidget(add_btn)
        add_row.addStretch()
        layout.addLayout(add_row)

        # السلة
        layout.addWidget(QLabel("🛒 السلة:"))
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(
            ["#", "الدواء", "الكمية", "السعر الفردي", "المجموع (IQD)"]
        )
        self.cart_table.horizontalHeader().setStretchLastSection(True)
        self.cart_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.cart_table)

        # شريط أسفل
        bottom = QHBoxLayout()
        self.total_lbl = QLabel("💰 المجموع: 0 IQD")
        self.total_lbl.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        self.total_lbl.setStyleSheet("color: #f9e2af;")

        rem_btn = QPushButton("🗑️ حذف من السلة")
        rem_btn.setStyleSheet(BTN_RED)
        rem_btn.clicked.connect(self._remove_from_cart)

        clr_btn = QPushButton("🧹 مسح السلة")
        clr_btn.clicked.connect(self._clear_cart)

        self.sell_btn = QPushButton("✅ إتمام البيع وطباعة الفاتورة")
        self.sell_btn.setStyleSheet(BTN_GREEN)
        self.sell_btn.setMinimumHeight(42)
        self.sell_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.sell_btn.clicked.connect(self._complete_sale)

        bottom.addWidget(self.total_lbl)
        bottom.addStretch()
        bottom.addWidget(rem_btn)
        bottom.addWidget(clr_btn)
        bottom.addWidget(self.sell_btn)
        layout.addLayout(bottom)

        self.timer = QTimer()
        self.timer.timeout.connect(self._auto_refresh)
        self.timer.start(3000)

    def _search(self):
        name = self.search_input.text().strip()
        if not name:
            return
        self.session.expire_all()
        if name.isdigit() and len(name) == 13:
            drug    = search_drug_by_barcode(self.session, name)
            results = [drug] if drug else []
        else:
            results = search_drug(self.session, name)
        self.search_table.setRowCount(len(results))
        for row, drug in enumerate(results):
            self.search_table.setItem(row, 0, QTableWidgetItem(str(drug.id)))
            self.search_table.setItem(row, 1, QTableWidgetItem(drug.trade_name))
            self.search_table.setItem(row, 2, QTableWidgetItem(drug.category or ""))
            self.search_table.setItem(row, 3, QTableWidgetItem(str(drug.quantity)))
            self.search_table.setItem(row, 4, QTableWidgetItem(f"{drug.price:,.0f}"))

    def _auto_refresh(self):
        if self.search_input.text():
            self._search()

    def _add_to_cart(self):
        row = self.search_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "خطأ", "اختر دواء من نتائج البحث")
            return
        try:
            qty = int(self.qty_input.text() or "1")
            if qty <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "خطأ", "أدخل كمية صحيحة")
            return
        drug_id    = int(self.search_table.item(row, 0).text())
        drug_name  = self.search_table.item(row, 1).text()
        drug_price = float(self.search_table.item(row, 4).text().replace(",", ""))
        available  = int(self.search_table.item(row, 3).text())
        if qty > available:
            QMessageBox.warning(self, "مخزون غير كافٍ", f"المتوفر فقط: {available}")
            return
        for item in self.cart:
            if item["drug_id"] == drug_id:
                if item["qty"] + qty > available:
                    QMessageBox.warning(self, "خطأ", f"الكمية الكلية تتجاوز المتوفر ({available})")
                    return
                item["qty"] += qty
                self.qty_input.clear()
                self._refresh_cart()
                return
        self.cart.append({"drug_id": drug_id, "name": drug_name, "qty": qty, "price": drug_price})
        self.qty_input.clear()
        self._refresh_cart()

    def _remove_from_cart(self):
        row = self.cart_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "خطأ", "اختر عنصراً من السلة")
            return
        self.cart.pop(row)
        self._refresh_cart()

    def _clear_cart(self):
        self.cart = []
        self._refresh_cart()

    def _refresh_cart(self):
        self.cart_table.setRowCount(len(self.cart))
        self.total = 0.0
        for row, item in enumerate(self.cart):
            sub = item["qty"] * item["price"]
            self.total += sub
            self.cart_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.cart_table.setItem(row, 1, QTableWidgetItem(item["name"]))
            self.cart_table.setItem(row, 2, QTableWidgetItem(str(item["qty"])))
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"{item['price']:,.0f}"))
            self.cart_table.setItem(row, 4, QTableWidgetItem(f"{sub:,.0f}"))
        self.total_lbl.setText(f"💰 المجموع: {self.total:,.0f} IQD")

    def _complete_sale(self):
        if not self.cart:
            QMessageBox.warning(self, "السلة فارغة", "أضف أدوية للسلة أولاً")
            return
        pharmacist_id = self.user.id if self.user else None
        errors = []
        for item in self.cart:
            _, err = sell_drug(self.session, item["drug_id"], item["qty"], pharmacist_id)
            if err:
                errors.append(f"{item['name']}: {err}")
        if errors:
            QMessageBox.warning(self, "أخطاء في البيع", "\n".join(errors))
            return
        inv_num  = len(get_all_sales(self.session))
        filename = generate_invoice(self.cart, self.total, inv_num)
        QMessageBox.information(
            self, "✅ تمت عملية البيع",
            f"تمت عملية البيع بنجاح!\n💰 الإجمالي: {self.total:,.0f} IQD\n📄 {os.path.basename(filename)}",
        )
        try:
            os.startfile(filename)
        except Exception:
            pass
        self._clear_cart()
        self.session.expire_all()
        self._search()
