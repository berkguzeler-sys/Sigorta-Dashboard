import streamlit as st
import pandas as pd
import plotly.express as px
import time
import numpy as np

# --------------------------------------------------
# SAYFA AYARI
# --------------------------------------------------
st.set_page_config(page_title="Polipedia Analiz", layout="wide")

import streamlit as st
import os

def load_svg_maskot(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return None

svg_icon = load_svg_maskot("maskot-onay-01.svg")

if svg_icon:
    st.markdown(f"""
    <style>
    /* 1. MASKOT KONUMU - SAYFA BAŞINDA SABİT */
    .poli-wrapper {{
        position: absolute; 
        top: 20px; 
        right: 40px;
        width: 100px;
        z-index: 99999;
    }}

    /* 2. SOL YANDA AÇILAN BALON */
    .poli-bubble-side {{
        position: absolute;
        top: 30px; /* Kafasından biraz aşağı, gövde hizasına */
        right: 115%; /* Karakterin soluna atar */
        transform: scale(0); /* Başlangıçta gizli */
        
        background-color: #ffffff; 
        color: #6a2473; 
        
        padding: 10px 18px;
        border-radius: 18px 18px 0px 18px; /* Sol alt köşeyi keskin yaparak yön gösterir */
        font-size: 15px; 
        font-weight: 800;
        
        box-shadow: -10px 10px 25px rgba(0,0,0,0.2);
        border: 2px solid #6a2473;
        
        white-space: nowrap;
        opacity: 0;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        pointer-events: none;
        z-index: 100000;
    }}

    /* Balonun yan kuyruğu (Karaktere doğru bakan küçük ok) */
    .poli-bubble-side::after {{
        content: '';
        position: absolute;
        right: -10px;
        top: 50%;
        transform: translateY(-50%);
        border-width: 8px 0 8px 10px;
        border-style: solid;
        border-color: transparent transparent transparent #ffffff;
    }}
    
    /* Kuyruk çerçevesi için dış katman */
    .poli-bubble-side::before {{
        content: '';
        position: absolute;
        right: -13px;
        top: 50%;
        transform: translateY(-50%);
        border-width: 10px 0 10px 13px;
        border-style: solid;
        border-color: transparent transparent transparent #6a2473;
        z-index: -1;
    }}

    /* 3. ETKİLEŞİM */
    .poli-wrapper:hover .poli-bubble-side {{
        opacity: 1;
        transform: scale(1);
        right: 120%; /* Biraz daha sola açılır */
    }}

    .poli-wrapper:hover {{
        transform: scale(1.05);
        cursor: pointer;
    }}
    </style>

    <div class="poli-wrapper">
        <div class="poli-bubble-side">Merhaba Ben Poli! 👋</div>
        {svg_icon}
    </div>
    """, unsafe_allow_html=True)
# --------------------------------------------------
# PREMIUM ADAPTIVE CSS (Karanlık & Aydınlık Tema Uyumu)
# --------------------------------------------------

st.markdown("""
<style>

/* 1. ANA ARKA PLAN VE METİN AYARI */
/* Kullanıcı bilgisayarı beyaz olsa bile bu dashboard'un kendi koyu temasını korumasını sağlar */
.stApp {
    background: radial-gradient(circle at top left, #6a2473 0%, #212a35 40%, #020617 100%) !important;
    color: #F8FAFC !important;
}

/* 2. OKUNURLUK FIX (Zorunlu Renk Tanımlamaları) */
/* Streamlit'in varsayılan beyaz tema yazılarını ezer */
html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label {
    color: #F8FAFC !important;
}

/* 3. SIDEBAR TEMASI */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1f2e, #020617) !important;
    border-right: 1px solid rgba(255,255,255,0.1);
}
section[data-testid="stSidebar"] * {
    color: #F8FAFC !important;
}

/* 4. INPUT VE SELECTBOX AYARLARI (Beyaz ekranda görünmesi için) */
.stSelectbox div, .stMultiSelect div, .stTextInput div, .stDateInput div {
    background-color: rgba(255, 255, 255, 0.05) !important;
    color: white !important;
}

/* 5. KPI CARD AYARLARI */
.kpi-card {
    backdrop-filter: blur(16px);
    background: linear-gradient(145deg, rgba(106,36,115,0.3), rgba(33,42,53,0.8));
    border-radius: 18px;
    padding: 15px 10px;
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0 12px 35px rgba(0,0,0,0.5);
    transition: all 0.3s ease;
    height: 110px;
    text-align: center;
}

.kpi-card:hover {
    transform: translateY(-5px);
    border-color: #e9617b;
    box-shadow: 0 15px 40px rgba(233,97,123,0.2);
}

.kpi-title {
    font-size: 12px;
    color: #CBD5E1 !important; /* Daha parlak gri */
    font-weight: 500;
    margin-bottom: 5px;
}

.kpi-value {
    font-size: 24px;
    font-weight: 800;
    background: linear-gradient(90deg, #e9617b, #f5a150);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* 6. TAB VE METRIC CARD */
.stTabs [aria-selected="true"] {
    color: #e9617b !important;
    border-bottom: 2px solid #e9617b !important;
}

.metric-card {
    background: rgba(255, 255, 255, 0.05);
    padding: 20px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.1);
}

/* 7. DATA EDITOR FIX (Tablo içindeki yazıların beyaz kalması için) */
div[data-testid="stDataEditor"] * {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# Başlık en üstte
st.title("📊 Polipedia Analiz")

# Sekmeler
tab1, tab2,= st.tabs(["📊 Dashboard", "💰 Muhasebe"])

# --------------------------------------------------
# VERİ KAYNAĞI
# --------------------------------------------------
excel_url = f"https://raw.githubusercontent.com/berkguzeler-sys/Sigorta-Dashboard/main/Acente_Analiz.xlsx?{int(time.time())}"

st.sidebar.header("📂 Veri Kaynağı")
if st.sidebar.button("🔄 Veriyi Yenile"):
    st.cache_data.clear()
uploaded_file = st.sidebar.file_uploader("Excel yükle", type=["xlsx"])

@st.cache_data(ttl=60)
def load_data(source):
    return pd.read_excel(source)

def run_etl(data):
    df = data.copy()

    # --------------------------------------------------
    # KOLON İSİMLERİNİ TEMİZLE
    # --------------------------------------------------
    df.columns = df.columns.str.strip()

    # Son satır toplam satırıysa kaldır
    if len(df) > 0:
        df = df.iloc[:-1].copy()

    # --------------------------------------------------
    # POLİÇE TÜRÜ KOD TEMİZLİĞİ
    # --------------------------------------------------
    if "Poliçe Türü Kod" in df.columns:
        df["Poliçe Türü Kod"] = (
            df["Poliçe Türü Kod"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        df.loc[df["Poliçe Türü Kod"].isin(["145", "YI1", "EEİ"]), "Poliçe Türü"] = "YANGIN"
        df.loc[df["Poliçe Türü Kod"] == "611", "Poliçe Türü"] = "SAĞLIK"
        df.loc[df["Poliçe Türü Kod"] == "524", "Poliçe Türü"] = "SEYAHAT SAĞLIK"

    if "Poliçe Türü" in df.columns:
        df["Poliçe Türü"] = df["Poliçe Türü"].fillna("DİĞER")
    else:
        df["Poliçe Türü"] = "DİĞER"

    # --------------------------------------------------
    # ŞİRKET DÜZELTME
    # --------------------------------------------------
    if "Sigorta Şirketi" in df.columns:
        df["Sigorta Şirketi"] = df["Sigorta Şirketi"].replace(
            "TÜRKİYE PUSULA", "TÜRKİYE SİGORTA"
        )

    # --------------------------------------------------
    # GEREKSİZ KOLONLARI SİL
    # --------------------------------------------------
    silinecek_kolonlar = [
        'İskonto',
        'Kayıt Şekli',
        'Sms Gönderme',
        'Mütabakat',
        'Açıklama',
        'Kalan Borç',
        'T.C. / VKn',
        'Referans Kişi',
        'Teklif Durumu',
        'Şube',
        'Belge Seri/Diğer',
        'Alınan Ödeme Tipi',
        'Eski Plaka',
        'Aracıyım',
        'Şirkete Ödeme Tipi',
        'Diğer Acente Adı',
        'Diğer A.Komisyon Tutarı'
    ]
    df = df.drop(columns=silinecek_kolonlar, errors="ignore")

    # --------------------------------------------------
    # DIŞ ACENTE ADI TEMİZLİĞİ
    # --------------------------------------------------
    if "Dış Acente Adı" in df.columns:
        df["Dış Acente Adı"] = (
            df["Dış Acente Adı"]
            .replace(['-', ' - ', None, ''], 'POLIPEDIA')
            .astype(str)
            .str.strip()
            .str.upper()
        )
    else:
        df["Dış Acente Adı"] = "POLIPEDIA"

    # --------------------------------------------------
    # TARİH VE AY
    # --------------------------------------------------
    if "Tanzim Tarihi" in df.columns:
        df["Tanzim Tarihi"] = pd.to_datetime(df["Tanzim Tarihi"], errors="coerce")
        df = df[df["Tanzim Tarihi"].notna()].copy()
        df["Ay"] = df["Tanzim Tarihi"].dt.to_period("M").astype(str)
    else:
        df["Tanzim Tarihi"] = pd.NaT
        df["Ay"] = ""

    # --------------------------------------------------
    # SAYISAL KOLONLAR
    # --------------------------------------------------
    for col in ["Net Prim", "Asıl Komisyon"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            df[col] = 0

    # --------------------------------------------------
    # KOMİSYON HESAPLARI
    # --------------------------------------------------
    if {"Dış Acente Adı", "Ay", "Net Prim"}.issubset(df.columns):
        toplam_net_prim = df.groupby(["Dış Acente Adı", "Ay"])["Net Prim"].transform("sum")

        kosullar = [
            (toplam_net_prim <= 250000),
            (toplam_net_prim <= 500000),
            (toplam_net_prim > 500000)
        ]
        oranlar = [0.55, 0.60, 0.65]

        df["Komisyon Oranı"] = np.select(kosullar, oranlar, default=0)
        df.loc[df["Dış Acente Adı"] == "POLIPEDIA", "Komisyon Oranı"] = 1.0
        df["Komisyon Oranı (%)"] = (df["Komisyon Oranı"] * 100).round(2)
    else:
        df["Komisyon Oranı"] = 0
        df["Komisyon Oranı (%)"] = 0

    df["Acente Komisyon Kazancı"] = np.where(
        df["Dış Acente Adı"] != "POLIPEDIA",
        df["Komisyon Oranı"] * df["Asıl Komisyon"],
        0
    )

    df["Polipedia Komisyon Kazancı"] = np.where(
        df["Dış Acente Adı"] == "POLIPEDIA",
        df["Asıl Komisyon"],
        0
    )

    df["Acente Mi?"] = np.where(
        df["Dış Acente Adı"] != "POLIPEDIA",
        1,
        0
    )

    df["Polipedia Net Prim"] = np.where(
        df["Dış Acente Adı"] == "POLIPEDIA",
        df["Net Prim"],
        0
    )

    df["Acente Net Prim"] = np.where(
        df["Dış Acente Adı"] != "POLIPEDIA",
        df["Net Prim"],
        0
    )

    df["Acenteden Gelen Komisyon"] = np.where(
        pd.to_numeric(df["Acente Komisyon Kazancı"], errors="coerce").fillna(0) != 0,
        pd.to_numeric(df["Asıl Komisyon"], errors="coerce").fillna(0)
        - pd.to_numeric(df["Acente Komisyon Kazancı"], errors="coerce").fillna(0),
        0
    )

    # --------------------------------------------------
    # APP.PY'NİN KULLANDIĞI İSİMLERE ÇEVİR
    # --------------------------------------------------
    rename_map = {
        "Asıl Komisyon": "Toplam Komisyon",
        "Dış Acente Adı": "Acente Adı",
        "Poliçe Türü": "Branş"
    }
    df.rename(columns=rename_map, inplace=True)

    # --------------------------------------------------
    # YARDIMCI KOLONLAR
    # --------------------------------------------------
    # --------------------------------------------------
    # UNIQUE ADET HESAPLARI (TEKİL POLİÇE BAZLI)
    # --------------------------------------------------

    # Poliçe No string olsun (çok önemli)
    df["Poliçe No"] = df["Poliçe No"].astype(str)

    # Tekil poliçe flag (duplicate varsa sadece ilkini alır)
    df["tekil_flag"] = ~df["Poliçe No"].duplicated()

    # -------------------------
    # POLİÇE ADET
    # -------------------------
    df["Poliçe Adet"] = df["tekil_flag"].astype(int)

    # -------------------------
    # ACENTE ADET (UNIQUE)
    # -------------------------
    df["Acente Adet"] = np.where(
        (df["Acente Mi?"] == 1) & (df["tekil_flag"]),
        1,
        0
    )

    # -------------------------
    # POLIPEDIA ADET (UNIQUE)
    # -------------------------
    df["Polipedia Adet"] = np.where(
        (df["Acente Mi?"] == 0) & (df["tekil_flag"]),
        1,
        0
    )
    # --------------------------------------------------
    # İPTAL ANALİZİ (UNIQUE POLİÇE BAZLI)
    # --------------------------------------------------

    # Kayıt Türü güvenli hale getir
    df["Kayıt Türü"] = df["Kayıt Türü"].astype(str).str.strip()

    # İptal flag
    df["İptal Flag"] = np.where(
        df["Kayıt Türü"] == "İptal Zeyl-",
        1,
        0
    )

    # Tekil poliçe bazında iptal var mı?
    iptal_df = df.groupby("Poliçe No")["İptal Flag"].max().reset_index()

    iptal_df.rename(columns={"İptal Flag": "İptal Edildi"}, inplace=True)

    # Ana df ile birleştir
    df = df.merge(iptal_df, on="Poliçe No", how="left")

    # Tekil poliçelerde iptal say
    df["İptal Poliçe Adet"] = np.where(
        (df["İptal Edildi"] == 1) & (df["tekil_flag"]),
        1,
        0
    )
       

    # --------------------------------------------------
    # EKSİK KOLON GÜVENLİĞİ
    # --------------------------------------------------
    gerekli_kolonlar = [
        "Net Prim", "Poliçe No", "Acente Adı", "Branş",
        "Acente Net Prim", "Toplam Komisyon",
        "Acente Komisyon Kazancı", "Polipedia Komisyon Kazancı",
        "Acenteden Gelen Komisyon"
    ]

    for col in gerekli_kolonlar:
        if col not in df.columns:
            if col in [
                "Net Prim", "Acente Net Prim", "Toplam Komisyon",
                "Acente Komisyon Kazancı", "Polipedia Komisyon Kazancı",
                "Acenteden Gelen Komisyon"
            ]:
                df[col] = 0
            else:
                df[col] = ""

    return df

try:
    if uploaded_file is not None:
        df_raw = load_data(uploaded_file)
    else:
        df_raw = load_data(excel_url)

    df = run_etl(df_raw)

except Exception as e:
    st.error("❌ Veri yüklenemedi!")
    st.write(e)
    st.stop()


# --------------------------------------------------
# SIDEBAR FİLTRELER
# --------------------------------------------------
st.sidebar.header("🔎 Filtreler")

min_date = df["Tanzim Tarihi"].min().date()
max_date = df["Tanzim Tarihi"].max().date()

date_range = st.sidebar.date_input(
    "Tanzim Tarihi",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

df_filtre = df.copy()

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

    df_filtre = df_filtre[
        (df_filtre["Tanzim Tarihi"] >= start_date) &
        (df_filtre["Tanzim Tarihi"] <= end_date)
    ]

brans_secim = st.sidebar.multiselect(
    "Branş",
    sorted(df_filtre["Branş"].dropna().astype(str).unique())
)

acente_secim = st.sidebar.multiselect(
    "Acente Adı",
    sorted(df_filtre["Acente Adı"].dropna().astype(str).unique())
)

if brans_secim:
    df_filtre = df_filtre[df_filtre["Branş"].isin(brans_secim)]

if acente_secim:
    df_filtre = df_filtre[df_filtre["Acente Adı"].isin(acente_secim)]

# --------------------------------------------------
# PREMIUM RENK PALETİ VE RENK HARİTASI
# --------------------------------------------------
premium_colors = ["#6a2473", "#e9617b", "#f5a150", "#34a49a", "#2c5055", "#212a35", "#F87171", "#2DD4BF", "#E879F9", "#94A3B8"]

# Branşlar için Sabit Renk Haritası
unique_types = sorted(df["Branş"].dropna().astype(str).unique())
color_map = {ptype: premium_colors[i % len(premium_colors)] for i, ptype in enumerate(unique_types)}

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------
with tab1:
    # KPI
    toplam_poliçe = df_filtre["Poliçe No"].count()
    toplam_net_prim = pd.to_numeric(df_filtre["Net Prim"], errors="coerce").fillna(0).sum()
    toplam_acente_adet = pd.to_numeric(df_filtre["Acente Adet"], errors="coerce").fillna(0).sum()
    toplam_polipedia_adet = pd.to_numeric(df_filtre["Polipedia Adet"], errors="coerce").fillna(0).sum()
    toplam_acente_komisyon = pd.to_numeric(df_filtre["Acente Komisyon Kazancı"], errors="coerce").fillna(0).sum()
    toplam_polipedia_komisyon = pd.to_numeric(df_filtre["Polipedia Komisyon Kazancı"], errors="coerce").fillna(0).sum()
    toplam_yk_kazanc = (
        pd.to_numeric(df_filtre["Polipedia Komisyon Kazancı"], errors="coerce").fillna(0).sum() +
        pd.to_numeric(df_filtre.get("Acenteden Gelen Komisyon", 0), errors="coerce").fillna(0).sum()
    )

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

    def kpi(title, val):
        return f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{val}</div>
        </div>
        """

    col1.markdown(kpi("Toplam Poliçe Adet", f"{toplam_poliçe:,}"), unsafe_allow_html=True)
    col2.markdown(kpi("Toplam Net Prim", f"₺{toplam_net_prim:,.0f}"), unsafe_allow_html=True)
    col3.markdown(kpi("Acente Poliçe Adet", f"{toplam_acente_adet:,}"), unsafe_allow_html=True)
    col4.markdown(kpi("Polipedia Poliçe Adet", f"{toplam_polipedia_adet:,}"), unsafe_allow_html=True)
    col5.markdown(kpi("Acente Komisyon", f"₺{toplam_acente_komisyon:,.0f}"), unsafe_allow_html=True)
    col6.markdown(kpi("Polipedia Komisyon", f"₺{toplam_polipedia_komisyon:,.0f}"), unsafe_allow_html=True)
    col7.markdown(kpi("Polipedia Gelir", f"₺{toplam_yk_kazanc:,.0f}"), unsafe_allow_html=True)

    st.divider()

    # --------------------------------------------------
    # BRANŞ ANALİZİ
    # --------------------------------------------------
    st.subheader("📊 Branş Analizi")

    col_pt1, col_pt2 = st.columns([1, 1])

    with col_pt1:
        brans_metric = st.radio(
            "Gösterilecek Değer",
            ["Net Prim", "Poliçe Adet"],
            horizontal=True,
            key="brans_metric"
        )

    with col_pt2:
        grafik = st.radio(
            "Grafik Tipi",
            ["Bar", "Pie"],
            horizontal=True,
            key="brans_grafik"
        )

    df_ozet = df_filtre.groupby("Branş", dropna=False).agg({
        "Net Prim": "sum",
        "Poliçe No": "count"
    }).reset_index()

    df_ozet.rename(columns={"Poliçe No": "Poliçe Adet"}, inplace=True)

    if brans_metric == "Net Prim":
        value_col = "Net Prim"
        title_text = "Branşa Göre Net Prim Dağılımı"
        text_template = "₺%{y:,.0f}" if grafik == "Bar" else "%{percent}"
    else:
        value_col = "Poliçe Adet"
        title_text = "Branşa Göre Poliçe Adet Dağılımı"
        text_template = "%{y}" if grafik == "Bar" else "%{percent}"

    df_ozet = df_ozet.sort_values(by=value_col, ascending=False)

    if grafik == "Bar":
        fig_brans = px.bar(
            df_ozet,
            x="Branş",
            y=value_col,
            color="Branş",
            color_discrete_map=color_map,
            text=value_col
        )
        fig_brans.update_traces(
            texttemplate=text_template,
            textposition="outside",
            marker_line_width=0
        )
        fig_brans.update_layout(
            title=title_text,
            template="plotly_dark",
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Branş",
            yaxis_title=f"{brans_metric} (₺)" if brans_metric == "Net Prim" else brans_metric,
            xaxis=dict(tickangle=-20),
            margin=dict(l=20, r=20, t=60, b=20)
        )
    else:
        fig_brans = px.pie(
            df_ozet,
            names="Branş",
            values=value_col,
            color="Branş",
            color_discrete_map=color_map,
            hole=0.50
        )
        fig_brans.update_traces(
            textinfo="percent+label",
            textposition="inside",
            insidetextorientation="radial"
        )
        fig_brans.update_layout(
            title=title_text,
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            height=600,
            margin=dict(l=0, r=0, t=80, b=0),
            legend=dict(
                orientation="v",
                y=0.5,
                x=1.05

            )
        )

    st.plotly_chart(fig_brans, use_container_width=True)

    st.divider()
    

    # --------------------------------------------------
    # GÜNLÜK / AYLIK TAKİP
    # --------------------------------------------------
    st.subheader("📈 Günlük ve Aylık Takip")

    metric_secim = st.radio(
        "Gösterilecek Metrik",
        ["Net Prim", "Poliçe Adet"],
        horizontal=True,
        key="gunluk_aylik_metric"
    )

    df_gunluk = df_filtre.groupby("Tanzim Tarihi").agg({
        "Net Prim": "sum",
        "Poliçe No": "count"
    }).reset_index()

    df_aylik = df_filtre.groupby("Ay").agg({
        "Net Prim": "sum",
        "Poliçe No": "count"
    }).reset_index()

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown("**Günlük Analiz**")
        if metric_secim == "Net Prim":
            fig_gun = px.line(df_gunluk, x="Tanzim Tarihi", y="Net Prim", markers=True, color_discrete_sequence=["#34a49a"])
            fig_gun.update_layout(yaxis_title="Net Prim (₺)")
        else:
            fig_gun = px.line(df_gunluk, x="Tanzim Tarihi", y="Poliçe No", markers=True, color_discrete_sequence=["#34a49a"])
            fig_gun.update_layout(yaxis_title="Poliçe Adet")

        fig_gun.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_gun, use_container_width=True)

    with col_g2:
        st.markdown("**Aylık Analiz**")
        if metric_secim == "Net Prim":
            fig_ay = px.bar(df_aylik, x="Ay", y="Net Prim", color_discrete_sequence=["#6a2473"], text="Net Prim")
            fig_ay.update_traces(texttemplate='₺%{text:,.0f}', textposition='outside')
            fig_ay.update_layout(yaxis_title="Net Prim (₺)")
        else:
            fig_ay = px.bar(df_aylik, x="Ay", y="Poliçe No", color_discrete_sequence=["#6a2473"], text="Poliçe No")
            fig_ay.update_traces(texttemplate='%{text}', textposition='outside')
            fig_ay.update_layout(yaxis_title="Poliçe Adet")

        fig_ay.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_ay, use_container_width=True)

    st.divider()

    # --------------------------------------------------
    # 🚨 İPTAL ORANI ANALİZİ
    # --------------------------------------------------
    st.subheader("🚨 İptal Oranı Analizi")

    if not df_filtre.empty:

        # Unique poliçe bazlı
        df_iptal = df_filtre[df_filtre["tekil_flag"] == True].copy()

        toplam_poliçe = df_iptal["Poliçe Adet"].sum()
        iptal_poliçe = df_iptal["İptal Poliçe Adet"].sum()

        iptal_orani = (iptal_poliçe / toplam_poliçe) if toplam_poliçe != 0 else 0

        # KPI
        col_i1, col_i2, col_i3 = st.columns(3)

        col_i1.markdown(kpi("Toplam Poliçe", f"{int(toplam_poliçe):,}"), unsafe_allow_html=True)
        col_i2.markdown(kpi("İptal Poliçe", f"{int(iptal_poliçe):,}"), unsafe_allow_html=True)
        col_i3.markdown(kpi("İptal Oranı", f"%{iptal_orani*100:.2f}"), unsafe_allow_html=True)

        

        df_acente_iptal = df_iptal.groupby("Acente Adı").agg({
            "Poliçe Adet": "sum",
            "İptal Poliçe Adet": "sum"
        }).reset_index()

        df_acente_iptal["İptal Oranı"] = np.where(
            df_acente_iptal["Poliçe Adet"] != 0,
            df_acente_iptal["İptal Poliçe Adet"] / df_acente_iptal["Poliçe Adet"],
            0
        )

        df_acente_iptal = df_acente_iptal.sort_values("İptal Oranı", ascending=False)

        # 🔥 PREMIUM GRAFİK
        df_plot = df_acente_iptal.copy()

        df_plot = df_plot.sort_values("İptal Oranı", ascending=False).head(10)
        df_plot["İptal %"] = df_plot["İptal Oranı"] * 100

        fig_iptal = px.bar(
            df_plot,
            x="İptal %",
            y="Acente Adı",
            orientation="h",
            text=df_plot["İptal %"].map(lambda x: f"%{x:.1f}"),
            color="İptal %",
            color_continuous_scale=["#34a49a", "#f5a150", "#e9617b"]
        )

        fig_iptal.update_traces(
            textposition="outside",
            marker_line_width=0,
            hovertemplate="<b>%{y}</b><br>İptal Oranı: %{x:.2f}%<extra></extra>"
        )

        fig_iptal.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title="İptal Oranı (%)",
            yaxis_title="",
            yaxis=dict(categoryorder="total ascending", tickfont=dict(size=13)),
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
            margin=dict(l=20, r=40, t=30, b=20),
            height=450,
            coloraxis_showscale=False
        )

        st.markdown("### 📋 Detay Tablo")

        df_display = df_acente_iptal.copy()
        df_display["İptal Oranı"] = df_display["İptal Oranı"].map(lambda x: f"%{x*100:.2f}")

        st.dataframe(df_display, use_container_width=True)

    else:
        st.warning("Veri bulunamadı")

    # --------------------------------------------------
    # ACENTE ANALİZ
    # --------------------------------------------------
    st.subheader("📊 Aylık Acente Net Prim (Polipedia Hariç)")

    df_acente = df_filtre[
        df_filtre["Acente Adı"].fillna("").str.upper() != "POLIPEDIA"
    ].copy()

    df_acente_aylik = df_acente.groupby(
        ["Acente Adı", "Ay"],
        dropna=False
    ).agg({
        "Acente Net Prim": "sum",
        "Toplam Komisyon": "sum",
        "Acente Komisyon Kazancı": "sum"
    }).reset_index()

    pivot = df_acente_aylik.pivot(
        index="Acente Adı",
        columns="Ay",
        values="Acente Net Prim"
    ).fillna(0)

    pivot_display = pivot.map(lambda x: f"₺{x:,.0f}") if not pivot.empty else pivot
    st.dataframe(pivot_display, use_container_width=True)

    # --------------------------------------------------
    # BAREM
    # --------------------------------------------------
    def barem(x):
        if x <= 250000:
            return "0-250K", 55, 250000 - x
        elif x <= 500000:
            return "250K-500K", 60, 500000 - x
        else:
            return "500K+", 65, 0

    if not df_acente_aylik.empty:
        df_acente_aylik[["Barem", "Komisyon %", "Bir Üst Bareme Kalan Tutar"]] = (
            df_acente_aylik["Acente Net Prim"].apply(lambda x: pd.Series(barem(x)))
        )
    else:
        df_acente_aylik["Barem"] = ""
        df_acente_aylik["Komisyon %"] = 0
        df_acente_aylik["Bir Üst Bareme Kalan Tutar"] = 0

    df_barem = df_acente_aylik[
        [
            "Acente Adı",
            "Ay",
            "Acente Net Prim",
            "Toplam Komisyon",
            "Acente Komisyon Kazancı",
            "Komisyon %",
            "Barem",
            "Bir Üst Bareme Kalan Tutar"
        ]
    ].copy()

    if not df_barem.empty:
        df_barem["Acente Net Prim"] = df_barem["Acente Net Prim"].apply(lambda x: f"₺{x:,.0f}")
        df_barem["Toplam Komisyon"] = df_barem["Toplam Komisyon"].apply(lambda x: f"₺{x:,.0f}")
        df_barem["Acente Komisyon Kazancı"] = df_barem["Acente Komisyon Kazancı"].apply(lambda x: f"₺{x:,.0f}")
        df_barem["Bir Üst Bareme Kalan Tutar"] = df_barem["Bir Üst Bareme Kalan Tutar"].apply(lambda x: f"₺{x:,.0f}")
        df_barem["Komisyon %"] = df_barem["Komisyon %"].apply(lambda x: f"%{x}")

    st.subheader("📊 Barem Analizi")
    st.dataframe(df_barem, use_container_width=True)

    st.divider()

    # --------------------------------------------------
    # ACENTE BAZINDA AYLIK BRANŞ ORANLARI
    # --------------------------------------------------
    st.subheader("📊 Acente Bazında Aylık Branş Oranları")

    col1, col2, col3 = st.columns(3)

    acente_list = sorted(df_filtre["Acente Adı"].dropna().astype(str).unique())
    acente_list = ["Tümü"] + acente_list

    with col1:
        secili_acente = st.multiselect(
            "Acente Adı",
            acente_list,
            default=["Tümü"]
        )

    ay_list = sorted(df_filtre["Ay"].dropna().astype(str).unique())
    ay_list = ["Tümü"] + ay_list

    with col2:
        secili_ay = st.multiselect(
            "Ay",
            ay_list,
            default=["Tümü"]
        )

    with col3:
        metric = st.radio(
            "Metrik",
            ["Net Prim", "Poliçe Adet"],
            horizontal=True,
            key="acente_brans_metric"
        )

    df_temp = df_filtre.copy()

    if "Tümü" not in secili_acente:
        df_temp = df_temp[df_temp["Acente Adı"].isin(secili_acente)]

    if "Tümü" not in secili_ay:
        df_temp = df_temp[df_temp["Ay"].isin(secili_ay)]

    if df_temp.empty:
        st.warning("Seçime uygun veri bulunamadı")
    else:
        df_group = df_temp.groupby("Branş").agg({
            "Net Prim": "sum",
            "Poliçe No": "count"
        }).reset_index()

        if metric == "Net Prim":
            toplam_deger = df_group["Net Prim"].sum()
            df_group["Oran"] = (df_group["Net Prim"] / toplam_deger * 100) if toplam_deger != 0 else 0
        else:
            toplam_deger = df_group["Poliçe No"].sum()
            df_group["Oran"] = (df_group["Poliçe No"] / toplam_deger * 100) if toplam_deger != 0 else 0

        df_group = df_group.sort_values("Oran", ascending=False)
        df_group_display = df_group.copy()
        df_group_display["Oran (%)"] = df_group_display["Oran"].map(lambda x: f"%{x:.2f}")

        col_table, col_chart = st.columns([1, 1.8])

        with col_table:
            st.markdown("### 📋 Oran Tablosu")
            st.dataframe(df_group_display[["Branş", "Oran (%)"]], use_container_width=True, height=350)

        with col_chart:
            st.markdown("### 🥧 Dağılım Grafiği")
            fig = px.pie(
                df_group,
                names="Branş",
                values="Oran",
                color="Branş",
                color_discrete_map=color_map,
                hole=0.40,
                height=450
            )
            fig.update_traces(textinfo="percent+label", textposition="inside")
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=50, b=0))
            st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------
    # ANALİZLER (Üst Bareme Yakın & Pasif)
    # --------------------------------------------------
    st.subheader("🚀 Bir Üst Bareme En Yakın 5 Acente")
    son_ay = df_acente_aylik["Ay"].max()
    df_yakin = df_acente_aylik[df_acente_aylik["Ay"] == son_ay].copy()
    df_yakin = df_yakin[df_yakin["Bir Üst Bareme Kalan Tutar"] > 0]
    df_yakin = df_yakin.sort_values("Bir Üst Bareme Kalan Tutar").head(5)

    if not df_yakin.empty:
        df_yakin_display = df_yakin.copy()
        df_yakin_display["Acente Net Prim"] = df_yakin_display["Acente Net Prim"].apply(lambda x: f"₺{x:,.0f}")
        df_yakin_display["Bir Üst Bareme Kalan Tutar"] = df_yakin_display["Bir Üst Bareme Kalan Tutar"].apply(lambda x: f"₺{x:,.0f}")
        st.dataframe(df_yakin_display[["Acente Adı", "Ay", "Acente Net Prim", "Barem", "Bir Üst Bareme Kalan Tutar"]], use_container_width=True)
    else:
        st.info("Uygun veri bulunamadı")

    st.divider()
 


    # --------------------------------------------------
    # SİGORTA ŞİRKETİ BAZINDA ANALİZ (EXECUTIVE PREMIUM V4 - SMART FOCUS)
    # --------------------------------------------------
    st.divider()
    st.subheader("🏢 Sigorta Şirketi Bazında Analiz")
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    sirket_kolon_adi = "Sigorta Şirketi" if "Sigorta Şirketi" in df_filtre.columns else "Şirket Adı"
    
    with col_s1:
        secili_s_acente = st.multiselect("Acente Filtresi", ["Tümü"] + sorted(df_filtre["Acente Adı"].unique()), default=["Tümü"], key="s_ac_v5")
    with col_s2:
        secili_sirket = st.multiselect("Şirket Seçimi", ["Tümü"] + sorted(df_filtre[sirket_kolon_adi].unique()), default=["Tümü"], key="s_sh_v5")
    with col_s3:
        secili_ay_s = st.multiselect("Dönem Seçimi", ["Tümü"] + sorted(df_filtre["Ay"].unique()), default=["Tümü"], key="s_ay_v5")
    with col_s4:
        s_metric = st.radio("Analiz Metriği", ["Net Prim", "Poliçe Adet"], horizontal=True, key="s_met_v5")

    # Filtreleme
    df_s = df_filtre.copy()
    if "Tümü" not in secili_s_acente: df_s = df_s[df_s["Acente Adı"].isin(secili_s_acente)]
    if "Tümü" not in secili_sirket: df_s = df_s[df_s[sirket_kolon_adi].isin(secili_sirket)]
    if "Tümü" not in secili_ay_s: df_s = df_s[df_s["Ay"].isin(secili_ay_s)]

    if not df_s.empty:
        m_col = "Net Prim" if s_metric == "Net Prim" else "Poliçe Adet"
        
        # --- Dinamik Analiz Mantığı ---
        tek_sirket_mi = len(secili_sirket) == 1 and "Tümü" not in secili_sirket
        
        if tek_sirket_mi:
            # Tek şirket seçiliyse: Acente Dağılımına Odaklan (Polipedia hariç ilk 10)
            df_plot = df_s[df_s["Acente Adı"].str.upper() != "POLIPEDIA"].groupby("Acente Adı")[m_col].sum().reset_index()
            df_plot = df_plot.sort_values(m_col, ascending=True).tail(10) # En iyi 10 acente
            y_axis_col = "Acente Adı"
            grafik_baslik = f"📊 {secili_sirket[0]} Bünyesindeki En İyi 10 Acente"
        else:
            # Çoklu seçim: Şirket Dağılımına Odaklan
            df_plot = df_s.groupby(sirket_kolon_adi)[m_col].sum().reset_index()
            df_plot = df_plot.sort_values(m_col, ascending=True)
            y_axis_col = sirket_kolon_adi
            grafik_baslik = f"📊 {s_metric} Pazar Dağılımı"

        # --- Üst Özet Panel (Aynı Kalıyor) ---
        df_s_group = df_s.groupby(sirket_kolon_adi)[m_col].sum().reset_index().sort_values(m_col, ascending=True)
        lider_sirket = df_s_group.iloc[-1][sirket_kolon_adi]
        lider_deger = df_s_group.iloc[-1][m_col]
        fmt_deger = f"₺{lider_deger:,.0f}" if s_metric == "Net Prim" else f"{lider_deger:,} Adet"
        
        df_lider_data = df_s[(df_s[sirket_kolon_adi] == lider_sirket) & (df_s["Acente Adı"].str.upper() != "POLIPEDIA")]
        if not df_lider_data.empty:
            ac_sum = df_lider_data.groupby("Acente Adı")[m_col].sum()
            lider_acente_bilgi = f"{ac_sum.idxmax()} ({'₺' if s_metric == 'Net Prim' else ''}{ac_sum.max():,.0f})"
        else:
            lider_acente_bilgi = "Dış Acente Kaydı Yok"

        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.03); padding: 25px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 25px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px;">
                    <div>
                        <div style="color: #94A3B8; font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px;">🏆 En Çok Üretim Yapılan Şirket</div>
                        <div style="color: #f5a150; font-weight: 800; font-size: 28px; line-height: 1.2;">{lider_sirket}</div>
                        <div style="color: #e9617b; font-weight: 600; font-size: 18px; margin-top: 5px;">Toplam Hacim: {fmt_deger}</div>
                    </div>
                    <div style="border-left: 2px dashed rgba(56, 189, 248, 0.3); padding-left: 30px;">
                        <div style="color: #94A3B8; font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px;">⭐ Şirketin Lokomotif Acentesi</div>
                        <div style="color: #38BDF8; font-weight: 800; font-size: 22px; line-height: 1.2;">{lider_acente_bilgi}</div>
                        <div style="color: #64748B; font-size: 13px; font-style: italic; margin-top: 5px;">*Polipedia dışı üretim verilerine dayanmaktadır.</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        c_table, c_chart = st.columns([1, 2.2])
        with c_table:
            st.markdown("##### 📋 Kurumsal Sıralama")
            disp_df = df_plot.sort_values(m_col, ascending=False).copy()
            if s_metric == "Net Prim": disp_df[m_col] = disp_df[m_col].map("₺{:,.0f}".format)
            st.dataframe(disp_df, use_container_width=True, height=450, hide_index=True)
            
        with c_chart:
            st.markdown(f"##### {grafik_baslik}")
            fig_s = px.bar(
                df_plot, x=m_col, y=y_axis_col, orientation='h',
                text=m_col, color=m_col, color_continuous_scale='Portland'
            )
            text_fmt = "₺%{text:,.0f}" if s_metric == "Net Prim" else "%{text:,}"
            fig_s.update_traces(texttemplate=text_fmt, textposition='outside', cliponaxis=False, width=0.7)
            fig_s.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(categoryorder='total ascending', tickfont=dict(size=12)),
                margin=dict(l=10, r=180, t=10, b=10), height=500, coloraxis_showscale=False
            )
            st.plotly_chart(fig_s, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("Kriterlere uygun veri bulunamadı.")


    # --------------------------------------------------
# 🏆 TOP 5 + PASİF ACENTE ANALİZİ (YAN YANA)
# --------------------------------------------------
    st.subheader("🏆 Acente Performans Özeti")

    col_perf1, col_perf2 = st.columns(2)

    with col_perf1:
        st.markdown("### 🚀 En Çok Üreten 5 Acente")

        df_top5 = df_filtre[
            df_filtre["Acente Adı"].fillna("").str.upper() != "POLIPEDIA"
        ].groupby("Acente Adı").agg({
            "Net Prim": "sum",
            "Poliçe No": "count"
        }).reset_index()

        df_top5 = df_top5.sort_values(by="Net Prim", ascending=False).head(5)

        if not df_top5.empty:
            df_top5_display = df_top5.copy()
            df_top5_display.rename(columns={"Poliçe No": "Poliçe Adet"}, inplace=True)
            df_top5_display["Net Prim"] = df_top5_display["Net Prim"].apply(lambda x: f"₺{x:,.0f}")

            st.dataframe(
                df_top5_display[["Acente Adı", "Net Prim", "Poliçe Adet"]],
                use_container_width=True,
                height=315
            )
        else:
            st.info("Top 5 acente verisi bulunamadı.")

    with col_perf2:
        st.markdown("### ⚠️ Son 1 Aydır Üretim Yapmayan Acenteler")

        max_tarih = df["Tanzim Tarihi"].max()
        son_1_ay = max_tarih - pd.Timedelta(days=30)

        aktif_acente = df[
            (df["Tanzim Tarihi"] >= son_1_ay) &
            (df["Acente Adı"].fillna("").str.upper() != "POLIPEDIA")
        ]["Acente Adı"].dropna().unique()

        tum_acente = df[
            df["Acente Adı"].fillna("").str.upper() != "POLIPEDIA"
        ]["Acente Adı"].dropna().unique()

        pasif_acente = sorted(set(tum_acente) - set(aktif_acente))

        if pasif_acente:
            df_pasif = pd.DataFrame(pasif_acente, columns=["Acente Adı"])
            st.dataframe(df_pasif, use_container_width=True, height=315)
        else:
            st.success("Tüm acenteler son 1 ayda üretim yapmış 🎯")

    st.divider()    

with tab2:
    st.subheader("💰 Muhasebe ve Komisyon Düzenleme")

    import io
    from datetime import datetime

    # --- PREMIUM CSS (Tüm Butonlar ve Kartlar İçin) ---
    st.markdown("""
    <style>
    /* Genel Buton Tasarımı */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #1E293B, #334155);
        color: white;
        border-radius: 8px;
        border: 1px solid rgba(255,255,255,0.1);
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    /* Aksiyon Butonları Renk Geçişleri */
    .st-emotion-cache-12w04pk.ef3ps4l4 { /* Primary buton için özel (Güncelle) */
        background: linear-gradient(90deg, #38BDF8, #818CF8) !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        border-color: #38BDF8;
    }
    /* KPI Kart Tasarımı */
    .metric-card {
        background: rgba(30, 41, 59, 0.4);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.05);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    # 🔥 INFO BOX
    st.markdown("""
    <div style="background: rgba(56,189,248,0.1); padding:10px 15px; border-radius:10px; border-left:4px solid #38BDF8; margin-bottom:20px; color:#CBD5F5; font-size:14px;">
    💡 <b>İpucu:</b> Komisyon oranını değiştirip "Hesaplamaları Güncelle" butonuna basarak farkları görebilirsiniz.
    </div>
    """, unsafe_allow_html=True)

    # Session State Başlatma
    if 'df_muhasebe' not in st.session_state:
        df_init = df_acente_aylik[[
            "Acente Adı", "Ay", "Acente Net Prim",
            "Toplam Komisyon", "Komisyon %", "Acente Komisyon Kazancı"
        ]].copy()
        df_init.rename(columns={"Acente Komisyon Kazancı": "Acente Toplam Kazanç"}, inplace=True)
        df_init["İlk Kazanç"] = df_init["Acente Toplam Kazanç"].fillna(0)
        df_init["İlk Komisyon %"] = df_init["Komisyon %"]
        df_init["Güncel Komisyon Farkı"] = 0.0
        df_init["Acenteye Ödenen Komisyon"] = 0.0
        df_init["Kalan Komisyon Tutarı"] = 0.0
        df_init["_row_id"] = range(len(df_init))
        st.session_state.df_muhasebe = df_init

    if "muhasebe_versions" not in st.session_state:
        st.session_state.muhasebe_versions = []

    # Yardımcı Fonksiyonlar
    def _to_excel_bytes(df_export):
        output = io.BytesIO()
        export_df = df_export.drop(columns=["_row_id"], errors="ignore").copy()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            export_df.to_excel(writer, index=False, sheet_name="Muhasebe")
        return output.getvalue()

    # --------------------------------------------------
    # KOMPAKT FİLTRELEME ALANI
    # --------------------------------------------------
    with st.expander("🔍 Filtreleme Seçenekleri", expanded=False):
        f_col1, f_col2, f_col3 = st.columns([2, 2, 1])
        
        with f_col1:
            acente_listesi = sorted(st.session_state.df_muhasebe["Acente Adı"].dropna().unique().tolist())
            secili_acenteler = st.multiselect("Acente Seç", options=acente_listesi, key="m_f_acente")
            
        with f_col2:
            ay_listesi = sorted(st.session_state.df_muhasebe["Ay"].dropna().unique().tolist())
            secili_aylar = st.multiselect("Ay Seç", options=ay_listesi, key="m_f_ay")
            
        with f_col3:
            st.write("") # Boşluk
            st.write("") # Boşluk
            if st.button("🧹 Filtreleri Temizle"):
                st.session_state.m_f_acente = []
                st.session_state.m_f_ay = []
                st.rerun()

    # Filtreleme Uygulama
    df_filtered = st.session_state.df_muhasebe.copy()
    if secili_acenteler:
        df_filtered = df_filtered[df_filtered["Acente Adı"].isin(secili_acenteler)]
    if secili_aylar:
        df_filtered = df_filtered[df_filtered["Ay"].isin(secili_aylar)]

    # --------------------------------------------------
    # VERİ EDİTÖRÜ
    # --------------------------------------------------
    edited_df = st.data_editor(
        df_filtered,
        height=400,
        column_config={
            "Acente Adı": st.column_config.TextColumn("Acente", disabled=True),
            "Ay": st.column_config.TextColumn("Ay", disabled=True),
            "Acente Net Prim": st.column_config.NumberColumn("Net Prim", format="₺%,.0f", disabled=True),
            "Toplam Komisyon": st.column_config.NumberColumn("Toplam Komisyon", format="₺%,.0f", disabled=True),
            "Komisyon %": st.column_config.NumberColumn("Komisyon %", min_value=0, max_value=100, format="%d%%"),
            "Acente Toplam Kazanç": st.column_config.NumberColumn("Toplam Kazanç", format="₺%,.2f", disabled=True),
            "Acenteye Ödenen Komisyon": st.column_config.NumberColumn("Ödenen", format="₺%,.2f"),
            "Güncel Komisyon Farkı": st.column_config.NumberColumn("Fark (Puan)", format="%d", disabled=True),
            "Kalan Komisyon Tutarı": st.column_config.NumberColumn("Kalan", format="₺%,.2f", disabled=True),
            "İlk Kazanç": None, "İlk Komisyon %": None, "_row_id": None,
        },
        hide_index=True,
        use_container_width=True,
        key="muhasebe_editor_v6"
    )

    # Butonlar İçin Sütunlar
    b_col1, b_col2, b_col3, b_col4 = st.columns(4)

    with b_col1:
        if st.button("🚀 Hesaplamaları Güncelle", type="primary"):
            # Hesaplama mantığı
            edited_df["Acente Toplam Kazanç"] = (edited_df["Toplam Komisyon"] * edited_df["Komisyon %"]) / 100
            edited_df["Güncel Komisyon Farkı"] = edited_df["Komisyon %"] - edited_df["İlk Komisyon %"]
            edited_df["Kalan Komisyon Tutarı"] = edited_df["Acente Toplam Kazanç"] - edited_df["Acenteye Ödenen Komisyon"].fillna(0)
            
            # Ana session state'i güncelle
            df_full = st.session_state.df_muhasebe.copy().set_index("_row_id")
            df_edit = edited_df.set_index("_row_id")
            df_full.update(df_edit)
            st.session_state.df_muhasebe = df_full.reset_index()
            st.rerun()

    with b_col2:
        if st.button("💾 Versiyon Kaydet"):
            mevcut_df = st.session_state.df_muhasebe.copy()
            versiyon_no = len(st.session_state.muhasebe_versions) + 1
            st.session_state.muhasebe_versions.append({
                "version_name": f"Versiyon {versiyon_no}",
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "df": mevcut_df
            })
            st.session_state.muhasebe_versions = st.session_state.muhasebe_versions[-5:]
            st.toast("Versiyon kaydedildi!", icon="✅")

    with b_col3:
        # İndirme butonu stilini uydurmak için placeholder veya doğrudan st.download_button
        excel_data_main = _to_excel_bytes(st.session_state.df_muhasebe)
        st.download_button("📥 Excel Olarak Al", data=excel_data_main, file_name="muhasebe_listesi.xlsx")

    with b_col4:
        if st.button("🔄 Tüm Verileri Sıfırla"):
            del st.session_state.df_muhasebe
            if 'muhasebe_versions' in st.session_state: del st.session_state.muhasebe_versions
            st.rerun()

    st.write("---")

    # --------------------------------------------------
    # KPI KARTLARI
    # --------------------------------------------------
    kpi1, kpi2, kpi3 = st.columns(3)
    
    total_kazanc = st.session_state.df_muhasebe["Acente Toplam Kazanç"].sum()
    total_odenen = st.session_state.df_muhasebe["Acenteye Ödenen Komisyon"].sum()
    total_kalan = st.session_state.df_muhasebe["Kalan Komisyon Tutarı"].sum()

    kpi1.markdown(f"<div class='metric-card'><span style='color:#94A3B8; font-size:12px;'>TOPLAM HAKEDİŞ</span><br><span style='color:#38BDF8; font-size:22px; font-weight:bold;'>₺{total_kazanc:,.2f}</span></div>", unsafe_allow_html=True)
    kpi2.markdown(f"<div class='metric-card'><span style='color:#94A3B8; font-size:12px;'>TOPLAM ÖDENEN</span><br><span style='color:#E2E8F0; font-size:22px; font-weight:bold;'>₺{total_odenen:,.2f}</span></div>", unsafe_allow_html=True)
    kpi3.markdown(f"<div class='metric-card'><span style='color:#94A3B8; font-size:12px;'>KALAN BAKİYE</span><br><span style='color:#22C55E; font-size:22px; font-weight:bold;'>₺{total_kalan:,.2f}</span></div>", unsafe_allow_html=True)

    # --------------------------------------------------
    # VERSİYON GEÇMİŞİ (YATAY KARTLAR)
    # --------------------------------------------------
    if st.session_state.muhasebe_versions:
        st.write("")
        st.markdown("### 📄 Son Kayıtlar")
        for v in reversed(st.session_state.muhasebe_versions):
            col_v1, col_v2 = st.columns([4, 1])
            col_v1.info(f"**{v['version_name']}** - Saat: {v['timestamp']}")
            with col_v2:
                st.download_button("İndir", _to_excel_bytes(v["df"]), file_name=f"{v['version_name']}.xlsx", key=f"dl_{v['version_name']}")
