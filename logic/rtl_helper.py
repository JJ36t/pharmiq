"""
PharmIQ — RTL & Arabic Text Helper
دعم الكتابة العربية من اليمين لليسار في الواجهة وملفات PDF
"""

from PyQt6.QtCore import Qt


def ar(text: str) -> str:
    """
    يحوّل النص العربي للعرض الصحيح في ReportLab PDF.
    يستخدم arabic_reshaper لتشكيل الحروف + python-bidi للاتجاه.
    """
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(str(text)))
    except ImportError:
        return str(text)


def apply_rtl(widget) -> None:
    """يطبق RTL على Widget واحد"""
    widget.setLayoutDirection(Qt.LayoutDirection.RightToLeft)


def apply_rtl_app(app) -> None:
    """يطبق RTL على كامل التطبيق"""
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
