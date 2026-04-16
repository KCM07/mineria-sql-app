import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# =========================================================
# CONFIGURACIÓN GENERAL DE LA APP
# =========================================================
st.set_page_config(
    page_title="Minería SQL App",
    page_icon="⛏️",
    layout="wide"
)

# =========================================================
# RUTA BASE DEL PROYECTO
# =========================================================
BASE_DIR = Path(__file__).resolve().parent

# =========================================================
# FUNCIÓN PARA CARGAR CSV
# =========================================================

@st.cache_data
def cargar_csv(nombre_archivo: str) -> pd.DataFrame:
    """
    Carga un CSV probando varias codificaciones comunes.
    """
    ruta = BASE_DIR / nombre_archivo

    if not ruta.exists():
        st.error(f"No se encontró el archivo: {nombre_archivo}")
        return pd.DataFrame()

    codificaciones = ["utf-8", "latin-1", "cp1252"]

    for enc in codificaciones:
        try:
            df = pd.read_csv(ruta, encoding=enc)
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            st.error(f"Error al leer {nombre_archivo}: {e}")
            return pd.DataFrame()

    st.error(f"No se pudo leer {nombre_archivo} con las codificaciones probadas.")
    return pd.DataFrame()

# =========================================================
# CARGA DE TABLAS
# =========================================================
dim_procesos = cargar_csv("dim_procesos.csv")
preparacion = cargar_csv("preparacion_minerales.csv")
extraccion = cargar_csv("extraccion_metales.csv")
refinacion = cargar_csv("refinacion_metales.csv")

