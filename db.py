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



def save_processed_data(df):
    """ETL'den geçmiş (branşları, acenteleri düzeltilmiş) veriyi DB'ye yazar."""
    try:
        df.to_sql("islenmis_veriler", engine, if_exists="replace", index=False)
        return True
    except Exception as e:
        print(f"İşlenmiş veri kayıt hatası: {e}")
        return False

def load_processed_data():
    """Dashboard için DB'den işlenmiş veriyi çeker."""
    try:
        return pd.read_sql("SELECT * FROM islenmis_veriler", engine)
    except:
        return pd.DataFrame()
    
def save_processed_data(df):
    """ETL'den geçmiş (hesaplanmış kolonların olduğu) veriyi DB'ye yazar."""
    try:
        # Dashboard için temizlenmiş veriyi 'islenmis_veriler' tablosuna kaydet
        df.to_sql("islenmis_veriler", engine, if_exists="replace", index=False)
        return True
    except Exception as e:
        print(f"İşlenmiş veri kayıt hatası: {e}")
        return False

def load_processed_data():
    """Dashboard'u beslemek için DB'den işlenmiş veriyi çeker."""
    try:
        # Veriyi SQL'den Pandas DataFrame olarak oku
        return pd.read_sql("SELECT * FROM islenmis_veriler", engine)
    except:
        # Tablo henüz yoksa (ilk kurulum) boş bir dataframe dön
        return pd.DataFrame()      

def save_raw_data_to_db(df_new):
    """Poliçe No ve Kayıt Türü bazlı artımlı yükleme yapar."""
    import pandas as pd
    try:
        # DB'deki mevcut anahtarları çek
        existing = pd.read_sql("SELECT [Poliçe No], [Kayıt Türü] FROM ham_veriler", engine)
        
        # Karşılaştırma için geçici anahtar oluştur
        df_new["temp_key"] = df_new["Poliçe No"].astype(str) + df_new["Kayıt Türü"].astype(str)
        existing["temp_key"] = existing["Poliçe No"].astype(str) + existing["Kayıt Türü"].astype(str)
        
        # Sadece DB'de olmayanları ayır
        df_to_add = df_new[~df_new["temp_key"].isin(existing["temp_key"])].drop(columns=["temp_key"])
        
        if not df_to_add.empty:
            df_to_add.to_sql("ham_veriler", engine, if_exists="append", index=False)
            return len(df_to_add)
        return 0
    except:
        # Tablo yoksa (ilk yükleme)
        if "temp_key" in df_new.columns: df_new = df_new.drop(columns=["temp_key"])
        df_new.to_sql("ham_veriler", engine, if_exists="replace", index=False)
        return len(df_new)    
    


  

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
    
