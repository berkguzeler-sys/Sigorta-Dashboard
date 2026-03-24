import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sigorta Dashboard", layout="wide")

# --- CSS ---
st.markdown("""
<style>
.kpi-card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 3px 8px rgba(0,0,0,0.12);
    text-align: center;
}
.kpi-title {font-size: 16px; color: #374151; font-weight: 600;}
.kpi-value {font-size: 30px; font-weight: 800; color: #111827;}
</style>
""", unsafe_allow_html=True)

st.title("📊 Sigorta Dashboard")

# 🔥 BURAYA KENDİ EXCEL RAW LINKİNİ KOY
excel_url = "https://raw.githubusercontent.com/berkguzeler-sys/Sigorta-Dashboard/main/Acente_Analiz.xlsx"

# --- SIDEBAR ---
st.sidebar.header("📂 Veri Kaynağı")
uploaded_file = st.sidebar.file_uploader("Excel yükle (opsiyonel)", type=["xlsx"])

# --- DATA LOAD ---
@st.cache_data
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

# --- TEMİZLEME ---
df.columns = df.columns.str.strip()

# --- TARİH ---
df["Tanzim Tarihi"] = pd.to_datetime(df["Tanzim Tarihi"], errors="coerce")
df["Ay"] = df["Tanzim Tarihi"].dt.to_period("M").astype(str)

# --- YENİ KOLONLAR ---
df["Acente Adet"] = (df["Acente Mi?"] == 1).astype(int)
df["Polipedia Adet"] = (df["Acente Mi?"] == 0).astype(int)

# --- FİLTRELER ---
st.sidebar.header("🔎 Filtreler")

poliçe = st.sidebar.multiselect("Poliçe Türü", df["Poliçe Türü"].dropna().unique())
acente = st.sidebar.multiselect("Acente", df["Dış Acente Adı"].dropna().unique())

df_filtre = df.copy()

if poliçe:
    df_filtre = df_filtre[df_filtre["Poliçe Türü"].isin(poliçe)]
if acente:
    df_filtre = df_filtre[df_filtre["Dış Acente Adı"].isin(acente)]

# --- KPI ---
toplam_poliçe = df_filtre["Poliçe No"].count()
toplam_net_prim = df_filtre["Net Prim"].sum()
toplam_acente_adet = df_filtre["Acente Adet"].sum()
toplam_polipedia_adet = df_filtre["Polipedia Adet"].sum()
toplam_acente_komisyon = df_filtre["Acente Komisyon Kazancı"].sum()
toplam_polipedia_komisyon = df_filtre["Polipedia Komisyon Kazancı"].sum()

col1, col2, col3, col4, col5, col6 = st.columns(6)

def kpi(title, val):
    return f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{val}</div>
    </div>
    """

col1.markdown(kpi("Toplam Poliçe", f"{toplam_poliçe:,}"), True)
col2.markdown(kpi("Net Prim", f"{toplam_net_prim:,.0f}"), True)
col3.markdown(kpi("Acente Adet", f"{toplam_acente_adet:,}"), True)
col4.markdown(kpi("Polipedia Adet", f"{toplam_polipedia_adet:,}"), True)
col5.markdown(kpi("Acente Komisyon", f"{toplam_acente_komisyon:,.0f}"), True)
col6.markdown(kpi("Polipedia Komisyon", f"{toplam_polipedia_komisyon:,.0f}"), True)

st.divider()

# --- POLİÇE ANALİZ ---
st.subheader("📊 Poliçe Türü Analizi")

df_ozet = df_filtre.groupby("Poliçe Türü")["Net Prim"].sum().reset_index()
df_ozet = df_ozet.sort_values(by="Net Prim", ascending=False)

grafik = st.radio("Grafik Tipi", ["Bar", "Pie"], horizontal=True)

if grafik == "Bar":
    fig = px.bar(df_ozet, x="Poliçe Türü", y="Net Prim")
else:
    fig = px.pie(df_ozet, names="Poliçe Türü", values="Net Prim")

st.plotly_chart(fig, use_container_width=True)

# --- ACENTE ANALİZ ---
st.subheader("📊 Aylık Acente Net Prim (Polipedia Hariç)")

df_acente = df_filtre[df_filtre["Dış Acente Adı"].str.upper() != "POLIPEDIA"]

df_acente_aylik = df_acente.groupby(
    ["Dış Acente Adı", "Ay"]
)["Acente Net Prim"].sum().reset_index()

pivot = df_acente_aylik.pivot(
    index="Dış Acente Adı",
    columns="Ay",
    values="Acente Net Prim"
).fillna(0)

pivot_display = pivot.applymap(lambda x: f"{x:,.0f}")
st.dataframe(pivot_display, use_container_width=True)

# --- BAREM ---
def barem(x):
    if x <= 250000:
        return "0-250K", 55, 250000 - x
    elif x <= 500000:
        return "250K-500K", 60, 500000 - x
    else:
        return "500K+", 65, 0

df_acente_aylik[["Barem", "Komisyon %", "Kalan"]] = (
    df_acente_aylik["Acente Net Prim"]
    .apply(lambda x: pd.Series(barem(x)))
)

df_barem = df_acente_aylik.copy()
df_barem["Acente Net Prim"] = df_barem["Acente Net Prim"].apply(lambda x: f"{x:,.0f}")
df_barem["Kalan"] = df_barem["Kalan"].apply(lambda x: f"{x:,.0f}")

st.subheader("📊 Barem Analizi")
st.dataframe(df_barem, use_container_width=True)

# --- EN YAKIN 5 ---
df_yakin = df_acente_aylik[
    (df_acente_aylik["Kalan"] > 0) &
    (df_acente_aylik["Kalan"] <= 50000)
].sort_values("Kalan").head(5)

st.subheader("🔥 Üst Bareme En Yakın 5 Acente")

if not df_yakin.empty:
    df_yakin["Acente Net Prim"] = df_yakin["Acente Net Prim"].apply(lambda x: f"{x:,.0f}")
    df_yakin["Kalan"] = df_yakin["Kalan"].apply(lambda x: f"{x:,.0f}")
    st.success("Bu acenteler üst bareme çok yakın 🚀")
    st.dataframe(df_yakin, use_container_width=True)
else:
    st.info("Yakın acente yok")

st.divider()

# --- DETAY ---
st.subheader("📋 Detay Veri")
st.dataframe(df_filtre.sort_values(by="Net Prim", ascending=False), use_container_width=True)
