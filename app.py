import streamlit as st
import pandas as pd
import plotly.express as px
import time

# --------------------------------------------------
# SAYFA AYARI
# --------------------------------------------------
st.set_page_config(page_title="Polipedia Analiz", layout="wide")


# --------------------------------------------------
# PREMIUM DARK CSS (Renk Paleti & KPI Düzenlemesi)
# --------------------------------------------------
# SADECE CSS BLOĞU DEĞİŞTİ — GERİ KALAN HER ŞEY AYNI

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
tab1, tab2 = st.tabs(["📊 Dashboard", "💰 Muhasebe"])

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
    data = pd.read_excel(source)
    # Kolon isimlerini temizle ve istenen değişiklikleri yap
    data.columns = data.columns.str.strip()
    rename_map = {
        "Asıl Komisyon": "Toplam Komisyon",
        "Dış Acente Adı": "Acente Adı",
        "Poliçe Türü": "Branş"
    }
    data.rename(columns=rename_map, inplace=True)
    return data

try:
    if uploaded_file is not None:
        df = load_data(uploaded_file)
    else:
        df = load_data(excel_url)
except Exception as e:
    st.error("❌ Veri yüklenemedi!")
    st.write(e)
    st.stop()

# --------------------------------------------------
# TEMİZLEME VE HAZIRLIK
# --------------------------------------------------
df["Tanzim Tarihi"] = pd.to_datetime(df["Tanzim Tarihi"], errors="coerce")
df = df[df["Tanzim Tarihi"].notna()].copy()
df["Ay"] = df["Tanzim Tarihi"].dt.to_period("M").astype(str)

# Yardımcı kolonlar
if "Acente Mi?" in df.columns:
    df["Acente Adet"] = (df["Acente Mi?"] == 1).astype(int)
    df["Polipedia Adet"] = (df["Acente Mi?"] == 0).astype(int)
else:
    df["Acente Adet"] = 0
    df["Polipedia Adet"] = 0

# Eksikse güvenli kolon üret
for col in ["Net Prim", "Poliçe No", "Acente Adı", "Branş", "Acente Net Prim", "Toplam Komisyon", "Acente Komisyon Kazancı", "Polipedia Komisyon Kazancı"]:
    if col not in df.columns:
        if col in ["Net Prim", "Acente Net Prim", "Toplam Komisyon", "Acente Komisyon Kazancı", "Polipedia Komisyon Kazancı"]:
            df[col] = 0
        else:
            df[col] = ""

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

    st.subheader("⚠️ Son 1 Aydır Hiç Üretim Yapmamış Acenteler")
    max_tarih = df["Tanzim Tarihi"].max()
    son_1_ay = max_tarih - pd.Timedelta(days=30)
    aktif_acente = df[df["Tanzim Tarihi"] >= son_1_ay]["Acente Adı"].dropna().unique()
    tum_acente = df["Acente Adı"].dropna().unique()
    pasif_acente = sorted(set(tum_acente) - set(aktif_acente))

    if len(pasif_acente) > 0:
        st.dataframe(pd.DataFrame(pasif_acente, columns=["Acente Adı"]), use_container_width=True)
    else:
        st.success("Tüm acenteler son 1 ayda üretim yapmış 🎯")


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
# MUHASEBE TAB
# --------------------------------------------------
with tab2:
    st.subheader("💰 Muhasebe ve Komisyon Düzenleme")

    # 🔥 PREMIUM INFO BOX
    st.markdown("""
    <div style="
        backdrop-filter: blur(10px);
        background: linear-gradient(145deg, rgba(15,23,42,0.7), rgba(30,41,59,0.6));
        padding:12px 16px;
        border-radius:12px;
        border:1px solid rgba(255,255,255,0.08);
        margin-bottom:10px;
        color:#CBD5F5;
    ">
    💡 <b>Komisyon %</b> değiştir → Güncelle. Ödenen komisyonu manuel gir.
    </div>
    """, unsafe_allow_html=True)

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
        st.session_state.df_muhasebe = df_init

    edited_df = st.data_editor(
        st.session_state.df_muhasebe,
        height=500,
        column_config={
            "Acente Adı": st.column_config.TextColumn("Acente", disabled=True),
            "Ay": st.column_config.TextColumn("Ay", disabled=True),
            "Acente Net Prim": st.column_config.NumberColumn("Net Prim", format="₺%,.0f", disabled=True),
            "Toplam Komisyon": st.column_config.NumberColumn("Toplam Komisyon", format="₺%,.0f", disabled=True),
            "Komisyon %": st.column_config.NumberColumn("Komisyon %", min_value=0, max_value=100, format="%d%%"),
            "Acente Toplam Kazanç": st.column_config.NumberColumn("Acente Toplam Kazanç", format="₺%,.2f", disabled=True),
            "Acenteye Ödenen Komisyon": st.column_config.NumberColumn("Acenteye Ödenen Komisyon", format="₺%,.2f"),
            "Güncel Komisyon Farkı": st.column_config.NumberColumn("Komisyon Farkı (puan)", format="%d", disabled=True),
            "Kalan Komisyon Tutarı": st.column_config.NumberColumn("Kalan Komisyon Tutarı", format="₺%,.2f", disabled=True),
            "İlk Kazanç": None,
            "İlk Komisyon %": None,
        },
        hide_index=True,
        use_container_width=True,
        key="muhasebe_editor_v5"
    )

    col_btn1, col_btn2 = st.columns([1, 4])

    # 🔥 PREMIUM BUTON CSS
    st.markdown("""
    <style>
    div.stButton > button {
        background: linear-gradient(90deg, #38BDF8, #818CF8);
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(56,189,248,0.4);
    }
    </style>
    """, unsafe_allow_html=True)

    with col_btn1:
        if st.button("🚀 Hesaplamaları Güncelle", type="primary"):
            edited_df["Acente Toplam Kazanç"] = (edited_df["Toplam Komisyon"] * edited_df["Komisyon %"]) / 100
            edited_df["Güncel Komisyon Farkı"] = edited_df["Komisyon %"] - edited_df["İlk Komisyon %"]
            edited_df["Kalan Komisyon Tutarı"] = edited_df["Acente Toplam Kazanç"] - edited_df["Acenteye Ödenen Komisyon"].fillna(0)
            st.session_state.df_muhasebe = edited_df
            st.rerun()

    with col_btn2:
        if st.button("🔄 Verileri Sıfırla"):
            if 'df_muhasebe' in st.session_state:
                del st.session_state.df_muhasebe
                st.rerun()

    st.divider()

    # 🔥 PREMIUM KPI CARDS
    t1, t2, t3 = st.columns(3)

    toplam_kazanc = st.session_state.df_muhasebe["Acente Toplam Kazanç"].sum()
    toplam_kalan = st.session_state.df_muhasebe["Kalan Komisyon Tutarı"].sum()

    t1.markdown(f"""
    <div class="metric-card">
        <div style="font-size:13px; color:#94A3B8;">Acente Toplam Kazanç</div>
        <div style="font-size:28px; font-weight:800;
            background: linear-gradient(90deg,#38BDF8,#818CF8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;">
            ₺{toplam_kazanc:,.2f}
        </div>
    </div>
    """, unsafe_allow_html=True)

    t3.markdown(f"""
    <div class="metric-card">
        <div style="font-size:13px; color:#94A3B8;">Kalan Komisyon</div>
        <div style="font-size:28px; font-weight:800;
            background: linear-gradient(90deg,#22C55E,#4ADE80);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;">
            ₺{toplam_kalan:,.2f}
        </div>
    </div>
    """, unsafe_allow_html=True)