def upsert_muhasebe_from_dashboard(df_dashboard, current_user):
    from sqlalchemy import text
    from datetime import datetime

    # TEK BİR BAĞLANTI BLOKU (with engine.begin)
    with engine.begin() as conn:
        
        # 1. ADIM: TABLOYU SİL (EĞER SÜTUN HATASI ALIYORSAN BU SATIRIN BAŞINDAKİ # İŞARETİNİ KALDIR)
        # conn.execute(text("DROP TABLE IF EXISTS muhasebe_kayitlari;")) 

        # 2. ADIM: TABLOYU DOĞRU SIRALAMA VE EKSİKSİZ SÜTUNLARLA OLUŞTUR
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS muhasebe_kayitlari (
            acente_adi TEXT,
            ay TEXT,
            net_prim REAL,
            toplam_komisyon REAL,
            komisyon_orani REAL,
            toplam_kazanc REAL,
            odenen_komisyon REAL,
            kalan_komisyon REAL,
            updated_at TEXT,
            updated_by TEXT,
            PRIMARY KEY (acente_adi, ay)
        )
        """))

        # 3. ADIM: DÖNGÜYE GİR
        for _, row in df_dashboard.iterrows():
            # DB'de bu acente ve ay için kayıt var mı bak
            existing = conn.execute(
                text("SELECT komisyon_orani FROM muhasebe_kayitlari WHERE acente_adi = :a AND ay = :ay"),
                {"a": row["acente_adi"], "ay": row["ay"]}
            ).fetchone()

            simdi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if existing:
                # KAYIT VARSA: Mevcut (manuel girilen) oranı koru, rakamları güncelle
                db_oran = existing._mapping["komisyon_orani"]
                yeni_kazanc = (row["toplam_komisyon"] * db_oran) / 100
                
                conn.execute(text("""
                    UPDATE muhasebe_kayitlari
                    SET net_prim = :n,
                        toplam_komisyon = :t,
                        toplam_kazanc = :tk,
                        updated_at = :u
                    WHERE acente_adi = :a AND ay = :ay
                """), {
                    "a": row["acente_adi"], "ay": row["ay"],
                    "n": row["net_prim"], "t": row["toplam_komisyon"],
                    "tk": yeni_kazanc, "u": simdi
                })
            else:
                # KAYIT YOKSA: İlk defa oluştur (Dashboard'daki varsayılan oranı kullan)
                conn.execute(text("""
                    INSERT INTO muhasebe_kayitlari (
                        acente_adi, ay, net_prim, toplam_komisyon, 
                        komisyon_orani, toplam_kazanc, odenen_komisyon, 
                        kalan_komisyon, updated_at, updated_by
                    )
                    VALUES (:a, :ay, :n, :t, :k, :tk, 0, :tk, :u, :ub)
                """), {
                    "a": row["acente_adi"], "ay": row["ay"], "n": row["net_prim"],
                    "t": row["toplam_komisyon"], "k": row["komisyon_orani"],
                    "tk": row["toplam_kazanc"], "u": simdi, "ub": current_user
                })
                

def upsert_muhasebe(df, current_user):
    from sqlalchemy import text
    from datetime import datetime

    # 1. TABLOYU İSTEDİĞİN SIRAYLA OLUŞTUR (YOKSA)
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS muhasebe_kayitlari (
            acente_adi TEXT,
            ay TEXT,
            net_prim REAL,
            toplam_komisyon REAL,
            komisyon_orani REAL,
            toplam_kazanc REAL,        -- İstediğin yer
            odenen_komisyon REAL,
            kalan_komisyon REAL,
            updated_at TEXT,           -- Sadece değişince güncellenecek
            updated_by TEXT,           -- İşlemi yapan kullanıcı
            PRIMARY KEY (acente_adi, ay)
        )
        """))

    with engine.begin() as conn:
        for _, row in df.iterrows():
            # Mevcut kaydı kontrol et
            existing = conn.execute(
                text("SELECT * FROM muhasebe_kayitlari WHERE acente_adi = :a AND ay = :ay"),
                {"a": row["acente_adi"], "ay": row["ay"]}
            ).fetchone()

            if existing:
                existing_dict = dict(existing._mapping)
                
                # 🔥 KRİTİK KONTROL: Verilerde gerçekten bir değişiklik var mı?
                # Sadece kullanıcı tarafından değiştirilebilen alanları kontrol ediyoruz
                has_changed = (
                    abs(existing_dict["komisyon_orani"] - row["komisyon_orani"]) > 0.001 or
                    abs(existing_dict["odenen_komisyon"] - row["odenen_komisyon"]) > 0.001 or
                    existing_dict["toplam_kazanc"] != row["toplam_kazanc"]
                )

                if has_changed:
                    # SADECE DEĞİŞİKLİK VARSA UPDATE ET VE TARİHİ GÜNCELLE
                    conn.execute(text("""
                        UPDATE muhasebe_kayitlari
                        SET komisyon_orani = :k,
                            toplam_kazanc = :tk,
                            odenen_komisyon = :o,
                            kalan_komisyon = :ka,
                            updated_at = :u,
                            updated_by = :ub
                        WHERE acente_adi = :a AND ay = :ay
                    """), {
                        "a": row["acente_adi"], "ay": row["ay"],
                        "k": row["komisyon_orani"], "tk": row["toplam_kazanc"],
                        "o": row["odenen_komisyon"], "ka": row["kalan_komisyon"],
                        "u": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "ub": current_user
                    })
            else:
                # YENİ KAYIT EKLEME
                conn.execute(text("""
                    INSERT INTO muhasebe_kayitlari (
                        acente_adi, ay, net_prim, toplam_komisyon, 
                        komisyon_orani, toplam_kazanc, odenen_komisyon, 
                        kalan_komisyon, updated_at, updated_by
                    )
                    VALUES (:a, :ay, :n, :t, :k, :tk, :o, :ka, :u, :ub)
                """), {
                    "a": row["acente_adi"], "ay": row["ay"], "n": row["net_prim"],
                    "t": row["toplam_komisyon"], "k": row["komisyon_orani"],
                    "tk": row["toplam_kazanc"], "o": row["odenen_komisyon"],
                    "ka": row["kalan_komisyon"],
                    "u": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "ub": current_user
                })
