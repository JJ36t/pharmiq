"""
PharmIQ — CRUD Operations
جميع عمليات قاعدة البيانات منظمة حسب الكيان
"""

from datetime import datetime, date as date_type
from sqlalchemy import text
from sqlalchemy.orm import Session

from .models import Drug, DrugInteraction, PurchaseOrder, Sale, Supplier, User


# ══════════════════════════════════════════════════════════════════════════════
# DRUGS — إدارة الأدوية
# ══════════════════════════════════════════════════════════════════════════════

def add_drug(session: Session, data: dict) -> Drug:
    """إضافة دواء جديد"""
    drug = Drug(**data)
    session.add(drug)
    session.commit()
    return drug


def get_all_drugs(session: Session) -> list[Drug]:
    """جلب كل الأدوية"""
    return session.query(Drug).order_by(Drug.trade_name).all()


def get_drugs_by_category(session: Session, category: str) -> list[Drug]:
    """جلب الأدوية حسب الفئة"""
    return session.query(Drug).filter_by(category=category).all()


def search_drug(session: Session, name: str) -> list[Drug]:
    """بحث بالاسم التجاري أو العلمي"""
    term = f"%{name}%"
    return (
        session.query(Drug)
        .filter(
            Drug.trade_name.ilike(term) | Drug.scientific_name.ilike(term)
        )
        .all()
    )


def search_drug_by_barcode(session: Session, barcode: str) -> Drug | None:
    """بحث بالباركود EAN-13"""
    return session.query(Drug).filter_by(barcode=barcode).first()


def update_drug(session: Session, drug_id: int, data: dict) -> Drug | None:
    """تعديل بيانات دواء"""
    drug = session.get(Drug, drug_id)
    if not drug:
        return None
    for key, value in data.items():
        setattr(drug, key, value)
    session.commit()
    return drug


def delete_drug(session: Session, drug_id: int) -> bool:
    """حذف دواء"""
    drug = session.get(Drug, drug_id)
    if not drug:
        return False
    session.delete(drug)
    session.commit()
    return True


# ══════════════════════════════════════════════════════════════════════════════
# SALES — عمليات البيع
# ══════════════════════════════════════════════════════════════════════════════

def sell_drug(
    session: Session,
    drug_id: int,
    quantity: int,
    pharmacist_id: int | None = None,
) -> tuple[Sale | None, str | None]:
    """
    تسجيل عملية بيع.
    يخصم الكمية من المخزون ويحفظ السجل.
    Returns: (Sale, None) عند النجاح | (None, error_msg) عند الفشل
    """
    drug = session.get(Drug, drug_id)
    if not drug:
        return None, "الدواء غير موجود"
    if drug.is_expired:
        return None, f"الدواء منتهي الصلاحية — لا يمكن بيعه"
    if drug.quantity < quantity:
        return None, f"الكمية غير كافية — المتوفر: {drug.quantity}"

    total = drug.price * quantity
    drug.quantity -= quantity

    sale = Sale(
        drug_id=drug_id,
        pharmacist_id=pharmacist_id,
        quantity_sold=quantity,
        total_price=total,
    )
    session.add(sale)
    session.commit()
    return sale, None


def get_all_sales(session: Session) -> list[Sale]:
    """جلب كل المبيعات"""
    return session.query(Sale).order_by(Sale.sale_date.desc()).all()


def get_today_sales(session: Session) -> list[Sale]:
    """مبيعات اليوم فقط"""
    today_start = datetime.combine(datetime.now().date(), datetime.min.time())
    return (
        session.query(Sale)
        .filter(Sale.sale_date >= today_start)
        .all()
    )


def get_today_revenue(session: Session) -> float:
    """إجمالي إيرادات اليوم"""
    return sum(s.total_price for s in get_today_sales(session))


def get_total_revenue(session: Session) -> float:
    """إجمالي الإيرادات الكلية"""
    return sum(s.total_price for s in get_all_sales(session))


# ══════════════════════════════════════════════════════════════════════════════
# USERS — إدارة المستخدمين
# ══════════════════════════════════════════════════════════════════════════════

def create_user(
    session: Session, username: str, password: str, role: str = "cashier"
) -> tuple[User | None, str | None]:
    """إنشاء مستخدم جديد"""
    if session.query(User).filter_by(username=username).first():
        return None, "اسم المستخدم موجود مسبقاً"
    user = User(
        username=username,
        password=User.hash_password(password),
        role=role,
    )
    session.add(user)
    session.commit()
    return user, None


def login_user(
    session: Session, username: str, password: str
) -> tuple[User | None, str | None]:
    """تسجيل الدخول مع تحديث last_login"""
    user = session.query(User).filter_by(username=username).first()
    if not user:
        return None, "اسم المستخدم غير موجود"
    if not user.check_password(password):
        return None, "كلمة المرور غير صحيحة"
    user.last_login = datetime.now()
    session.commit()
    return user, None


