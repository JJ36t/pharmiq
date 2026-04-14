"""
PharmIQ — Smart Pharmacy Management System
Entry Point | نقطة التشغيل الرئيسية

Department of Intelligent Medical Systems
College of Computer Science — Al-Diwaniyah, Iraq
"""

import sys

from PyQt6.QtWidgets import QApplication

from database.db import SessionLocal, engine
from database.migrate import run_migrations
from database.models import Base
from database.seed_data import seed_database
from logic.alerts import run_daily_checks, start_alert_scheduler
from logic.backup_manager import start_auto_backup
from logic.rtl_helper import apply_rtl_app
from ui.style import DARK_STYLE


def main():
    # ── 1. إنشاء الجداول الجديدة ────────────────────────────────────────
    Base.metadata.create_all(engine)

    # ── 2. Migration للأعمدة الجديدة على قواعد بيانات قديمة ─────────────
    run_migrations()

    # ── 3. تشغيل التطبيق ────────────────────────────────────────────────
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)
    apply_rtl_app(app)

    # ── 4. تشغيل النسخ الاحتياطي التلقائي (كل يوم 02:00) ────────────────
    start_auto_backup()

    # ── 5. جلسة مشتركة ──────────────────────────────────────────────────
    session = SessionLocal()

    # ── 6. بيانات أولية (أول تشغيل فقط) ─────────────────────────────────
    seed_database(session)

    # ── 7. تشغيل فحص التنبيهات اليومي (08:00) ────────────────────────────
    start_alert_scheduler(session)

    # ── 8. فحص فوري عند الفتح (يُعرض بعد نجاح الدخول) ──────────────────
    startup_alerts = run_daily_checks(session)

    # ── 9. Callback بعد تسجيل الدخول ─────────────────────────────────────
    def on_login_success(user):
        from PyQt6.QtWidgets import QMessageBox
        from ui.main_window import MainWindow

        window = MainWindow(session, user)
        window.show()
        app._main_window = window

        # عرض تنبيهات الفتح إذا وُجدت
        if startup_alerts:
            from logic.alerts import check_alerts
            alerts = check_alerts(session)
            if alerts:
                QMessageBox.warning(
                    window,
                    f"⚠️ تنبيهات — {len(startup_alerts)} مشكلة",
                    "\n".join(alerts[:15]),
                )

    # ── 10. شاشة تسجيل الدخول ────────────────────────────────────────────
    from ui.login_window import LoginWindow
    login = LoginWindow(session, on_login_success)
    login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
