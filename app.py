import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================
st.set_page_config(
    page_title="Dashboard Minero",
    page_icon="⛏️",
    layout="wide"
)

# =========================================================
# RUTA BASE
# =========================================================
BASE_DIR = Path(__file__).resolve().parent

# =========================================================
# FUNCIÓN PARA CARGAR CSV
# =========================================================
@st.cache_data
def cargar_csv(nombre_archivo: str) -> pd.DataFrame:
    """
    Carga archivos CSV probando codificaciones comunes.
    """
    ruta = BASE_DIR / nombre_archivo

    if not ruta.exists():
        st.error(f"No se encontró el archivo: {nombre_archivo}")
        return pd.DataFrame()

    codificaciones = ["utf-8", "latin-1", "cp1252"]

    for enc in codificaciones:
        try:
            return pd.read_csv(ruta, encoding=enc)
        except UnicodeDecodeError:
            continue
        except Exception as e:
            st.error(f"Error al leer {nombre_archivo}: {e}")
            return pd.DataFrame()

    st.error(f"No se pudo leer {nombre_archivo} con las codificaciones probadas.")
    return pd.DataFrame()


# =========================================================
# CARGA DE DATOS
# =========================================================
dim_procesos = cargar_csv("dim_procesos.csv")
preparacion = cargar_csv("preparacion_minerales.csv")
extraccion = cargar_csv("extraccion_metales.csv")
refinacion = cargar_csv("refinacion_metales.csv")

# =========================================================
# LIMPIEZA BÁSICA
# =========================================================
def convertir_fecha(df: pd.DataFrame, columna: str = "fecha") -> pd.DataFrame:
    """
    Convierte una columna de fecha a datetime si existe.
    """
    if columna in df.columns:
        df[columna] = pd.to_datetime(df[columna], errors="coerce")
    return df


preparacion = convertir_fecha(preparacion, "fecha")
extraccion = convertir_fecha(extraccion, "fecha")
refinacion = convertir_fecha(refinacion, "fecha")

# =========================================================
# TÍTULO PRINCIPAL
# =========================================================
st.title("⛏️ Dashboard de Procesos Mineros")
st.markdown(
    "Visualización interactiva de la información operativa de "
    "**preparación, extracción y refinación**."
)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("⚙️ Navegación")

seccion = st.sidebar.radio(
    "Selecciona una sección:",
    [
        "Inicio",
        "Ver tablas",
        "Relaciones",
        "Control de calidad",
        "Consultas analíticas",
        "Dashboard"
    ]
)

# =========================================================
# SECCIÓN: INICIO
# =========================================================
if seccion == "Inicio":
    st.subheader("📌 Resumen general")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Procesos", len(dim_procesos))
    c2.metric("Preparación", len(preparacion))
    c3.metric("Extracción", len(extraccion))
    c4.metric("Refinación", len(refinacion))

    st.markdown("---")
    st.markdown("### 📁 Archivos cargados")
    st.write("- dim_procesos.csv")
    st.write("- preparacion_minerales.csv")
    st.write("- extraccion_metales.csv")
    st.write("- refinacion_metales.csv")

    st.markdown("---")
    st.markdown("### 🧠 Descripción")
    st.write(
        "La aplicación permite explorar la base de datos minera, revisar relaciones "
        "entre tablas, identificar anomalías y analizar indicadores operativos mediante "
        "un dashboard interactivo."
    )

# =========================================================
# SECCIÓN: VER TABLAS
# =========================================================
elif seccion == "Ver tablas":
    st.subheader("📋 Visualización de tablas")

    opcion_tabla = st.selectbox(
        "Selecciona una tabla:",
        [
            "dim_procesos",
            "preparacion_minerales",
            "extraccion_metales",
            "refinacion_metales"
        ]
    )

    limite = st.slider("Número de filas a mostrar", 5, 100, 20)

    if opcion_tabla == "dim_procesos":
        df_tabla = dim_procesos.copy()
    elif opcion_tabla == "preparacion_minerales":
        df_tabla = preparacion.copy()
    elif opcion_tabla == "extraccion_metales":
        df_tabla = extraccion.copy()
    else:
        df_tabla = refinacion.copy()

    st.dataframe(df_tabla.head(limite), use_container_width=True)

    st.download_button(
        label="⬇️ Descargar tabla",
        data=df_tabla.to_csv(index=False).encode("utf-8"),
        file_name=f"{opcion_tabla}.csv",
        mime="text/csv"
    )

