"""
PharmIQ — Barcode Manager
توليد والتحقق من أكواد EAN-13
كود الدولة المستخدم: 6291 (العراق)
"""

import os
import barcode
from barcode.writer import ImageWriter


BARCODE_DIR = "barcodes"
IRAQ_COUNTRY_CODE = "6291"


# ══════════════════════════════════════════════════════════════════════════════
# التحقق من صحة الباركود
# ══════════════════════════════════════════════════════════════════════════════

def validate_barcode(barcode_number: str) -> bool:
    """
    يتحقق من صحة رقم EAN-13.
    يحسب Check Digit ويقارنه بالرقم الأخير.
    """
    if not barcode_number or not barcode_number.isdigit():
        return False
    if len(barcode_number) != 13:
        return False
    digits = [int(d) for d in barcode_number[:-1]]
    total  = sum(d * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits))
    check  = (10 - (total % 10)) % 10
    return check == int(barcode_number[-1])


# ══════════════════════════════════════════════════════════════════════════════
# توليد رقم باركود
# ══════════════════════════════════════════════════════════════════════════════

def generate_barcode_number(drug_id: int) -> str:
    """
    يولّد رقم EAN-13 صحيح من ID الدواء.
    التنسيق: 6291 (العراق) + 8 أرقام من ID + check digit
    """
    base   = f"{IRAQ_COUNTRY_CODE}{drug_id:08d}"
    digits = [int(d) for d in base]
    total  = sum(d * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits))
    check  = (10 - (total % 10)) % 10
    return base + str(check)


# ══════════════════════════════════════════════════════════════════════════════
# توليد صورة الباركود
# ══════════════════════════════════════════════════════════════════════════════

def generate_barcode(barcode_number: str, filename: str = None) -> str | None:
    """
    يولّد صورة PNG للباركود ويحفظها في مجلد barcodes/.
    Returns: مسار الملف المحفوظ | None عند الفشل
    """
    os.makedirs(BARCODE_DIR, exist_ok=True)
    filename = filename or f"barcode_{barcode_number}"
    filepath = os.path.join(BARCODE_DIR, filename)

    try:
        ean   = barcode.get("ean13", barcode_number, writer=ImageWriter())
        saved = ean.save(filepath)
        return saved
    except Exception as e:
        print(f"Barcode generation error: {e}")
        return None


def get_barcode_path(drug_id: int) -> str:
    """إرجاع مسار ملف الباركود للدواء"""
    return os.path.join(BARCODE_DIR, f"drug_{drug_id}.png")


def barcode_exists(drug_id: int) -> bool:
    """التحقق من وجود صورة الباركود"""
    return os.path.exists(get_barcode_path(drug_id))
