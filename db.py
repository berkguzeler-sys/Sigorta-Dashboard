from sqlalchemy import create_engine, text
import pandas as pd
from datetime import datetime

# --------------------------------------------------
# 🔗 DB CONNECTION
# --------------------------------------------------
engine = create_engine("sqlite:///polipedia.db", echo=False)

# --------------------------------------------------
# 👤 USERS
# --------------------------------------------------
def create_users_table():
    from sqlalchemy import text

    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
        """))

def add_user(username, password):
    from sqlalchemy import text

    with engine.begin() as conn:
        conn.execute(text("""
        INSERT OR REPLACE INTO users (username, password)
        VALUES (:u, :p)
        """), {"u": username, "p": password})

def save_anlasma_log(df, user):

    df_log = df.copy()

    df_log["version_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_log["updated_by"] = user

    df_log.to_sql(
        "komisyon_anlasmalari_log",
        engine,
        if_exists="append",
        index=False
    )        

def get_user(username):
    from sqlalchemy import text

    with engine.begin() as conn:
        result = conn.execute(
            text("SELECT * FROM users WHERE username = :u"),
            {"u": username}
        ).fetchone()

        if result:
            return dict(result._mapping)
        return None

def get_engine():
    return engine

# --------------------------------------------------
# 📑 KOMİSYON ANLAŞMALARI
# --------------------------------------------------
def load_komisyon_anlasmalari():
    try:
        return pd.read_sql("SELECT * FROM komisyon_anlasmalari", engine)
    except:
        return pd.DataFrame(columns=[
            "acente_adi",
            "komisyon_orani",
            "ekran_ucreti_alindi_mi",
            "anlasma_bicimi",
            "updated_at"
        ])


def upsert_komisyon_anlasmalari(df):

    from sqlalchemy import text

    with engine.begin() as conn:

        for _, row in df.iterrows():

            # 🔥 eski kayıt var mı
            existing = conn.execute(
                text("SELECT * FROM komisyon_anlasmalari WHERE acente_adi = :a"),
                {"a": row["acente_adi"]}
            ).fetchone()

            # 🔥 tuple → dict dönüşümü (KRİTİK)
            if existing:
                existing = dict(existing._mapping)

            if existing:
                # 🔥 SADECE DEĞİŞTİYSE UPDATE
                if (
                    existing["komisyon_orani"] != row["komisyon_orani"] or
                    existing["ekran_ucreti_alindi_mi"] != row["ekran_ucreti_alindi_mi"] or
                    existing["anlasma_bicimi"] != row["anlasma_bicimi"]
                ):
                    conn.execute(text("""
                        UPDATE komisyon_anlasmalari
                        SET komisyon_orani = :k,
                            ekran_ucreti_alindi_mi = :e,
                            anlasma_bicimi = :b,
                            updated_at = :u
                        WHERE acente_adi = :a
                    """), {
                        "a": row["acente_adi"],
                        "k": row["komisyon_orani"],
                        "e": row["ekran_ucreti_alindi_mi"],
                        "b": row["anlasma_bicimi"],
                        "u": row["updated_at"]
                    })

            else:
                # 🔥 yeni satır
                conn.execute(text("""
                    INSERT INTO komisyon_anlasmalari (
                        acente_adi,
                        komisyon_orani,
                        ekran_ucreti_alindi_mi,
                        anlasma_bicimi,
                        updated_at
                    )
                    VALUES (:a, :k, :e, :b, :u)
                """), {
                    "a": row["acente_adi"],
                    "k": row["komisyon_orani"],
                    "e": row["ekran_ucreti_alindi_mi"],
                    "b": row["anlasma_bicimi"],
                    "u": row["updated_at"]
                })

# --------------------------------------------------


def delete_anlasma_log(version_time):
    from sqlalchemy import text

    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM komisyon_anlasmalari_log WHERE version_time = :v"),
            {"v": version_time}
        )    


def load_anlasma_log():
    try:
        return pd.read_sql(
            "SELECT * FROM komisyon_anlasmalari_log ORDER BY id DESC",
            engine
        )
    except:
        return pd.DataFrame()

# --------------------------------------------------
# 💰 MUHASEBE
# --------------------------------------------------
def load_muhasebe():
    try:
        return pd.read_sql("SELECT * FROM muhasebe_kayitlari", engine)
    except:
        return pd.DataFrame(columns=[
            "acente_adi",
            "ay",
            "net_prim",
            "toplam_komisyon",
            "komisyon_orani",
            "odenen_komisyon",
            "kalan_komisyon",
            "updated_at"
        ])


def save_muhasebe(df):
    df = df.copy()
    df["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM muhasebe_kayitlari"))

    df.to_sql(
        "muhasebe_kayitlari",
        engine,
        if_exists="append",
        index=False
    )