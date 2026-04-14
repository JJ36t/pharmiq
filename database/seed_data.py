"""
PharmIQ — Seed Data
50 دواء عراقي شائع + 10 تفاعلات دوائية مهمة
يُشغَّل مرة واحدة فقط عند أول تشغيل للبرنامج
"""

from datetime import date
from .crud import (
    add_drug, add_interaction,
    get_all_drugs, get_all_interactions,
)

# ── بيانات الأدوية ─────────────────────────────────────────────────────────
# (الاسم التجاري، الاسم العلمي، الفئة، السعر بالدينار العراقي، الكمية)
IRAQI_DRUGS = [
    # Analgesics
    ("Panadol",        "Paracetamol",              "Analgesics",       1500,  100),
    ("Brufen",         "Ibuprofen",                "Analgesics",       2000,   80),
    ("Aspirin",        "Acetylsalicylic Acid",     "Analgesics",       1000,  120),
    ("Voltaren",       "Diclofenac",               "Analgesics",       3000,   75),
    ("Tramadol",       "Tramadol HCl",             "Analgesics",       4000,   40),
    # Antibiotics
    ("Augmentin",      "Amoxicillin+Clavulanate",  "Antibiotics",      5000,   60),
    ("Amoxil",         "Amoxicillin",              "Antibiotics",      3000,   90),
    ("Cipro",          "Ciprofloxacin",            "Antibiotics",      4000,   70),
    ("Flagyl",         "Metronidazole",            "Antibiotics",      2500,   85),
    ("Zithromax",      "Azithromycin",             "Antibiotics",      6000,   50),
    ("Ceclor",         "Cefaclor",                 "Antibiotics",      7000,   40),
    ("Keflex",         "Cefalexin",                "Antibiotics",      4500,   55),
    # Gastrointestinal
    ("Omeprazole",     "Omeprazole",               "Gastrointestinal", 2000,  100),
    ("Nexium",         "Esomeprazole",             "Gastrointestinal", 8000,   45),
    ("Gaviscon",       "Alginate Antacid",         "Gastrointestinal", 4500,   55),
    ("Antinal",        "Nifuroxazide",             "Gastrointestinal", 3500,   75),
    ("Imodium",        "Loperamide",               "Gastrointestinal", 2500,   85),
    ("Dulcolax",       "Bisacodyl",                "Gastrointestinal", 2000,   90),
    ("Domperidone",    "Domperidone",              "Gastrointestinal", 3000,   80),
    # Diabetes
    ("Glucophage",     "Metformin",                "Diabetes",         3000,   95),
    ("Insulin Mixtard","Human Insulin 30/70",      "Diabetes",        15000,   30),
    ("Diamicron",      "Gliclazide",               "Diabetes",         4000,   60),
    # Cardiovascular
    ("Aspocid",        "Aspirin 100mg",            "Cardiovascular",   1500,  130),
    ("Concor",         "Bisoprolol",               "Cardiovascular",   5000,   65),
    ("Amlor",          "Amlodipine",               "Cardiovascular",   4000,   75),
    ("Lipitor",        "Atorvastatin",             "Cardiovascular",   7000,   50),
    ("Zocor",          "Simvastatin",              "Cardiovascular",   5000,   55),
    ("Warfarin",       "Warfarin Sodium",          "Cardiovascular",   3500,   60),
    ("Lasix",          "Furosemide",               "Cardiovascular",   2000,   80),
    ("Digoxin",        "Digoxin",                  "Cardiovascular",   2500,   55),
    ("Amiodarone",     "Amiodarone HCl",           "Cardiovascular",   8000,   30),
    ("Clopidogrel",    "Clopidogrel",              "Cardiovascular",   6000,   50),
    ("Aldactone",      "Spironolactone",           "Cardiovascular",   3500,   60),
    # Respiratory
    ("Ventolin",       "Salbutamol",               "Respiratory",      3500,   70),
    ("Symbicort",      "Budesonide+Formoterol",    "Respiratory",     18000,   20),
    ("Atrovent",       "Ipratropium",              "Respiratory",      7000,   35),
    # Antihistamines
    ("Claritine",      "Loratadine",               "Antihistamines",   2500,   90),
    ("Zyrtec",         "Cetirizine",               "Antihistamines",   3000,   85),
    ("Phenergan",      "Promethazine",             "Antihistamines",   2000,   70),
    # Neurology / Psychiatry
    ("Neurontin",      "Gabapentin",               "Neurology",        6000,   45),
    ("Lyrica",         "Pregabalin",               "Neurology",       12000,   25),
    ("Prozac",         "Fluoxetine",               "Psychiatry",       5000,   50),
    ("Xanax",          "Alprazolam",               "Psychiatry",       3000,   35),
    # Steroids
    ("Dexamethasone",  "Dexamethasone",            "Steroids",         2000,   90),
    ("Prednisolone",   "Prednisolone",             "Steroids",         2500,   80),
    # Vitamins & Supplements
    ("Vitamin C",      "Ascorbic Acid 500mg",      "Vitamins",         1500,  150),
    ("Vitamin D3",     "Cholecalciferol 1000IU",   "Vitamins",         5000,   80),
    ("Calcium Sandoz", "Calcium Carbonate",        "Vitamins",         3000,   90),
    ("Folic Acid",     "Folic Acid 5mg",           "Vitamins",         1500,  120),
    ("Zinc",           "Zinc Sulfate",             "Vitamins",         2000,  100),
]

