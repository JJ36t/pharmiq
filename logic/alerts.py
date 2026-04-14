"""
PharmIQ — Automatic Alert System
نظام التنبيهات التلقائية — 3 مستويات حسب التقرير:
  critical → منتهي الصلاحية
  warning  → ينتهي خلال 30 يوم
  info     → مخزون قليل
"""

import schedule
import threading
import time

from database.crud import get_all_drugs


# ══════════════════════════════════════════════════════════════════════════════
# فحص المخزون الكامل
# ══════════════════════════════════════════════════════════════════════════════

def run_daily_checks(session) -> list[dict]:
    """
    يفحص كل الأدوية ويرجع قائمة تنبيهات منظمة.
    كل تنبيه: {drug, type, detail, level}
    level: critical | warning | info
    """
    drugs = get_all_drugs(session)
    alerts = []

    # ── منتهي الصلاحية (critical) ────────────────────────────────────────
    for d in drugs:
        if d.is_expired:
            alerts.append({
                "drug":   d.trade_name,
                "type":   "EXPIRED",
                "detail": "منتهي الصلاحية — أزله من الرف فوراً",
                "level":  "critical",
            })

    # ── ينتهي قريباً (warning) ────────────────────────────────────────────
    for d in drugs:
        if d.is_expiring_soon:
            alerts.append({
                "drug":   d.trade_name,
                "type":   "EXPIRING SOON",
                "detail": f"ينتهي خلال {d.days_to_expiry} يوم",
                "level":  "warning",
            })

    # ── مخزون قليل (info) ────────────────────────────────────────────────
    for d in drugs:
        if d.is_low_stock and not d.is_expired:
            alerts.append({
                "drug":   d.trade_name,
                "type":   "LOW STOCK",
                "detail": f"متبقي {d.quantity} فقط (الحد الأدنى: {d.min_quantity})",
                "level":  "info",
            })

    return alerts


def check_alerts(session) -> list[str]:
    """
    واجهة بسيطة ترجع قائمة نصوص للعرض في QMessageBox.
    """
    alerts = run_daily_checks(session)
    icons  = {"critical": "🔴", "warning": "⚠️", "info": "📦"}
    return [
        f"{icons.get(a['level'], '•')} {a['type']}: {a['drug']} — {a['detail']}"
        for a in alerts
    ]


# ══════════════════════════════════════════════════════════════════════════════
# Scheduler — يشتغل يومياً الساعة 8:00 صباحاً
# ══════════════════════════════════════════════════════════════════════════════

_scheduler_started = False


def start_alert_scheduler(session):
    """
    يشغل فحصاً يومياً تلقائياً في خلفية البرنامج.
    يعمل في thread منفصل حتى لا يعطل الواجهة.
    """
    global _scheduler_started
    if _scheduler_started:
        return
    _scheduler_started = True

    schedule.every().day.at("08:00").do(
        lambda: run_daily_checks(session)
    )

    def _runner():
        while True:
            schedule.run_pending()
            time.sleep(60)

    thread = threading.Thread(target=_runner, daemon=True)
    thread.start()
