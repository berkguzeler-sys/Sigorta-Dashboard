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
.kpi-title {
    font-size: 16px;
    color: #374151;
    font-weight: 600;
}
.kpi-value {
    font-size: 30px;
    font-weight: 800;
    color: #111827;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Sigorta Dashboard")

# --- EXCEL ---
excel_url = "https://raw.githubusercontent.com/berkguzeler-sys/Sigorta-Dashboard/main/Acente_Analiz.xlsx"

# --- SIDEBAR ---
st.sidebar.header("📂 Veri Kaynağı")
uploaded_file = st.sidebar.file_uploader("Excel yükle", type=["xlsx"])

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
df = df[df["Tanzim Tarihi"].notna()].copy()
df["Ay"] = df["Tanzim Tarihi"].dt.to_period("M").astype(str)

# --- YENİ KOLONLAR ---
df["Acente Adet"] = (df["Acente Mi?"] == 1).astype(int)
df["Polipedia Adet"] = (df["Acente Mi?"] == 0).astype(int)

# --- FİLTRELER ---
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
    sorted(df_filtre["Poliçe Türü"].dropna().unique())
)

acente = st.sidebar.multiselect(
    "Acente",
    sorted(df_filtre["Dış Acente Adı"].dropna().unique())
)

if poliçe:
    df_filtre = df_filtre[df_filtre["Poliçe Türü"].isin(poliçe)]

if acente:
    df_filtre = df_filtre[df_filtre["Dış Acente Adı"].isin(acente)]

# Filtre sonrası Ay kolonunu yeniden garantiye al
df_filtre["Ay"] = df_filtre["Tanzim Tarihi"].dt.to_period("M").astype(str)

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

col1.markdown(kpi("Toplam Poliçe", f"{toplam_poliçe:,}"), unsafe_allow_html=True)
col2.markdown(kpi("Net Prim", f"{toplam_net_prim:,.0f}"), unsafe_allow_html=True)
col3.markdown(kpi("Acente Adet", f"{toplam_acente_adet:,}"), unsafe_allow_html=True)
col4.markdown(kpi("Polipedia Adet", f"{toplam_polipedia_adet:,}"), unsafe_allow_html=True)
col5.markdown(kpi("Acente Komisyon", f"{toplam_acente_komisyon:,.0f}"), unsafe_allow_html=True)
col6.markdown(kpi("Polipedia Komisyon", f"{toplam_polipedia_komisyon:,.0f}"), unsafe_allow_html=True)

st.divider()

# --- POLİÇE TÜRÜ ANALİZİ ---
st.subheader("📊 Poliçe Türü Analizi")

df_ozet = df_filtre.groupby("Poliçe Türü", dropna=False)["Net Prim"].sum().reset_index()
df_ozet = df_ozet.sort_values(by="Net Prim", ascending=False)

grafik = st.radio("Grafik Tipi", ["Bar", "Pie"], horizontal=True)

if grafik == "Bar":
    fig_policetur = px.bar(df_ozet, x="Poliçe Türü", y="Net Prim")
else:
    fig_policetur = px.pie(df_ozet, names="Poliçe Türü", values="Net Prim")

st.plotly_chart(fig_policetur, use_container_width=True)

st.divider()

# --- GÜNLÜK / AYLIK ANALİZ ---
st.subheader("📈 Günlük ve Aylık Takip")