# ── بيانات التفاعلات الدوائية ─────────────────────────────────────────────
# (drug_a, drug_b, severity, description, recommendation)
DRUG_INTERACTIONS = [
    (
        "Warfarin", "Aspirin",
        "High",
        "يزيد خطر النزيف الحاد — الجمع بينهما يضاعف تأثير مضاد التخثر",
        "تجنب الجمع تماماً — استشر الطبيب فوراً إذا لزم الأمر وراقب علامات النزيف",
    ),
    (
        "Warfarin", "Ibuprofen",
        "High",
        "مضادات الالتهاب غير الستيرويدية ترفع مستوى الوارفارين في الدم",
        "استخدم Paracetamol بديلاً — راقب INR بشكل مكثف",
    ),
    (
        "Fluoxetine", "Tramadol",
        "High",
        "خطر متلازمة السيروتونين — حالة طارئة تهدد الحياة (ارتفاع حرارة، رعشة، ارتباك)",
        "لا تجمع أبداً — استخدم مسكناً آخر غير أوبيوئيدي",
    ),
    (
        "Amiodarone", "Warfarin",
        "High",
        "الأميودارون يضاعف مستوى الوارفارين ويرفع خطر النزيف الداخلي",
        "قلل جرعة الوارفارين 30-50% وراقب INR كل 3 أيام",
    ),
    (
        "Metronidazole", "Warfarin",
        "High",
        "الميترونيدازول يثبط استقلاب الوارفارين ويرفع مستواه في الدم",
        "راقب INR يومياً — قد تحتاج تخفيض جرعة الوارفارين",
    ),
    (
        "Glucophage", "Prednisolone",
        "Medium",
        "الكورتيزون يرفع سكر الدم ويضعف فاعلية الميتفورمين",
        "راقب مستوى السكر يومياً — قد تحتاج زيادة جرعة Metformin",
    ),
    (
        "Cipro", "Calcium Sandoz",
        "Medium",
        "الكالسيوم يقلل امتصاص السيبروفلوكساسين في الجهاز الهضمي",
        "خذ السيبروفلوكساسين ساعتين قبل أو 6 ساعات بعد الكالسيوم",
    ),
    (
        "Aspirin", "Clopidogrel",
        "Medium",
        "الجمع يزيد خطر النزيف — لكن قد يكون مفيداً في متلازمات القلب الحادة",
        "يستخدم فقط بتوجيه الطبيب — راقب علامات النزيف المعدي",
    ),
    (
        "Digoxin", "Lasix",
        "Medium",
        "الليزيكس يسبب نقص البوتاسيوم مما يزيد سمية الديجوكسين على القلب",
        "راقب مستوى البوتاسيوم والديجوكسين بانتظام",
    ),
    (
        "Zocor", "Amiodarone",
        "Medium",
        "الأميودارون يرفع مستوى السيمفاستاتين وخطر اعتلال عضلي خطير",
        "لا تتجاوز 20mg من Simvastatin مع الأميودارون — فكر في تغيير الستاتين",
    ),
]


def seed_database(session) -> None:
    """
    يملأ قاعدة البيانات ببيانات أولية إذا كانت فارغة.
    يُستدعى مرة واحدة عند أول تشغيل.
    """
    # ── أدوية ─────────────────────────────────────────────────────────────
    if not get_all_drugs(session):
        print(f"⏳ Adding {len(IRAQI_DRUGS)} Iraqi drugs...")
        for trade, scientific, category, price, qty in IRAQI_DRUGS:
            add_drug(session, {
                "trade_name":      trade,
                "scientific_name": scientific,
                "category":        category,
                "price":           price,
                "quantity":        qty,
                "min_quantity":    10,
                "expiry_date":     date(2027, 6, 30),
            })
        print(f"  ✅ {len(IRAQI_DRUGS)} drugs added.")

    # ── تفاعلات ───────────────────────────────────────────────────────────
    if not get_all_interactions(session):
        print(f"⏳ Adding {len(DRUG_INTERACTIONS)} drug interactions...")
        for d1, d2, sev, desc, rec in DRUG_INTERACTIONS:
            add_interaction(session, d1, d2, sev, desc, rec)
        print(f"  ✅ {len(DRUG_INTERACTIONS)} interactions added.")