# =========================================================
# LIMPIEZA Y AJUSTES BÁSICOS
# =========================================================
def convertir_fecha(df: pd.DataFrame, columna: str = "fecha") -> pd.DataFrame:
    """
    Convierte la columna fecha a tipo datetime si existe.
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
st.title("⛏️ Gestión de Bases de Datos en Minería")
st.markdown(
    "Aplicación interactiva para visualizar, consultar y analizar "
    "los procesos mineros de **preparación, extracción y refinación**."
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
        "Dashboard",
        "SQL simulado"
    ]
)

# =========================================================
# SECCIÓN: INICIO
# =========================================================
if seccion == "Inicio":
    st.subheader("📌 Resumen del proyecto")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Procesos en dimensión", len(dim_procesos))
    col2.metric("Registros preparación", len(preparacion))
    col3.metric("Registros extracción", len(extraccion))
    col4.metric("Registros refinación", len(refinacion))

    st.markdown("---")
    st.markdown("### 📁 Archivos cargados")
    st.write("- dim_procesos.csv")
    st.write("- preparacion_minerales.csv")
    st.write("- extraccion_metales.csv")
    st.write("- refinacion_metales.csv")

    st.markdown("---")
    st.markdown("### 🧠 Modelo de datos")
    st.write(
        "La tabla **dim_procesos** funciona como dimensión central, "
        "mientras que las tablas **preparacion_minerales**, "
        "**extraccion_metales** y **refinacion_metales** almacenan la "
        "información operativa de cada etapa."
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

    # Botón para descargar la tabla seleccionada
    st.download_button(
        label="⬇️ Descargar tabla en CSV",
        data=df_tabla.to_csv(index=False).encode("utf-8"),
        file_name=f"{opcion_tabla}.csv",
        mime="text/csv"
    )

# =========================================================
# SECCIÓN: RELACIONES
# =========================================================
elif seccion == "Relaciones":
    st.subheader("🔗 Verificación de relaciones")

    # Verificamos registros huérfanos en preparación
    prep_rel = preparacion.merge(
        dim_procesos,
        on="id_proceso",
        how="left",
        indicator=True
    )
    prep_huerfanos = prep_rel[prep_rel["_merge"] == "left_only"]

    # Verificamos registros huérfanos en extracción
    ext_rel = extraccion.merge(
        dim_procesos,
        on="id_proceso",
        how="left",
        indicator=True
    )
    ext_huerfanos = ext_rel[ext_rel["_merge"] == "left_only"]

    # Verificamos registros huérfanos en refinación
    if "id_proceso" in refinacion.columns:
        ref_rel = refinacion.merge(
            dim_procesos,
            on="id_proceso",
            how="left",
            indicator=True
        )
        ref_huerfanos = ref_rel[ref_rel["_merge"] == "left_only"]
    else:
        ref_huerfanos = pd.DataFrame()

    col1, col2, col3 = st.columns(3)
    col1.metric("Huérfanos en preparación", len(prep_huerfanos))
    col2.metric("Huérfanos en extracción", len(ext_huerfanos))
    col3.metric("Huérfanos en refinación", len(ref_huerfanos))

    st.markdown("---")

    if len(prep_huerfanos) == 0 and len(ext_huerfanos) == 0 and len(ref_huerfanos) == 0:
        st.success("No se encontraron registros huérfanos. Las relaciones son consistentes.")
    else:
        st.warning("Se encontraron registros sin correspondencia en la tabla dimensión.")

        if len(prep_huerfanos) > 0:
            st.markdown("### Preparación sin correspondencia")
            st.dataframe(prep_huerfanos, use_container_width=True)

        if len(ext_huerfanos) > 0:
            st.markdown("### Extracción sin correspondencia")
            st.dataframe(ext_huerfanos, use_container_width=True)

        if len(ref_huerfanos) > 0:
            st.markdown("### Refinación sin correspondencia")
            st.dataframe(ref_huerfanos, use_container_width=True)

# =========================================================
# SECCIÓN: CONTROL DE CALIDAD
# =========================================================
elif seccion == "Control de calidad":
    st.subheader("🧪 Control de calidad de datos")

    # Reglas de control para preparación
    prep_anomalias = preparacion[
        (preparacion["porcentaje_recuperacion"] > 100) |
        (preparacion["porcentaje_recuperacion"] < 0) |
        (preparacion["tiempo_operacion_horas"] < 0)
    ]

    # Reglas de control para extracción
    ext_anomalias = extraccion[
        (extraccion["porcentaje_extraccion"] > 100) |
        (extraccion["porcentaje_extraccion"] < 0) |
        (extraccion["temperatura_procesos_celcius"] < 0)
    ]

    col1, col2 = st.columns(2)
    col1.metric("Anomalías en preparación", len(prep_anomalias))
    col2.metric("Anomalías en extracción", len(ext_anomalias))

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
            "1. Total de toneladas por proceso",
            "2. Costo promedio por proceso",
            "3. Tiempo promedio de operación",
            "4. Recuperación vs energía",
            "5. Extracción vs temperatura",
            "6. Mejora de pureza en refinación",
            "7. Registros sobre el promedio",
            "8. Reporte operativo con JOIN",
            "9. Consumo energético por tonelada"
        ]
    )

    resultado = pd.DataFrame()

    # -----------------------------------------------------
    # Consulta 1
    # -----------------------------------------------------
    if consulta == "1. Total de toneladas por proceso":
        resultado = (
            preparacion.merge(dim_procesos, on="id_proceso", how="left")
            .groupby("proceso", as_index=False)["toneladas_procesadas"]
            .sum()
            .rename(columns={"toneladas_procesadas": "total_toneladas"})
            .sort_values("total_toneladas", ascending=False)
        )

    # -----------------------------------------------------
    # Consulta 2
    # -----------------------------------------------------
    elif consulta == "2. Costo promedio por proceso":
        resultado = (
            preparacion.merge(dim_procesos, on="id_proceso", how="left")
            .groupby("proceso", as_index=False)["costo_tonelada_usd"]
            .mean()
            .rename(columns={"costo_tonelada_usd": "costo_promedio"})
            .sort_values("costo_promedio", ascending=False)
        )

    # -----------------------------------------------------
    # Consulta 3
    # -----------------------------------------------------
    elif consulta == "3. Tiempo promedio de operación":
        resultado = (
            preparacion.merge(dim_procesos, on="id_proceso", how="left")
            .groupby("proceso", as_index=False)["tiempo_operacion_horas"]
            .mean()
            .rename(columns={"tiempo_operacion_horas": "tiempo_promedio"})
            .sort_values("tiempo_promedio", ascending=False)
        )

    # -----------------------------------------------------
    # Consulta 4
    # -----------------------------------------------------
    elif consulta == "4. Recuperación vs energía":
        resultado = preparacion[
            ["fecha", "id_proceso", "porcentaje_recuperacion", "consumo_energia_kwh"]
        ].sort_values("porcentaje_recuperacion", ascending=False)

    # -----------------------------------------------------
    # Consulta 5
    # -----------------------------------------------------
    elif consulta == "5. Extracción vs temperatura":
        resultado = extraccion[
            ["fecha", "id_proceso", "porcentaje_extraccion", "temperatura_procesos_celcius"]
        ].sort_values("porcentaje_extraccion", ascending=False)

    # -----------------------------------------------------
    # Consulta 6
    # -----------------------------------------------------
    elif consulta == "6. Mejora de pureza en refinación":
        resultado = refinacion.copy()
        resultado["mejora_pureza"] = (
            resultado["pureza_final_pct"] - resultado["pureza_inicial_pct"]
        )
        resultado = resultado[
            ["proceso", "pureza_inicial_pct", "pureza_final_pct", "mejora_pureza"]
        ].sort_values("mejora_pureza", ascending=False)

    # -----------------------------------------------------
    # Consulta 7
    # -----------------------------------------------------
    elif consulta == "7. Registros sobre el promedio":
        promedio = preparacion["toneladas_procesadas"].mean()
        resultado = preparacion[preparacion["toneladas_procesadas"] > promedio]

    # -----------------------------------------------------
    # Consulta 8
    # -----------------------------------------------------
    elif consulta == "8. Reporte operativo con JOIN":
        resultado = (
            preparacion.merge(dim_procesos, on="id_proceso", how="left")
            [["proceso", "tipo_proceso", "fecha", "toneladas_procesadas", "costo_tonelada_usd"]]
            .sort_values("fecha")
        )

    # -----------------------------------------------------
    # Consulta 9
    # -----------------------------------------------------
    elif consulta == "9. Consumo energético por tonelada":
        tmp = preparacion.merge(dim_procesos, on="id_proceso", how="left")
        resultado = (
            tmp.groupby("proceso", as_index=False)
            .agg({
                "consumo_energia_kwh": "sum",
                "toneladas_procesadas": "sum"
            })
        )
        resultado["kwh_por_tonelada"] = (
            resultado["consumo_energia_kwh"] / resultado["toneladas_procesadas"]
        )
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
    st.subheader("📈 Dashboard de indicadores")

    # KPI 1: total toneladas preparación
    total_ton_prep = preparacion["toneladas_procesadas"].sum()

    # KPI 2: costo promedio preparación
    costo_prom_prep = preparacion["costo_tonelada_usd"].mean()

    # KPI 3: extracción promedio
    extraccion_prom = extraccion["porcentaje_extraccion"].mean()

    # KPI 4: mejora promedio en refinación
    mejora_prom_ref = (refinacion["pureza_final_pct"] - refinacion["pureza_inicial_pct"]).mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Toneladas preparación", f"{total_ton_prep:,.2f}")
    c2.metric("Costo promedio preparación", f"{costo_prom_prep:,.2f}")
    c3.metric("Extracción promedio (%)", f"{extraccion_prom:,.2f}")
    c4.metric("Mejora pureza promedio", f"{mejora_prom_ref:,.2f}")

    st.markdown("---")

    # Gráfico 1: toneladas por proceso
    st.markdown("### Toneladas procesadas por proceso")

    graf1 = (
        preparacion.merge(dim_procesos, on="id_proceso", how="left")
        .groupby("proceso", as_index=False)["toneladas_procesadas"]
        .sum()
        .sort_values("toneladas_procesadas", ascending=False)
    )

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.bar(graf1["proceso"], graf1["toneladas_procesadas"])
    ax1.set_xlabel("Proceso")
    ax1.set_ylabel("Toneladas")
    ax1.set_title("Toneladas procesadas por proceso")
    plt.xticks(rotation=45)
    st.pyplot(fig1)

    # Gráfico 2: costo promedio por proceso
    st.markdown("### Costo promedio por proceso")

    graf2 = (
        preparacion.merge(dim_procesos, on="id_proceso", how="left")
        .groupby("proceso", as_index=False)["costo_tonelada_usd"]
        .mean()
        .sort_values("costo_tonelada_usd", ascending=False)
    )

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.bar(graf2["proceso"], graf2["costo_tonelada_usd"])
    ax2.set_xlabel("Proceso")
    ax2.set_ylabel("Costo promedio")
    ax2.set_title("Costo promedio por proceso")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

# =========================================================..
# SECCIÓN: SQL SIMULADO
# =========================================================..
elif seccion == "SQL simulado":
    st.subheader("🧠 SQL simulado")

    st.info(
        "Esta sección no ejecuta SQL real. "
        "Sirve para mostrar consultas escritas y sus resultados equivalentes usando pandas."
    )

    consulta_sql = st.text_area(
        "Escribe una consulta SQL de ejemplo:",
        value="SELECT * FROM dim_procesos;"
    )

    st.code(consulta_sql, language="sql")

    if st.button("Mostrar tabla ejemplo"):
        st.dataframe(dim_procesos, use_container_width=True)