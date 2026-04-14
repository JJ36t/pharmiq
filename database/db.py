"""
PharmIQ — Database Engine Configuration
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ─── محرك قاعدة البيانات ───────────────────────────────────────────────────
engine = create_engine(
    "sqlite:///pharmiq.db",
    echo=False,          # True للتطوير فقط
    connect_args={"check_same_thread": False},
)

# ─── مصنع الجلسات ─────────────────────────────────────────────────────────
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# ─── الأساس لكل الموديلات ─────────────────────────────────────────────────
Base = declarative_base()
