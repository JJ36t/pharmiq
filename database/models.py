"""
PharmIQ — SQLAlchemy Database Models
يتطابق مع مخطط قاعدة البيانات في تقرير المشروع بالكامل
"""

import hashlib
from datetime import date, datetime

from sqlalchemy import (
    Column, Integer, String, Float, Date,
    DateTime, ForeignKey, Text,
)
from sqlalchemy.orm import relationship

from .db import Base


# ══════════════════════════════════════════════════════════════════════════════
# 1. USER — المستخدمين والصلاحيات
# ══════════════════════════════════════════════════════════════════════════════
class User(Base):
    """
    جدول المستخدمين.
    role: admin  → صلاحية كاملة
    role: cashier → بيع وعرض فقط
    """
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True)
    username   = Column(String(64), unique=True, nullable=False)
    password   = Column(String(64), nullable=False)       # SHA-256 hash
    role       = Column(String(16), default="cashier")    # admin / cashier
    last_login = Column(DateTime, nullable=True)

    # ── علاقات ──────────────────────────────────────────────────────────────
    sales = relationship("Sale", back_populates="pharmacist")

    # ── تشفير كلمة المرور ───────────────────────────────────────────────────
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password: str) -> bool:
        return self.password == self.hash_password(password)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


# ══════════════════════════════════════════════════════════════════════════════
# 2. DRUG — كتالوج الأدوية والمخزون
# ══════════════════════════════════════════════════════════════════════════════
class Drug(Base):
    """
    جدول الأدوية الرئيسي.
    يشمل: الاسم التجاري، العلمي، الفئة، الكمية، السعر، الباركود، تاريخ الانتهاء.
    """
    __tablename__ = "drugs"

    id              = Column(Integer, primary_key=True)
    trade_name      = Column(String(128), nullable=False)    # الاسم التجاري
    scientific_name = Column(String(128))                    # الاسم العلمي (INN)
    category        = Column(String(64), default="General")  # الفئة الدوائية
    barcode         = Column(String(13), unique=True, nullable=True)  # EAN-13
    quantity        = Column(Integer, default=0)
    min_quantity    = Column(Integer, default=5)             # حد التنبيه
    price           = Column(Float, default=0)               # دينار عراقي
    expiry_date     = Column(Date, nullable=True)
    supplier_id     = Column(Integer, ForeignKey("suppliers.id"), nullable=True)

    # ── علاقات ──────────────────────────────────────────────────────────────
    supplier = relationship("Supplier", back_populates="drugs")
    sales    = relationship("Sale", back_populates="drug")

    # ── خصائص ذكية ──────────────────────────────────────────────────────────
    @property
    def is_low_stock(self) -> bool:
        return self.quantity <= self.min_quantity

    @property
    def days_to_expiry(self) -> int:
        if self.expiry_date:
            return (self.expiry_date - date.today()).days
        return 9999

    @property
    def is_expiring_soon(self) -> bool:
        return 0 < self.days_to_expiry <= 30

    @property
    def is_expired(self) -> bool:
        return self.days_to_expiry <= 0

    def __repr__(self):
        return f"<Drug {self.trade_name} qty={self.quantity}>"


# ══════════════════════════════════════════════════════════════════════════════
# 3. DRUG INTERACTION — تفاعلات الأدوية الخطرة
# ══════════════════════════════════════════════════════════════════════════════
class DrugInteraction(Base):
    """
    قاعدة بيانات التفاعلات الدوائية.
    severity: High / Medium / Low
    """
    __tablename__ = "drug_interactions"

    id             = Column(Integer, primary_key=True)
    drug_a         = Column(String(128), nullable=False)
    drug_b         = Column(String(128), nullable=False)
    severity       = Column(String(16), default="Medium")   # High / Medium / Low
    description    = Column(Text)
    recommendation = Column(Text)

    def __repr__(self):
        return f"<Interaction {self.drug_a} + {self.drug_b} [{self.severity}]>"


# ══════════════════════════════════════════════════════════════════════════════
# 4. SALE — سجل المبيعات
# ══════════════════════════════════════════════════════════════════════════════
class Sale(Base):
    """
    كل عملية بيع تُسجَّل هنا مع ربط الدواء والصيدلاني.
    """
    __tablename__ = "sales"

    id             = Column(Integer, primary_key=True)
    drug_id        = Column(Integer, ForeignKey("drugs.id"))
    pharmacist_id  = Column(Integer, ForeignKey("users.id"), nullable=True)
    quantity_sold  = Column(Integer)
    total_price    = Column(Float)
    sale_date      = Column(DateTime, default=datetime.now)

    # ── علاقات ──────────────────────────────────────────────────────────────
    drug       = relationship("Drug", back_populates="sales")
    pharmacist = relationship("User", back_populates="sales")

    def __repr__(self):
        return f"<Sale #{self.id} drug={self.drug_id} total={self.total_price}>"


# ══════════════════════════════════════════════════════════════════════════════
# 5. SUPPLIER — دليل الموردين
# ══════════════════════════════════════════════════════════════════════════════
class Supplier(Base):
    __tablename__ = "suppliers"

    id      = Column(Integer, primary_key=True)
    name    = Column(String(128), nullable=False)
    phone   = Column(String(32))
    email   = Column(String(128))
    address = Column(Text)

    # ── علاقات ──────────────────────────────────────────────────────────────
    drugs           = relationship("Drug", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")

    def __repr__(self):
        return f"<Supplier {self.name}>"


# ══════════════════════════════════════════════════════════════════════════════
# 6. PURCHASE ORDER — طلبات التوريد وتاريخ التسليم
# ══════════════════════════════════════════════════════════════════════════════
class PurchaseOrder(Base):
    """
    سجل طلبات الشراء من الموردين.
    status: pending / received / cancelled
    """
    __tablename__ = "purchase_orders"

    id            = Column(Integer, primary_key=True)
    supplier_id   = Column(Integer, ForeignKey("suppliers.id"))
    drug_id       = Column(Integer, ForeignKey("drugs.id"))
    quantity      = Column(Integer)
    cost_per_unit = Column(Float)
    order_date    = Column(DateTime, default=datetime.now)
    received_date = Column(DateTime, nullable=True)
    status        = Column(String(16), default="pending")   # pending/received/cancelled
    notes         = Column(Text)

    # ── علاقات ──────────────────────────────────────────────────────────────
    supplier = relationship("Supplier", back_populates="purchase_orders")
    drug     = relationship("Drug")

    @property
    def total_cost(self) -> float:
        return (self.quantity or 0) * (self.cost_per_unit or 0)

    def __repr__(self):
        return f"<PurchaseOrder #{self.id} status={self.status}>"