metric_secim = st.radio(
    "Gösterilecek Metrik",
    ["Net Prim", "Poliçe Adet"],
    horizontal=True
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
        fig_gun = px.line(df_gunluk, x="Tanzim Tarihi", y="Net Prim", markers=True)
    else:
        fig_gun = px.line(df_gunluk, x="Tanzim Tarihi", y="Poliçe No", markers=True)
    st.plotly_chart(fig_gun, use_container_width=True)

with col_g2:
    st.markdown("**Aylık Analiz**")
    if metric_secim == "Net Prim":
        fig_ay = px.bar(df_aylik, x="Ay", y="Net Prim")
    else:
        fig_ay = px.bar(df_aylik, x="Ay", y="Poliçe No")
    st.plotly_chart(fig_ay, use_container_width=True)

st.divider()

# --- ACENTE ANALİZ ---
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

pivot_display = pivot.map(lambda x: f"{x:,.0f}") if not pivot.empty else pivot
st.dataframe(pivot_display, use_container_width=True)

# --- BAREM ---
def barem(x):
    if x <= 250000:
        return "0-250K", 55, 250000 - x
    elif x <= 500000:
        return "250K-500K", 60, 500000 - x
    else:
        return "500K+", 65, 0

df_acente_aylik[["Barem", "Komisyon %", "Bir Üst Bareme Kalan Tutar"]] = (
    df_acente_aylik["Acente Net Prim"].apply(lambda x: pd.Series(barem(x)))
)

# --- KOMİSYONLAR ---
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

# --- BAREM TABLO ---
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

# --- FORMAT ---
df_barem["Acente Net Prim"] = df_barem["Acente Net Prim"].apply(lambda x: f"{x:,.0f}")
df_barem["Asıl Komisyon"] = df_barem["Asıl Komisyon"].apply(lambda x: f"{x:,.0f}")
df_barem["Acente Komisyon Kazancı"] = df_barem["Acente Komisyon Kazancı"].apply(lambda x: f"{x:,.0f}")
df_barem["Bir Üst Bareme Kalan Tutar"] = df_barem["Bir Üst Bareme Kalan Tutar"].apply(lambda x: f"{x:,.0f}")

st.subheader("📊 Barem Analizi")
st.dataframe(df_barem, use_container_width=True)

st.divider()

# --- DETAY ---
st.subheader("📋 Detay Veri")
st.dataframe(
    df_filtre.sort_values(by="Net Prim", ascending=False),
    use_container_width=True
)
# =========================================================
# 🔥 YENİ ANALİZ (MULTI + TÜMÜ + % FORMAT)
# =========================================================

st.subheader("📊 Acente Bazında Aylık Poliçe Türü Oranları")

col1, col2, col3 = st.columns(3)

# --- ACENTE (MULTI + TÜMÜ) ---
acente_list = sorted(df_filtre["Dış Acente Adı"].dropna().unique())
acente_list = ["Tümü"] + acente_list

with col1:
    secili_acente = st.multiselect(
        "Dış Acente",
        acente_list,
        default=["Tümü"]
    )

# --- AY (MULTI + TÜMÜ) ---
ay_list = sorted(df_filtre["Ay"].dropna().unique())
ay_list = ["Tümü"] + ay_list

with col2:
    secili_ay = st.multiselect(
        "Ay",
        ay_list,
        default=["Tümü"]
    )

# --- METRİK ---
with col3:
    metric = st.radio(
        "Metrik",
        ["Net Prim", "Poliçe Adet"],
        horizontal=True
    )

# --- DATA FİLTRE ---
df_temp = df_filtre.copy()

# ACENTE
if "Tümü" not in secili_acente:
    df_temp = df_temp[df_temp["Dış Acente Adı"].isin(secili_acente)]

# AY
if "Tümü" not in secili_ay:
    df_temp = df_temp[df_temp["Ay"].isin(secili_ay)]

if df_temp.empty:
    st.warning("Seçime uygun veri bulunamadı")
    st.stop()

# --- GROUP ---
df_group = df_temp.groupby("Poliçe Türü").agg({
    "Net Prim": "sum",
    "Poliçe No": "count"
}).reset_index()

# --- ORAN ---
if metric == "Net Prim":
    df_group["Oran"] = df_group["Net Prim"] / df_group["Net Prim"].sum()
else:
    df_group["Oran"] = df_group["Poliçe No"] / df_group["Poliçe No"].sum()

# yüzde hesap
df_group["Oran"] = (df_group["Oran"] * 100)

# --- TABLO (% FORMAT) ---
st.markdown("### 📋 Oran Tablosu")

df_group_display = df_group.copy()
df_group_display["Oran (%)"] = df_group_display["Oran"].map(lambda x: f"%{x:.2f}")

st.dataframe(
    df_group_display[["Poliçe Türü", "Oran (%)"]],
    use_container_width=True
)

# --- PIE CHART ---
st.markdown("### 🥧 Dağılım Grafiği")

title_acente = ", ".join(secili_acente)
title_ay = ", ".join(secili_ay)

fig = px.pie(
    df_group,
    names="Poliçe Türü",
    values="Oran",
    title=f"{title_acente} | {title_ay} Dağılım (%)"
)

st.plotly_chart(fig, use_container_width=True)
