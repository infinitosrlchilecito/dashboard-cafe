import pandas as pd
import streamlit as st
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Consumo de Café",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos CSS personalizados para asegurar el tema oscuro y colores llamativos
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .sidebar .sidebar-content {
        background-color: #161b22;
    }
    div.stMetric {
        background-color: #1f242d;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border: 1px solid #30363d;
    }
    div.stMetric label {
        color: #8b949e !important;
        font-size: 14px !important;
    }
    div.stMetric [data-testid="stMetricValue"] {
        color: #00ffcc !important;
        font-size: 26px !important;
        font-weight: bold;
    }
    h1, h2, h3 {
        color: #58a6ff;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Carga de datos desde el archivo Excel
EXCEL_FILE = "CONSUMO SEMANALES DE CAFÉ.xlsx"


@st.cache_data
def load_data():
    # Cargar solapa de división para análisis de categorías
    df_div = pd.read_excel(EXCEL_FILE, sheet_name="DIVISIÓN")
    df_cafe = pd.read_excel(EXCEL_FILE, sheet_name="CAFÉ")
    return df_div, df_cafe


df_div, df_cafe = load_data()

# TÍTULO DEL DASHBOARD
st.title("☕ DASHBOARD INTERACTIVO - CONSUMO SEMANAL DE CAFÉ")
st.markdown(
    "Panel de control profesional con actualización automática de métricas y gráficos."
)
st.markdown("---")

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.header("🎛️ Panel de Control & Filtros")
st.sidebar.markdown(
    "Modifica los valores para actualizar automáticamente el dashboard."
)

# Filtro interactivo de categoría
categoria_filtro = st.sidebar.selectbox(
    "Seleccionar Categoría de Análisis",
    [
        "Todas las Categorías",
        "Promos / Desayunos",
        "Café en Jarra / Dobles",
        "Cafés y Especiales",
    ],
)

# Simulación de control deslizante interactivo para ajustar factor de escala o demanda
factor_ajuste = st.sidebar.slider(
    "Ajuste Dinámico de Demanda (%)",
    min_value=50,
    max_value=150,
    value=100,
    step=5,
)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Nota:** Los gráficos reaccionan dinámicamente a cualquier cambio en los selectores o controles deslizantes."
)

# --- PROCESAMIENTO DE DATOS PARA VISUALIZACIÓN ---
# Limpiamos y preparamos datos de la solapa DIVISIÓN
promos_data = df_div[["PROMOS", "CANTIDAD", "KILOS"]].dropna()
promos_data["Tipo"] = "Promos / Desayunos"
promos_data.columns = ["Ítem", "Cantidad", "Kilos", "Tipo"]

jarra_data = df_div[["CAFÉ", "CANTIDAD.1", "KILOS.1"]].dropna()
jarra_data["Tipo"] = "Café en Jarra / Dobles"
jarra_data.columns = ["Ítem", "Cantidad", "Kilos", "Tipo"]

especiales_data = df_div[["CAFÉ.1", "CANTIDAD.2", "KILOS.2"]].dropna()
especiales_data["Tipo"] = "Cafés y Especiales"
especiales_data.columns = ["Ítem", "Cantidad", "Kilos", "Tipo"]

# Unificar dataset
df_global = pd.concat([promos_data, jarra_data, especiales_data], ignore_index=True)

# Aplicar factor de ajuste dinámico del slider
df_global["Cantidad"] = df_global["Cantidad"] * (factor_ajuste / 100.0)
df_global["Kilos"] = df_global["Kilos"] * (factor_ajuste / 100.0)

# Filtrar según la selección del usuario
if categoria_filtro != "Todas las Categorías":
    df_global = df_global[df_global["Tipo"] == categoria_filtro]

# --- TARJETAS KPI (MÉTRICAS PRINCIPALES) ---
total_cafes = int(df_global["Cantidad"].sum())
total_kilos = round(df_global["Kilos"].sum(), 2)
gramos_totales = int(total_kilos * 1000)
promedio_item = (
    round(df_global["Cantidad"].mean(), 1) if not df_global.empty else 0
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="☕ Total Unidades Vendidas", value=f"{total_cafes:,}")
with col2:
    st.metric(label="⚖️ Kilos Totales Consumidos", value=f"{total_kilos} kg")
with col3:
    st.metric(label="📦 Gramos Totales", value=f"{gramos_totales:,} g")
with col4:
    st.metric(label="📊 Promedio por Ítem", value=f"{promedio_item}")

st.markdown("---")

# --- SECCIÓN DE GRÁFICOS INTERACTIVOS (PLOTLY CON TEMA OSCURO) ---
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("📈 Top Ítems de Mayor Consumo")
    if not df_global.empty:
        df_top = df_global.sort_values(by="Cantidad", ascending=True).tail(10)
        fig_bar = px.bar(
            df_top,
            x="Cantidad",
            y="Ítem",
            orientation="h",
            color="Cantidad",
            color_continuous_scale=["#ff007f", "#ff9900", "#00ffcc"],
            text="Cantidad",
        )
        fig_bar.update_layout(
            plot_bgcolor="#0e1117",
            paper_bgcolor="#0e1117",
            font_color="#ffffff",
            xaxis=dict(showgrid=True, gridcolor="#30363d"),
            yaxis=dict(showgrid=False),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar en esta categoría.")

with col_g2:
    st.subheader("🍩 Distribución por Categoría (Kilos)")
    if not df_global.empty:
        df_pie = (
            df_global.groupby("Tipo")["Kilos"].sum().reset_index()
        )
        fig_pie = px.pie(
            df_pie,
            names="Tipo",
            values="Kilos",
            hole=0.4,
            color_discrete_sequence=["#00ffcc", "#ff007f", "#9d00ff", "#ff9900"],
        )
        fig_pie.update_layout(
            plot_bgcolor="#0e1117",
            paper_bgcolor="#0e1117",
            font_color="#ffffff",
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar en esta categoría.")

# --- SECCIÓN INFERIOR: TENDENCIA Y DETALLE ---
st.subheader("📋 Detalle Analítico de Registros")
st.dataframe(
    df_global.style.format({"Cantidad": "{:.1f}", "Kilos": "{:.3f}"}),
    use_container_width=True,
    height=250,
)