"""
PharmIQ — Database Migration
يضيف الأعمدة الجديدة لقاعدة بيانات قديمة بدون حذف البيانات
"""

from sqlalchemy import text
from .db import engine


def run_migrations():
    """
    تشغيل كل migrations المطلوبة.
    كل migration يُجرَّب بشكل مستقل — الخطأ يعني العمود موجود مسبقاً.
    """
    migrations = [
        # ── جدول drugs ──────────────────────────────────────────────────────
        ("drugs", "ALTER TABLE drugs ADD COLUMN barcode VARCHAR"),
        ("drugs", "ALTER TABLE drugs ADD COLUMN supplier_id INTEGER"),
        ("drugs", "ALTER TABLE drugs ADD COLUMN category VARCHAR DEFAULT 'General'"),
        # ── جدول sales ──────────────────────────────────────────────────────
        ("sales", "ALTER TABLE sales ADD COLUMN pharmacist_id INTEGER"),
        # ── جدول users ──────────────────────────────────────────────────────
        ("users", "ALTER TABLE users ADD COLUMN last_login DATETIME"),
        # ── جدول drug_interactions (إعادة تسمية الحقول القديمة) ─────────────
        # ملاحظة: SQLite لا يدعم RENAME COLUMN في الإصدارات القديمة
        # لذلك نضيف الأعمدة الجديدة ونحتفظ بالقديمة
        ("drug_interactions", "ALTER TABLE drug_interactions ADD COLUMN drug_a VARCHAR"),
        ("drug_interactions", "ALTER TABLE drug_interactions ADD COLUMN drug_b VARCHAR"),
        ("drug_interactions", "ALTER TABLE drug_interactions ADD COLUMN recommendation TEXT"),
    ]

    print("─" * 50)
    print("PharmIQ — Running Database Migrations")
    print("─" * 50)

    with engine.connect() as conn:
        for table, sql in migrations:
            try:
                conn.execute(text(sql))
                conn.commit()
                col = sql.split("ADD COLUMN")[1].split()[0]
                print(f"  ✅ {table}.{col}")
            except Exception:
                col = sql.split("ADD COLUMN")[1].split()[0]
                print(f"  ⏭  {table}.{col} (already exists)")

        # ── نسخ البيانات القديمة (drug1_name → drug_a) إذا كانت موجودة ─────
        try:
            conn.execute(text("""
                UPDATE drug_interactions
                SET drug_a = drug1_name, drug_b = drug2_name
                WHERE drug_a IS NULL AND drug1_name IS NOT NULL
            """))
            conn.commit()
            print("  ✅ Migrated drug1_name → drug_a, drug2_name → drug_b")
        except Exception:
            pass  # العمود القديم غير موجود — لا بأس

    print("─" * 50)
    print("Migrations complete.")
    print("─" * 50)
