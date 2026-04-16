import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================
st.set_page_config(
    page_title="🗃️CODEaUNI - MINERIA -  SQL - APP",
    page_icon="🐬",
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
st.title("💻 GESTIÓN DE BASES DE DATOS EN MINERÍA - MySQL🐬")
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
    st.markdown("### 📝 Descripción")
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
    st.subheader("🔗 Modelo de datos y verificación de relaciones")

    st.markdown("""
    En esta sección se muestra el modelo relacional de la base de datos y la validación
    de integridad referencial entre la tabla dimensión `dim_procesos` y las tablas operativas
    de preparación, extracción y refinación.
    """)

    # -----------------------------------------------------
    # IMAGEN DEL MODELO RELACIONAL
    # -----------------------------------------------------
    # Asegúrate de guardar la imagen con este nombre
    # en la misma carpeta donde está app.py
    ruta_imagen = BASE_DIR /"relaciones.png"

    if ruta_imagen.exists():
        st.image(
            str(ruta_imagen),
            caption="Modelo relacional de la base de datos mineria_operaciones",
            use_container_width=True
        )
    else:
        st.info("No se encontró la imagen modelo_relacional.png en la carpeta del proyecto.")

    st.markdown("---")

    # -----------------------------------------------------
    # VERIFICACIÓN DE REGISTROS HUÉRFANOS
    # -----------------------------------------------------
    prep_rel = preparacion.merge(dim_procesos, on="id_proceso", how="left", indicator=True)
    prep_huerfanos = prep_rel[prep_rel["_merge"] == "left_only"]

    ext_rel = extraccion.merge(dim_procesos, on="id_proceso", how="left", indicator=True)
    ext_huerfanos = ext_rel[ext_rel["_merge"] == "left_only"]

    ref_huerfanos = pd.DataFrame()
    if "id_proceso" in refinacion.columns:
        ref_rel = refinacion.merge(dim_procesos, on="id_proceso", how="left", indicator=True)
        ref_huerfanos = ref_rel[ref_rel["_merge"] == "left_only"]

    # -----------------------------------------------------
    # MÉTRICAS
    # -----------------------------------------------------
    c1, c2, c3 = st.columns(3)
    c1.metric("Huérfanos preparación", len(prep_huerfanos))
    c2.metric("Huérfanos extracción", len(ext_huerfanos))
    c3.metric("Huérfanos refinación", len(ref_huerfanos))

    st.markdown("---")

    # -----------------------------------------------------
    # INTERPRETACIÓN
    # -----------------------------------------------------
    if len(prep_huerfanos) == 0 and len(ext_huerfanos) == 0 and len(ref_huerfanos) == 0:
        st.success("No se encontraron registros huérfanos. Las relaciones entre tablas son consistentes.")
        st.markdown("""
        **Interpretación:**  
        Todos los registros de las tablas operativas tienen correspondencia en la tabla
        `dim_procesos`, por lo que la integridad referencial del modelo es correcta.
        """)
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
    st.subheader("📈 Dashboard ejecutivo de procesos mineros")

    # -----------------------------------------------------
    # PREPARACIÓN DE DATOS
    # -----------------------------------------------------
    prep_full = preparacion.merge(dim_procesos, on="id_proceso", how="left")
    ext_full = extraccion.merge(dim_procesos, on="id_proceso", how="left")

    # Si refinación tiene id_proceso, también la vinculamos
    if "id_proceso" in refinacion.columns:
        ref_full = refinacion.merge(dim_procesos, on="id_proceso", how="left")
    else:
        ref_full = refinacion.copy()

    # -----------------------------------------------------
    # FILTROS
    # -----------------------------------------------------
    st.markdown("### 🎛️ Filtros")

    procesos_disponibles = sorted(dim_procesos["proceso"].dropna().unique().tolist())
    procesos_sel = st.multiselect(
        "Selecciona procesos",
        options=procesos_disponibles,
        default=procesos_disponibles
    )

    if procesos_sel:
        prep_filtrado = prep_full[prep_full["proceso"].isin(procesos_sel)].copy()
        ext_filtrado = ext_full[ext_full["proceso"].isin(procesos_sel)].copy()

        if "proceso" in ref_full.columns:
            ref_filtrado = ref_full[ref_full["proceso"].isin(procesos_sel)].copy()
        else:
            ref_filtrado = ref_full.copy()
    else:
        prep_filtrado = prep_full.copy()
        ext_filtrado = ext_full.copy()
        ref_filtrado = ref_full.copy()

    # -----------------------------------------------------
    # KPIs PRINCIPALES
    # -----------------------------------------------------
    st.markdown("### 📌 Indicadores clave")

    total_ton = prep_filtrado["toneladas_procesadas"].sum() if not prep_filtrado.empty else 0
    costo_prom = prep_filtrado["costo_tonelada_usd"].mean() if not prep_filtrado.empty else 0
    rec_prom = prep_filtrado["porcentaje_recuperacion"].mean() if not prep_filtrado.empty else 0
    ext_prom = ext_filtrado["porcentaje_extraccion"].mean() if not ext_filtrado.empty else 0

    if not ref_filtrado.empty and "pureza_final_pct" in ref_filtrado.columns and "pureza_inicial_pct" in ref_filtrado.columns:
        mejora_pureza_prom = (ref_filtrado["pureza_final_pct"] - ref_filtrado["pureza_inicial_pct"]).mean()
    else:
        mejora_pureza_prom = 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Toneladas totales", f"{total_ton:,.2f}")
    c2.metric("Costo promedio USD/t", f"{costo_prom:,.2f}")
    c3.metric("Recuperación promedio %", f"{rec_prom:,.2f}")
    c4.metric("Extracción promedio %", f"{ext_prom:,.2f}")
    c5.metric("Mejora pureza promedio", f"{mejora_pureza_prom:,.2f}")

    st.markdown("---")

    # -----------------------------------------------------
    # ESTADÍSTICAS DESCRIPTIVAS
    # -----------------------------------------------------
    st.markdown("### 📊 Estadísticas descriptivas")

    col_est_1, col_est_2 = st.columns(2)

    with col_est_1:
        st.markdown("#### Preparación")
        if not prep_filtrado.empty:
            stats_prep = prep_filtrado[
                [
                    "toneladas_procesadas",
                    "porcentaje_recuperacion",
                    "tiempo_operacion_horas",
                    "consumo_energia_kwh",
                    "costo_tonelada_usd"
                ]
            ].describe().T
            st.dataframe(stats_prep, use_container_width=True)
        else:
            st.info("No hay datos de preparación para mostrar.")

    with col_est_2:
        st.markdown("#### Extracción")
        if not ext_filtrado.empty:
            stats_ext = ext_filtrado[
                [
                    "toneladas_procesadas",
                    "porcentaje_extraccion",
                    "temperatura_procesos_celcius",
                    "consumo_reactivos_kg",
                    "costo_operacion_usd"
                ]
            ].describe().T
            st.dataframe(stats_ext, use_container_width=True)
        else:
            st.info("No hay datos de extracción para mostrar.")

    st.markdown("---")

    # -----------------------------------------------------
    # GRÁFICOS PRINCIPALES
    # -----------------------------------------------------
    st.markdown("### 📈 Gráficos principales")

    # Gráfico 1: toneladas por proceso
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown("#### Toneladas procesadas por proceso")
        if not prep_filtrado.empty:
            g1 = (
                prep_filtrado.groupby("proceso", as_index=False)["toneladas_procesadas"]
                .sum()
                .sort_values("toneladas_procesadas", ascending=False)
            )
            fig1, ax1 = plt.subplots(figsize=(8, 4))
            ax1.bar(g1["proceso"], g1["toneladas_procesadas"])
            ax1.set_xlabel("Proceso")
            ax1.set_ylabel("Toneladas")
            ax1.set_title("Toneladas por proceso")
            plt.xticks(rotation=45)
            st.pyplot(fig1)
        else:
            st.info("No hay datos para graficar.")

    # Gráfico 2: costo promedio por proceso
    with col_g2:
        st.markdown("#### Costo promedio por proceso")
        if not prep_filtrado.empty:
            g2 = (
                prep_filtrado.groupby("proceso", as_index=False)["costo_tonelada_usd"]
                .mean()
                .sort_values("costo_tonelada_usd", ascending=False)
            )
            fig2, ax2 = plt.subplots(figsize=(8, 4))
            ax2.bar(g2["proceso"], g2["costo_tonelada_usd"])
            ax2.set_xlabel("Proceso")
            ax2.set_ylabel("USD/t")
            ax2.set_title("Costo promedio")
            plt.xticks(rotation=45)
            st.pyplot(fig2)
        else:
            st.info("No hay datos para graficar.")

    # Gráfico 3: recuperación vs energía
    col_g3, col_g4 = st.columns(2)

    with col_g3:
        st.markdown("#### Recuperación vs consumo de energía")
        if not prep_filtrado.empty:
            fig3, ax3 = plt.subplots(figsize=(8, 4))
            ax3.scatter(
                prep_filtrado["consumo_energia_kwh"],
                prep_filtrado["porcentaje_recuperacion"]
            )
            ax3.set_xlabel("Consumo energía (kWh)")
            ax3.set_ylabel("Recuperación (%)")
            ax3.set_title("Recuperación vs energía")
            st.pyplot(fig3)
        else:
            st.info("No hay datos para graficar.")

    # Gráfico 4: extracción vs temperatura
    with col_g4:
        st.markdown("#### Extracción vs temperatura")
        if not ext_filtrado.empty:
            fig4, ax4 = plt.subplots(figsize=(8, 4))
            ax4.scatter(
                ext_filtrado["temperatura_procesos_celcius"],
                ext_filtrado["porcentaje_extraccion"]
            )
            ax4.set_xlabel("Temperatura (°C)")
            ax4.set_ylabel("Extracción (%)")
            ax4.set_title("Extracción vs temperatura")
            st.pyplot(fig4)
        else:
            st.info("No hay datos para graficar.")

    # Gráfico 5: mejora de pureza
    col_g5, col_g6 = st.columns(2)

    with col_g5:
        st.markdown("#### Mejora de pureza en refinación")
        if not ref_filtrado.empty and "pureza_final_pct" in ref_filtrado.columns and "pureza_inicial_pct" in ref_filtrado.columns:
            g5 = ref_filtrado.copy()
            g5["mejora_pureza"] = g5["pureza_final_pct"] - g5["pureza_inicial_pct"]
            g5 = g5[["proceso", "mejora_pureza"]].sort_values("mejora_pureza", ascending=False)

            fig5, ax5 = plt.subplots(figsize=(8, 4))
            ax5.bar(g5["proceso"], g5["mejora_pureza"])
            ax5.set_xlabel("Proceso")
            ax5.set_ylabel("Mejora de pureza")
            ax5.set_title("Mejora de pureza por proceso")
            plt.xticks(rotation=45)
            st.pyplot(fig5)
        else:
            st.info("No hay datos de refinación para graficar.")

    # Gráfico 6: evolución temporal
    with col_g6:
        st.markdown("#### Evolución temporal de toneladas")
        if not prep_filtrado.empty and "fecha" in prep_filtrado.columns:
            g6 = (
                prep_filtrado.groupby("fecha", as_index=False)["toneladas_procesadas"]
                .sum()
                .sort_values("fecha")
            )
            fig6, ax6 = plt.subplots(figsize=(8, 4))
            ax6.plot(g6["fecha"], g6["toneladas_procesadas"], marker="o")
            ax6.set_xlabel("Fecha")
            ax6.set_ylabel("Toneladas")
            ax6.set_title("Toneladas procesadas en el tiempo")
            plt.xticks(rotation=45)
            st.pyplot(fig6)
        else:
            st.info("No hay datos temporales para graficar.")

    st.markdown("---")

    # -----------------------------------------------------
    # CONSULTAS / RESÚMENES MÁS IMPORTANTES
    # -----------------------------------------------------
    st.markdown("### 🧠 Consultas y resúmenes clave")

    # Consulta 1: top toneladas
    top_ton = pd.DataFrame()
    if not prep_filtrado.empty:
        top_ton = (
            prep_filtrado.groupby("proceso", as_index=False)["toneladas_procesadas"]
            .sum()
            .rename(columns={"toneladas_procesadas": "total_toneladas"})
            .sort_values("total_toneladas", ascending=False)
        )

    # Consulta 2: top costo
    top_costo = pd.DataFrame()
    if not prep_filtrado.empty:
        top_costo = (
            prep_filtrado.groupby("proceso", as_index=False)["costo_tonelada_usd"]
            .mean()
            .rename(columns={"costo_tonelada_usd": "costo_promedio"})
            .sort_values("costo_promedio", ascending=False)
        )

    # Consulta 3: energía por tonelada
    energia_ton = pd.DataFrame()
    if not prep_filtrado.empty:
        energia_ton = (
            prep_filtrado.groupby("proceso", as_index=False)
            .agg({
                "consumo_energia_kwh": "sum",
                "toneladas_procesadas": "sum"
            })
        )
        energia_ton["kwh_por_tonelada"] = (
            energia_ton["consumo_energia_kwh"] / energia_ton["toneladas_procesadas"]
        )
        energia_ton = energia_ton[["proceso", "kwh_por_tonelada"]].sort_values(
            "kwh_por_tonelada", ascending=False
        )

    # Consulta 4: registros sobre el promedio
    sobre_promedio = pd.DataFrame()
    if not prep_filtrado.empty:
        prom_ton = prep_filtrado["toneladas_procesadas"].mean()
        sobre_promedio = prep_filtrado[prep_filtrado["toneladas_procesadas"] > prom_ton]

    col_q1, col_q2 = st.columns(2)

    with col_q1:
        st.markdown("#### Top procesos por toneladas")
        st.dataframe(top_ton, use_container_width=True)

        st.markdown("#### Top procesos por costo promedio")
        st.dataframe(top_costo, use_container_width=True)

    with col_q2:
        st.markdown("#### Procesos con mayor consumo energético por tonelada")
        st.dataframe(energia_ton, use_container_width=True)

        st.markdown("#### Registros con toneladas sobre el promedio")
        st.dataframe(sobre_promedio, use_container_width=True)

    st.markdown("---")

    # -----------------------------------------------------
    # RESUMEN DESCARGABLE
    # -----------------------------------------------------
    st.markdown("### ⬇️ Exportar resumen ejecutivo")

    resumen_dashboard = pd.DataFrame({
        "indicador": [
            "Toneladas totales",
            "Costo promedio USD/t",
            "Recuperación promedio %",
            "Extracción promedio %",
            "Mejora pureza promedio"
        ],
        "valor": [
            total_ton,
            costo_prom,
            rec_prom,
            ext_prom,
            mejora_pureza_prom
        ]
    })

    st.dataframe(resumen_dashboard, use_container_width=True)

    st.download_button(
        label="Descargar resumen ejecutivo",
        data=resumen_dashboard.to_csv(index=False).encode("utf-8"),
        file_name="resumen_dashboard.csv",
        mime="text/csv"
    )