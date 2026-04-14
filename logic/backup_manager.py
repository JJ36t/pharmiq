"""
PharmIQ — Backup Manager
نسخ احتياطي تلقائي يومي مع الاحتفاظ بآخر 7 نسخ
"""

import os
import shutil
import schedule
import threading
import time
from datetime import datetime


BACKUP_DIR = "backups"
DB_FILE    = "pharmiq.db"
KEEP_LAST  = 7


def create_backup() -> str | None:
    """
    ينشئ نسخة احتياطية مختومة بالتاريخ والوقت.
    Returns: مسار الملف | None عند الفشل
    """
    if not os.path.exists(DB_FILE):
        return None

    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dest      = os.path.join(BACKUP_DIR, f"pharmiq_backup_{timestamp}.db")

    shutil.copy2(DB_FILE, dest)
    _cleanup_old_backups()
    return dest


def _cleanup_old_backups() -> None:
    """يحذف النسخ الزائدة — يبقي فقط آخر KEEP_LAST نسخة"""
    if not os.path.exists(BACKUP_DIR):
        return
    files = sorted(
        [os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.endswith(".db")]
    )
    while len(files) > KEEP_LAST:
        os.remove(files.pop(0))


def get_all_backups() -> list[str]:
    """قائمة النسخ الاحتياطية مرتبة تنازلياً (الأحدث أولاً)"""
    if not os.path.exists(BACKUP_DIR):
        return []
    return sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.endswith(".db")],
        reverse=True,
    )


def restore_backup(filename: str) -> bool:
    """يستعيد نسخة احتياطية محددة"""
    src = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(src):
        return False
    shutil.copy2(src, DB_FILE)
    return True


_backup_started = False


def start_auto_backup() -> None:
    """
    يشغل النسخ الاحتياطي التلقائي كل يوم الساعة 02:00.
    Thread daemon — يتوقف تلقائياً مع إغلاق البرنامج.
    """
    global _backup_started
    if _backup_started:
        return
    _backup_started = True

    schedule.every().day.at("02:00").do(create_backup)

    def _runner():
        while True:
            schedule.run_pending()
            time.sleep(60)

    threading.Thread(target=_runner, daemon=True).start()