def get_all_users(session: Session) -> list[User]:
    return session.query(User).all()


def delete_user(session: Session, user_id: int) -> bool:
    user = session.get(User, user_id)
    if not user:
        return False
    session.delete(user)
    session.commit()
    return True


# ══════════════════════════════════════════════════════════════════════════════
# DRUG INTERACTIONS — التفاعلات الدوائية
# ══════════════════════════════════════════════════════════════════════════════

def check_interactions(
    session: Session, drug_names: list[str]
) -> list[dict]:
    """
    فحص التفاعلات بين قائمة أدوية.
    الخوارزمية: كل زوج ممكن → SQL مباشر → مرتب حسب الخطورة.
    Input:  ['Warfarin', 'Aspirin', 'Metformin']
    Output: list of dicts مرتبة (High أولاً)
    """
    warnings = []
    for i in range(len(drug_names)):
        for j in range(i + 1, len(drug_names)):
            d1, d2 = drug_names[i], drug_names[j]
            row = session.execute(
                text("""
                    SELECT severity, description, recommendation
                    FROM drug_interactions
                    WHERE (LOWER(drug_a) = LOWER(:a) AND LOWER(drug_b) = LOWER(:b))
                       OR (LOWER(drug_a) = LOWER(:b) AND LOWER(drug_b) = LOWER(:a))
                """),
                {"a": d1, "b": d2},
            ).fetchone()
            if row:
                warnings.append({
                    "pair":           f"{d1} + {d2}",
                    "drug1":          d1,
                    "drug2":          d2,
                    "severity":       row.severity,
                    "description":    row.description,
                    "recommendation": row.recommendation,
                })

    severity_order = {"High": 0, "Medium": 1, "Low": 2}
    return sorted(warnings, key=lambda x: severity_order.get(x["severity"], 3))


def add_interaction(
    session: Session,
    drug_a: str,
    drug_b: str,
    severity: str,
    description: str,
    recommendation: str = "",
) -> DrugInteraction:
    """إضافة تفاعل دوائي جديد"""
    inter = DrugInteraction(
        drug_a=drug_a,
        drug_b=drug_b,
        severity=severity,
        description=description,
        recommendation=recommendation,
    )
    session.add(inter)
    session.commit()
    return inter


def get_all_interactions(session: Session) -> list[DrugInteraction]:
    return session.query(DrugInteraction).all()


def delete_interaction(session: Session, interaction_id: int) -> bool:
    inter = session.get(DrugInteraction, interaction_id)
    if not inter:
        return False
    session.delete(inter)
    session.commit()
    return True


# ══════════════════════════════════════════════════════════════════════════════
# SUPPLIERS — إدارة الموردين
# ══════════════════════════════════════════════════════════════════════════════

def add_supplier(session: Session, data: dict) -> Supplier:
    supplier = Supplier(**data)
    session.add(supplier)
    session.commit()
    return supplier


def get_all_suppliers(session: Session) -> list[Supplier]:
    return session.query(Supplier).order_by(Supplier.name).all()


def delete_supplier(session: Session, supplier_id: int) -> bool:
    supplier = session.get(Supplier, supplier_id)
    if not supplier:
        return False
    session.delete(supplier)
    session.commit()
    return True


# ══════════════════════════════════════════════════════════════════════════════
# PURCHASE ORDERS — طلبات التوريد
# ══════════════════════════════════════════════════════════════════════════════

def add_purchase_order(
    session: Session,
    supplier_id: int,
    drug_id: int,
    quantity: int,
    cost_per_unit: float,
    notes: str = "",
) -> PurchaseOrder:
    """إنشاء طلب شراء جديد"""
    order = PurchaseOrder(
        supplier_id=supplier_id,
        drug_id=drug_id,
        quantity=quantity,
        cost_per_unit=cost_per_unit,
        notes=notes,
    )
    session.add(order)
    session.commit()
    return order


def get_all_purchase_orders(session: Session) -> list[PurchaseOrder]:
    return (
        session.query(PurchaseOrder)
        .order_by(PurchaseOrder.order_date.desc())
        .all()
    )


def receive_purchase_order(session: Session, order_id: int) -> bool:
    """استلام الطلب وإضافة الكمية للمخزون تلقائياً"""
    order = session.get(PurchaseOrder, order_id)
    if not order or order.status != "pending":
        return False
    drug = session.get(Drug, order.drug_id)
    if drug:
        drug.quantity += order.quantity
    order.status = "received"
    order.received_date = datetime.now()
    session.commit()
    return True


def cancel_purchase_order(session: Session, order_id: int) -> bool:
    order = session.get(PurchaseOrder, order_id)
    if not order or order.status != "pending":
        return False
    order.status = "cancelled"
    session.commit()
    return True