# =========================================================
# SECCIÓN: RELACIONES
# =========================================================
elif seccion == "Relaciones":
    st.subheader("🔗 Verificación de relaciones")

    prep_rel = preparacion.merge(dim_procesos, on="id_proceso", how="left", indicator=True)
    prep_huerfanos = prep_rel[prep_rel["_merge"] == "left_only"]

    ext_rel = extraccion.merge(dim_procesos, on="id_proceso", how="left", indicator=True)
    ext_huerfanos = ext_rel[ext_rel["_merge"] == "left_only"]

    ref_huerfanos = pd.DataFrame()
    if "id_proceso" in refinacion.columns:
        ref_rel = refinacion.merge(dim_procesos, on="id_proceso", how="left", indicator=True)
        ref_huerfanos = ref_rel[ref_rel["_merge"] == "left_only"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Huérfanos preparación", len(prep_huerfanos))
    c2.metric("Huérfanos extracción", len(ext_huerfanos))
    c3.metric("Huérfanos refinación", len(ref_huerfanos))

    st.markdown("---")

    if len(prep_huerfanos) == 0 and len(ext_huerfanos) == 0 and len(ref_huerfanos) == 0:
        st.success("No se encontraron registros huérfanos. Las relaciones son consistentes.")
    else:
        st.warning("Se detectaron registros sin correspondencia en la tabla dimensión.")

        if len(prep_huerfanos) > 0:
            st.markdown("### Registros huérfanos en preparación")
            st.dataframe(prep_huerfanos, use_container_width=True)

        if len(ext_huerfanos) > 0:
            st.markdown("### Registros huérfanos en extracción")
            st.dataframe(ext_huerfanos, use_container_width=True)

        if len(ref_huerfanos) > 0:
            st.markdown("### Registros huérfanos en refinación")
            st.dataframe(ref_huerfanos, use_container_width=True)

# =========================================================
# SECCIÓN: CONTROL DE CALIDAD
# =========================================================
elif seccion == "Control de calidad":
    st.subheader("🧪 Control de calidad de datos")

    prep_anomalias = preparacion[
        (preparacion["porcentaje_recuperacion"] > 100) |
        (preparacion["porcentaje_recuperacion"] < 0) |
        (preparacion["tiempo_operacion_horas"] < 0)
    ]

    ext_anomalias = extraccion[
        (extraccion["porcentaje_extraccion"] > 100) |
        (extraccion["porcentaje_extraccion"] < 0) |
        (extraccion["temperatura_procesos_celcius"] < 0)
    ]

    c1, c2 = st.columns(2)
    c1.metric("Anomalías preparación", len(prep_anomalias))
    c2.metric("Anomalías extracción", len(ext_anomalias))

    st.markdown("---")

    if len(prep_anomalias) == 0:
        st.success("No se encontraron anomalías en preparación.")
    else:
        st.warning("Se encontraron registros atípicos en preparación.")
        st.dataframe(prep_anomalias, use_container_width=True)

    if len(ext_anomalias) == 0:
        st.success("No se encontraron anomalías en extracción.")
    else:
        st.warning("Se encontraron registros atípicos en extracción.")
        st.dataframe(ext_anomalias, use_container_width=True)

# =========================================================
# SECCIÓN: CONSULTAS ANALÍTICAS
# =========================================================
elif seccion == "Consultas analíticas":
    st.subheader("📊 Consultas analíticas")

    consulta = st.selectbox(
        "Selecciona una consulta:",
        [
            "Toneladas por proceso",
            "Costo promedio por proceso",
            "Tiempo promedio de operación",
            "Mejora de pureza en refinación",
            "Consumo energético por tonelada"
        ]
    )

    resultado = pd.DataFrame()

    if consulta == "Toneladas por proceso":
        resultado = (
            preparacion.merge(dim_procesos, on="id_proceso", how="left")
            .groupby("proceso", as_index=False)["toneladas_procesadas"]
            .sum()
            .rename(columns={"toneladas_procesadas": "total_toneladas"})
            .sort_values("total_toneladas", ascending=False)
        )

    elif consulta == "Costo promedio por proceso":
        resultado = (
            preparacion.merge(dim_procesos, on="id_proceso", how="left")
            .groupby("proceso", as_index=False)["costo_tonelada_usd"]
            .mean()
            .rename(columns={"costo_tonelada_usd": "costo_promedio"})
            .sort_values("costo_promedio", ascending=False)
        )

    elif consulta == "Tiempo promedio de operación":
        resultado = (
            preparacion.merge(dim_procesos, on="id_proceso", how="left")
            .groupby("proceso", as_index=False)["tiempo_operacion_horas"]
            .mean()
            .rename(columns={"tiempo_operacion_horas": "tiempo_promedio"})
            .sort_values("tiempo_promedio", ascending=False)
        )

    elif consulta == "Mejora de pureza en refinación":
        resultado = refinacion.copy()
        resultado["mejora_pureza"] = resultado["pureza_final_pct"] - resultado["pureza_inicial_pct"]
        resultado = resultado[
            ["proceso", "pureza_inicial_pct", "pureza_final_pct", "mejora_pureza"]
        ].sort_values("mejora_pureza", ascending=False)

    elif consulta == "Consumo energético por tonelada":
        tmp = preparacion.merge(dim_procesos, on="id_proceso", how="left")
        resultado = (
            tmp.groupby("proceso", as_index=False)
            .agg({
                "consumo_energia_kwh": "sum",
                "toneladas_procesadas": "sum"
            })
        )
        resultado["kwh_por_tonelada"] = resultado["consumo_energia_kwh"] / resultado["toneladas_procesadas"]
        resultado = resultado[["proceso", "kwh_por_tonelada"]].sort_values(
            "kwh_por_tonelada", ascending=False
        )

    st.dataframe(resultado, use_container_width=True)

    st.download_button(
        label="⬇️ Descargar resultado",
        data=resultado.to_csv(index=False).encode("utf-8"),
        file_name="resultado_consulta.csv",
        mime="text/csv"
    )

# =========================================================
# SECCIÓN: DASHBOARD
# =========================================================
elif seccion == "Dashboard":
    st.subheader("📈 Dashboard interactivo")

    # -----------------------------------------------------
    # FILTROS
    # -----------------------------------------------------
    st.markdown("### 🎛️ Filtros")

    procesos_disponibles = sorted(dim_procesos["proceso"].dropna().unique().tolist())
    procesos_seleccionados = st.multiselect(
        "Filtrar por proceso",
        options=procesos_disponibles,
        default=procesos_disponibles
    )

    # Unimos preparación con dimensión para filtrar por nombre
    prep_full = preparacion.merge(dim_procesos, on="id_proceso", how="left")
    ext_full = extraccion.merge(dim_procesos, on="id_proceso", how="left")

    if procesos_seleccionados:
        prep_filtrado = prep_full[prep_full["proceso"].isin(procesos_seleccionados)].copy()
        ext_filtrado = ext_full[ext_full["proceso"].isin(procesos_seleccionados)].copy()
    else:
        prep_filtrado = prep_full.copy()
        ext_filtrado = ext_full.copy()

    # -----------------------------------------------------
    # KPIs
    # -----------------------------------------------------
    st.markdown("### 📌 Indicadores clave")

    total_ton = prep_filtrado["toneladas_procesadas"].sum()
    costo_prom = prep_filtrado["costo_tonelada_usd"].mean()
    recuperacion_prom = prep_filtrado["porcentaje_recuperacion"].mean()
    extraccion_prom = ext_filtrado["porcentaje_extraccion"].mean()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Toneladas procesadas", f"{total_ton:,.2f}")
    k2.metric("Costo promedio USD/t", f"{costo_prom:,.2f}")
    k3.metric("Recuperación promedio %", f"{recuperacion_prom:,.2f}")
    k4.metric("Extracción promedio %", f"{extraccion_prom:,.2f}")

    st.markdown("---")

    # -----------------------------------------------------
    # GRÁFICO 1: TONELADAS POR PROCESO
    # -----------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Toneladas por proceso")
        graf1 = (
            prep_filtrado.groupby("proceso", as_index=False)["toneladas_procesadas"]
            .sum()
            .sort_values("toneladas_procesadas", ascending=False)
        )

        fig1, ax1 = plt.subplots(figsize=(8, 4))
        ax1.bar(graf1["proceso"], graf1["toneladas_procesadas"])
        ax1.set_xlabel("Proceso")
        ax1.set_ylabel("Toneladas")
        ax1.set_title("Toneladas procesadas")
        plt.xticks(rotation=45)
        st.pyplot(fig1)

    # -----------------------------------------------------
    # GRÁFICO 2: COSTO PROMEDIO POR PROCESO
    # -----------------------------------------------------
    with col2:
        st.markdown("### Costo promedio por proceso")
        graf2 = (
            prep_filtrado.groupby("proceso", as_index=False)["costo_tonelada_usd"]
            .mean()
            .sort_values("costo_tonelada_usd", ascending=False)
        )

        fig2, ax2 = plt.subplots(figsize=(8, 4))
        ax2.bar(graf2["proceso"], graf2["costo_tonelada_usd"])
        ax2.set_xlabel("Proceso")
        ax2.set_ylabel("USD/t")
        ax2.set_title("Costo promedio")
        plt.xticks(rotation=45)
        st.pyplot(fig2)

    st.markdown("---")

    # -----------------------------------------------------
    # GRÁFICO 3: RECUPERACIÓN VS ENERGÍA
    # -----------------------------------------------------
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### Recuperación vs consumo de energía")
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        ax3.scatter(
            prep_filtrado["consumo_energia_kwh"],
            prep_filtrado["porcentaje_recuperacion"]
        )
        ax3.set_xlabel("Consumo energía (kWh)")
        ax3.set_ylabel("Recuperación (%)")
        ax3.set_title("Recuperación vs energía")
        st.pyplot(fig3)

    # -----------------------------------------------------
    # GRÁFICO 4: EXTRACCIÓN VS TEMPERATURA
    # -----------------------------------------------------
    with col4:
        st.markdown("### Extracción vs temperatura")
        fig4, ax4 = plt.subplots(figsize=(8, 4))
        ax4.scatter(
            ext_filtrado["temperatura_procesos_celcius"],
            ext_filtrado["porcentaje_extraccion"]
        )
        ax4.set_xlabel("Temperatura (°C)")
        ax4.set_ylabel("Extracción (%)")
        ax4.set_title("Extracción vs temperatura")
        st.pyplot(fig4)

    st.markdown("---")

    # -----------------------------------------------------
    # TABLAS RESUMEN
    # -----------------------------------------------------
    st.markdown("### 📋 Resumen por proceso")

    resumen = (
        prep_filtrado.groupby("proceso", as_index=False)
        .agg({
            "toneladas_procesadas": "sum",
            "costo_tonelada_usd": "mean",
            "porcentaje_recuperacion": "mean",
            "consumo_energia_kwh": "sum"
        })
        .rename(columns={
            "toneladas_procesadas": "total_toneladas",
            "costo_tonelada_usd": "costo_promedio",
            "porcentaje_recuperacion": "recuperacion_promedio",
            "consumo_energia_kwh": "energia_total"
        })
    )

    st.dataframe(resumen, use_container_width=True)

    st.download_button(
        label="⬇️ Descargar resumen del dashboard",
        data=resumen.to_csv(index=False).encode("utf-8"),
        file_name="dashboard_resumen.csv",
        mime="text/csv"
    )