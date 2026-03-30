from db import get_engine
from sqlalchemy import text

engine = get_engine()

with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS komisyon_anlasmalari (
            acente_adi TEXT PRIMARY KEY,
            komisyon_orani REAL,
            ekran_ucreti_alindi_mi TEXT,
            anlasma_bicimi TEXT,
            updated_at TEXT
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS muhasebe_kayitlari (
            acente_adi TEXT,
            ay TEXT,
            net_prim REAL,
            toplam_komisyon REAL,
            komisyon_orani REAL,
            odenen_komisyon REAL,
            kalan_komisyon REAL,
            updated_at TEXT,
            PRIMARY KEY (acente_adi, ay)
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS komisyon_anlasmalari_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        acente_adi TEXT,
        komisyon_orani REAL,
        ekran_ucreti_alindi_mi TEXT,
        anlasma_bicimi TEXT,
        pdated_at TEXT,
        version_time TEXT
        )
    """))
    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS komisyon_anlasmalari_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        acente_adi TEXT,
        komisyon_orani REAL,
        ekran_ucreti_alindi_mi TEXT,
        anlasma_bicimi TEXT,
        updated_at TEXT,
        version_time TEXT
        )
    """))
    

print("Tablolar oluşturuldu.")