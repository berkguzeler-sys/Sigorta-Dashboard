import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# SAYFA AYARI
# --------------------------------------------------
st.set_page_config(page_title="Polipedia Analiz", layout="wide")

# --------------------------------------------------
# PREMIUM DARK CSS (Renk Paleti & KPI Düzenlemesi)
# --------------------------------------------------
st.markdown("""
<style>
    /* Ana Uygulama Arka Planı */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }

    /* Üst Boşluk Ayarı */
    .main > div {
        padding-top: 1rem;
    }

    /* Sidebar Rengi */
    section[data-testid="stSidebar"] {
        background-color: #1E293B !important;
    }

    /* KPI Kartları (Simetri ve Sığma Ayarı Yapıldı) */
    .kpi-card {
        background: rgba(30, 41, 59, 0.7);
        padding: 15px 10px; /* İç boşluklar optimize edildi */
        border-radius: 16px;
        box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.4);
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.3s ease;
        
        /* Tüm kutuların boyunu eşitlemek için */
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 110px; /* Sabit yükseklik */
        overflow: hidden; /* Taşmayı önle */
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        border-color: #38BDF8;
    }

    .kpi-title {
        font-size: 13px; /* Hafif küçültüldü */
        color: #94A3B8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
        white-space: nowrap; /* Başlığın sığmasını sağla */
    }

    .kpi-value {
        font-size: 24px; /* TL işaretiyle sığması için optimize edildi */
        font-weight: 800;
        color: #38BDF8; /* Parlak Mavi Metin */
        white-space: nowrap; /* Değerin tek satırda kalmasını sağla */
        overflow: hidden;
        text-overflow: ellipsis; /* Çok uzunsa üç nokta koy (taşmayı önler) */
    }

    /* Tab Başlıkları */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94A3B8;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #38BDF8 !important;
        border-bottom-color: #38BDF8 !important;
    }

    /* Metin Renkleri */
    h1, h2, h3, .stSubheader, p {
        color: #F8FAFC !important;
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
import time

excel_url = f"https://raw.githubusercontent.com/berkguzeler-sys/Sigorta-Dashboard/main/Acente_Analiz.xlsx?{int(time.time())}"

st.sidebar.header("📂 Veri Kaynağı")
if st.sidebar.button("🔄 Veriyi Yenile"):
    st.cache_data.clear()
uploaded_file = st.sidebar.file_uploader("Excel yükle", type=["xlsx"])

@st.cache_data(ttl=60)
def load_data(source):
    return pd.read_excel(source)

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
# TEMİZLEME
# --------------------------------------------------
df.columns = df.columns.str.strip()

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
for col in ["Net Prim", "Poliçe No", "Dış Acente Adı", "Poliçe Türü", "Acente Net Prim", "Asıl Komisyon", "Acente Komisyon Kazancı", "Polipedia Komisyon Kazancı"]:
    if col not in df.columns:
        if col in ["Net Prim", "Acente Net Prim", "Asıl Komisyon", "Acente Komisyon Kazancı", "Polipedia Komisyon Kazancı"]:
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

poliçe = st.sidebar.multiselect(
    "Poliçe Türü",
    sorted(df_filtre["Poliçe Türü"].dropna().astype(str).unique())
)

acente = st.sidebar.multiselect(
    "Acente",
    sorted(df_filtre["Dış Acente Adı"].dropna().astype(str).unique())
)

if poliçe:
    df_filtre = df_filtre[df_filtre["Poliçe Türü"].isin(poliçe)]

if acente:
    df_filtre = df_filtre[df_filtre["Dış Acente Adı"].isin(acente)]

df_filtre["Ay"] = df_filtre["Tanzim Tarihi"].dt.to_period("M").astype(str)

# --------------------------------------------------
# PREMIUM RENK PALETİ VE RENK HARİTASI
# --------------------------------------------------
premium_colors = ["#38BDF8", "#818CF8", "#34D399", "#FB923C", "#F472B6", "#A78BFA", "#F87171", "#2DD4BF", "#E879F9", "#94A3B8"]

# Poliçe Türleri için Sabit Renk Haritası
unique_types = sorted(df["Poliçe Türü"].dropna().astype(str).unique())
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

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    def kpi(title, val):
        return f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{val}</div>
        </div>
        """

    col1.markdown(kpi("Toplam Poliçe", f"{toplam_poliçe:,}"), unsafe_allow_html=True)
    col2.markdown(kpi("Net Prim", f"₺{toplam_net_prim:,.0f}"), unsafe_allow_html=True)
    col3.markdown(kpi("Acente Adet", f"{toplam_acente_adet:,}"), unsafe_allow_html=True)
    col4.markdown(kpi("Polipedia Adet", f"{toplam_polipedia_adet:,}"), unsafe_allow_html=True)
    col5.markdown(kpi("Acente Komisyon", f"₺{toplam_acente_komisyon:,.0f}"), unsafe_allow_html=True)
    col6.markdown(kpi("Polipedia Komisyon", f"₺{toplam_polipedia_komisyon:,.0f}"), unsafe_allow_html=True)

    st.divider()

    # --------------------------------------------------
    # POLİÇE TÜRÜ ANALİZİ
    # --------------------------------------------------
    st.subheader("📊 Poliçe Türü Analizi")

    col_pt1, col_pt2 = st.columns([1, 1])

    with col_pt1:
        policetur_metric = st.radio(
            "Gösterilecek Değer",
            ["Net Prim", "Poliçe Adet"],
            horizontal=True,
            key="police_turu_metric"
        )

    with col_pt2:
        grafik = st.radio(
            "Grafik Tipi",
            ["Bar", "Pie"],
            horizontal=True,
            key="police_turu_grafik"
        )

    df_ozet = df_filtre.groupby("Poliçe Türü", dropna=False).agg({
        "Net Prim": "sum",
        "Poliçe No": "count"
    }).reset_index()

    df_ozet.rename(columns={"Poliçe No": "Poliçe Adet"}, inplace=True)

    if policetur_metric == "Net Prim":
        value_col = "Net Prim"
        title_text = "Poliçe Türüne Göre Net Prim Dağılımı"
        text_template = "₺%{y:,.0f}" if grafik == "Bar" else "%{percent}"
    else:
        value_col = "Poliçe Adet"
        title_text = "Poliçe Türüne Göre Poliçe Adet Dağılımı"
        text_template = "%{y}" if grafik == "Bar" else "%{percent}"

    df_ozet = df_ozet.sort_values(by=value_col, ascending=False)

    if grafik == "Bar":
        fig_policetur = px.bar(
            df_ozet,
            x="Poliçe Türü",
            y=value_col,
            color="Poliçe Türü",
            color_discrete_map=color_map,
            text=value_col
        )
        fig_policetur.update_traces(
            texttemplate=text_template,
            textposition="outside",
            marker_line_width=0
        )
        fig_policetur.update_layout(
            title=title_text,
            template="plotly_dark",
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Poliçe Türü",
            yaxis_title=f"{policetur_metric} (₺)" if policetur_metric == "Net Prim" else policetur_metric,
            xaxis=dict(tickangle=-20),
            margin=dict(l=20, r=20, t=60, b=20)
        )
    else:
        fig_policetur = px.pie(
            df_ozet,
            names="Poliçe Türü",
            values=value_col,
            color="Poliçe Türü",
            color_discrete_map=color_map,
            hole=0.45
        )
        fig_policetur.update_traces(
            textinfo="percent+label",
            pull=[0.03 if i == 0 else 0 for i in range(len(df_ozet))]
        )
        fig_policetur.update_layout(
            title=title_text,
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=60, b=20)
        )

    st.plotly_chart(fig_policetur, use_container_width=True)

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
            fig_gun = px.line(df_gunluk, x="Tanzim Tarihi", y="Net Prim", markers=True, color_discrete_sequence=["#38BDF8"])
            fig_gun.update_layout(yaxis_title="Net Prim (₺)")
        else:
            fig_gun = px.line(df_gunluk, x="Tanzim Tarihi", y="Poliçe No", markers=True, color_discrete_sequence=["#38BDF8"])
            fig_gun.update_layout(yaxis_title="Poliçe Adet")

        fig_gun.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_gun, use_container_width=True)

    with col_g2:
        st.markdown("**Aylık Analiz**")
        if metric_secim == "Net Prim":
            fig_ay = px.bar(df_aylik, x="Ay", y="Net Prim", color_discrete_sequence=["#818CF8"], text="Net Prim")
            fig_ay.update_traces(texttemplate='₺%{text:,.0f}', textposition='outside')
            fig_ay.update_layout(yaxis_title="Net Prim (₺)")
        else:
            fig_ay = px.bar(df_aylik, x="Ay", y="Poliçe No", color_discrete_sequence=["#818CF8"], text="Poliçe No")
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
        df_filtre["Dış Acente Adı"].fillna("").str.upper() != "POLIPEDIA"
    ].copy()

    df_acente_aylik = df_acente.groupby(
        ["Dış Acente Adı", "Ay"],
        dropna=False
    )["Acente Net Prim"].sum().reset_index()

    pivot = df_acente_aylik.pivot(
        index="Dış Acente Adı",
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

    df_komisyon = df_acente.groupby(
        ["Dış Acente Adı", "Ay"],
        dropna=False
    ).agg({
        "Acente Komisyon Kazancı": "sum",
        "Asıl Komisyon": "sum"
    }).reset_index()

    df_acente_aylik = df_acente_aylik.merge(
        df_komisyon,
        on=["Dış Acente Adı", "Ay"],
        how="left"
    )

    df_acente_aylik["Asıl Komisyon"] = df_acente_aylik["Asıl Komisyon"].fillna(0)
    df_acente_aylik["Acente Komisyon Kazancı"] = df_acente_aylik["Acente Komisyon Kazancı"].fillna(0)

    df_barem = df_acente_aylik[
        [
            "Dış Acente Adı",
            "Ay",
            "Acente Net Prim",
            "Asıl Komisyon",
            "Acente Komisyon Kazancı",
            "Komisyon %",
            "Barem",
            "Bir Üst Bareme Kalan Tutar"
        ]
    ].copy()

    if not df_barem.empty:
        df_barem["Acente Net Prim"] = df_barem["Acente Net Prim"].apply(lambda x: f"₺{x:,.0f}")
        df_barem["Asıl Komisyon"] = df_barem["Asıl Komisyon"].apply(lambda x: f"₺{x:,.0f}")
        df_barem["Acente Komisyon Kazancı"] = df_barem["Acente Komisyon Kazancı"].apply(lambda x: f"₺{x:,.0f}")
        df_barem["Bir Üst Bareme Kalan Tutar"] = df_barem["Bir Üst Bareme Kalan Tutar"].apply(lambda x: f"₺{x:,.0f}")
        df_barem["Komisyon %"] = df_barem["Komisyon %"].apply(lambda x: f"%{x}")

    st.subheader("📊 Barem Analizi")
    st.dataframe(df_barem, use_container_width=True)

    st.divider()

    # --------------------------------------------------
    # ACENTE BAZINDA AYLIK POLİÇE TÜRÜ ORANLARI (GÜNCELLENDİ)
    # --------------------------------------------------
    st.subheader("📊 Acente Bazında Aylık Poliçe Türü Oranları")

    col1, col2, col3 = st.columns(3)

    acente_list = sorted(df_filtre["Dış Acente Adı"].dropna().astype(str).unique())
    acente_list = ["Tümü"] + acente_list

    with col1:
        secili_acente = st.multiselect(
            "Dış Acente",
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
            horizontal=True
        )

    df_temp = df_filtre.copy()

    if "Tümü" not in secili_acente:
        df_temp = df_temp[df_temp["Dış Acente Adı"].isin(secili_acente)]

    if "Tümü" not in secili_ay:
        df_temp = df_temp[df_temp["Ay"].isin(secili_ay)]

    if df_temp.empty:
        st.warning("Seçime uygun veri bulunamadı")
    else:
        df_group = df_temp.groupby("Poliçe Türü").agg({
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

        title_acente = ", ".join(secili_acente)
        title_ay = ", ".join(secili_ay)

        col_table, col_chart = st.columns([1, 1.8])

        with col_table:
            st.markdown("### 📋 Oran Tablosu")
            st.dataframe(
                df_group_display[["Poliçe Türü", "Oran (%)"]],
                use_container_width=True,
                height=350
            )

        with col_chart:
            st.markdown("### 🥧 Dağılım Grafiği")
            # Sabit renkler ve sığma ayarları uygulandı
            fig = px.pie(
                df_group,
                names="Poliçe Türü",
                values="Oran",
                title=f"{title_acente} | {title_ay} Dağılım (%)",
                color="Poliçe Türü",
                color_discrete_map=color_map,
                hole=0.40,
                height=450
            )
            fig.update_traces(
                textinfo="percent+label",
                textposition="inside" # Grafik küçülmesini engellemek için yazıları içeri alır
            )
            fig.update_layout(
                template="plotly_dark", 
                paper_bgcolor="rgba(0,0,0,0)", 
                margin=dict(l=0, r=0, t=50, b=0), # Margin daraltıldı
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)




            # --- YENİ ANALİZ 1: ÜST BAREME EN YAKIN 5 ACENTE ---
# ==================================================

st.subheader("🚀 Bir Üst Bareme En Yakın 5 Acente")

# SON AYI BUL
son_ay = df_acente_aylik["Ay"].max()

# SADECE SON AY VERİSİ
df_yakin = df_acente_aylik[
    df_acente_aylik["Ay"] == son_ay
].copy()

# ÜST BAREME GEÇME İHTİMALİ OLANLAR
df_yakin = df_yakin[df_yakin["Bir Üst Bareme Kalan Tutar"] > 0]

# EN YAKIN 5 ACENTE
df_yakin = df_yakin.sort_values("Bir Üst Bareme Kalan Tutar").head(5)

if not df_yakin.empty:
    df_yakin_display = df_yakin.copy()
    df_yakin_display["Acente Net Prim"] = df_yakin_display["Acente Net Prim"].apply(lambda x: f"₺{x:,.0f}")
    df_yakin_display["Bir Üst Bareme Kalan Tutar"] = df_yakin_display["Bir Üst Bareme Kalan Tutar"].apply(lambda x: f"₺{x:,.0f}")
    
    st.dataframe(
        df_yakin_display[
            ["Dış Acente Adı", "Ay", "Acente Net Prim", "Barem", "Bir Üst Bareme Kalan Tutar"]
        ],
        use_container_width=True
    )
else:
    st.info("Uygun veri bulunamadı")

st.divider()

# ==================================================
# --- YENİ ANALİZ 2: SON 1 AYDIR ÜRETİM YOK ---
# ==================================================

st.subheader("⚠️ Son 1 Aydır Hiç Üretim Yapmamış Acenteler")

# Son tarih
max_tarih = df["Tanzim Tarihi"].max()

# 30 gün geri
son_1_ay = max_tarih - pd.Timedelta(days=30)

# Son 1 ayda üretim yapanlar
aktif_acente = df[
    df["Tanzim Tarihi"] >= son_1_ay
]["Dış Acente Adı"].dropna().unique()

# Tüm acenteler
tum_acente = df["Dış Acente Adı"].dropna().unique()

# Üretim yapmayanlar
pasif_acente = sorted(set(tum_acente) - set(aktif_acente))

if len(pasif_acente) > 0:
    df_pasif = pd.DataFrame(pasif_acente, columns=["Dış Acente Adı"])
    st.dataframe(df_pasif, use_container_width=True)
else:
    st.success("Tüm acenteler son 1 ayda üretim yapmış 🎯")

# --------------------------------------------------
# MUHASEBE TAB (KOMİSYON FARKI ANALİZLİ)
# --------------------------------------------------
with tab2:
    st.subheader("💰 Muhasebe ve Komisyon Düzenleme")

    # 1. Veri Hazırlığı ve İlk Değerlerin Sabitlenmesi
    if 'df_muhasebe' not in st.session_state:
        df_init = df_acente_aylik[[
            "Dış Acente Adı", "Ay", "Acente Net Prim", 
            "Asıl Komisyon", "Komisyon %", "Acente Komisyon Kazancı"
        ]].copy()
        
        df_init["İlk Kazanç"] = df_init["Acente Komisyon Kazancı"].fillna(0)
        df_init["Güncel Komisyon Farkı"] = 0.0
        
        st.session_state.df_muhasebe = df_init

    st.info("💡 **Komisyon %** değerini değiştirip **'Hesaplamaları Güncelle'** butonuna bastığınızda kazanç ve fark kolonları güncellenir.")

    # 2. Düzenlenebilir Tablo
    edited_df = st.data_editor(
        st.session_state.df_muhasebe,
        column_config={
            "Dış Acente Adı": st.column_config.TextColumn("Acente", disabled=True),
            "Ay": st.column_config.TextColumn("Ay", disabled=True),
            "Acente Net Prim": st.column_config.NumberColumn("Net Prim", format="₺%,.0f", disabled=True),
            "Asıl Komisyon": st.column_config.NumberColumn("Asıl Komisyon", format="₺%,.0f", disabled=True),
            "Komisyon %": st.column_config.NumberColumn(
                "Komisyon %", 
                min_value=0, max_value=100, format="%d%%"
            ),
            "Acente Komisyon Kazancı": st.column_config.NumberColumn(
                "Güncel Kazanç", format="₺%,.2f", disabled=True
            ),
            "Güncel Komisyon Farkı": st.column_config.NumberColumn(
                "Komisyon Farkı (+/-)", 
                format="₺%,.2f", 
                disabled=True,
                help="Yeni Kazanç - Eski Kazanç"
            ),
            "İlk Kazanç": None, 
        },
        hide_index=True,
        use_container_width=True,
        key="muhasebe_editor_v4"
    )

    # 3. Güncelleme Butonu ve Matematiksel Hesaplama
    col_btn1, col_btn2 = st.columns([1, 4])
    
    with col_btn1:
        if st.button("🚀 Hesaplamaları Güncelle", type="primary"):
            edited_df["Acente Komisyon Kazancı"] = (edited_df["Asıl Komisyon"] * edited_df["Komisyon %"]) / 100
            edited_df["Güncel Komisyon Farkı"] = edited_df["Acente Komisyon Kazancı"] - edited_df["İlk Kazanç"]
            st.session_state.df_muhasebe = edited_df
            st.success("✅ Kazançlar ve farklar hesaplandı!")
            st.rerun()

    with col_btn2:
        if st.button("🔄 Verileri Sıfırla"):
            if 'df_muhasebe' in st.session_state:
                del st.session_state.df_muhasebe
                st.rerun()

    # 4. Özet Bilgiler (Alt Toplamlar)
    st.divider()
    t1, t2 = st.columns(2)
    
    toplam_kazanc = st.session_state.df_muhasebe["Acente Komisyon Kazancı"].sum()
    toplam_fark = st.session_state.df_muhasebe["Güncel Komisyon Farkı"].sum()
    
    t1.metric(label="📊 Güncel Toplam Kazanç", value=f"₺{toplam_kazanc:,.2f}")
    t2.metric(
        label="📉 Toplam Fark Etkisi", 
        value=f"₺{toplam_fark:,.2f}",
        delta=f"{toplam_fark:,.2f}", 
        delta_color="normal"
    )
