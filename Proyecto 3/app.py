import streamlit as st
import pandas as pd
import mysql.connector

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(page_title="App Minera SQL", layout="wide")

st.title("⛏️ App de Consultas - Minería")

# =========================
# CONEXIÓN
# =========================
@st.cache_resource
def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # tu contraseña aquí
        database="mineria_operaciones"
    )

conexion = conectar()

# =========================
# FUNCIÓN QUERY
# =========================
def run_query(query):
    return pd.read_sql(query, conexion)

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙️ Opciones")

opcion = st.sidebar.selectbox(
    "Selecciona una opción",
    [
        "Ver tablas",
        "Consultas",
        "SQL libre"
    ]
)

# =========================
# 1. VER TABLAS
# =========================
if opcion == "Ver tablas":

    tabla = st.selectbox(
        "Selecciona tabla",
        [
            "dim_procesos",
            "preparacion_minerales",
            "extraccion_metales",
            "refinacion_metales"
        ]
    )

    query = f"SELECT * FROM {tabla} LIMIT 20;"
    df = run_query(query)

    st.dataframe(df, use_container_width=True)

# =========================
# 2. CONSULTAS
# =========================
elif opcion == "Consultas":

    consulta = st.selectbox(
        "Selecciona consulta",
        [
            "Toneladas por proceso",
            "Costo promedio",
            "Mejora de pureza"
        ]
    )

    if consulta == "Toneladas por proceso":
        query = """
        SELECT d.proceso,
               SUM(p.toneladas_procesadas) AS total_toneladas
        FROM preparacion_minerales p
        JOIN dim_procesos d ON p.id_proceso = d.id_proceso
        GROUP BY d.proceso
        ORDER BY total_toneladas DESC;
        """

    elif consulta == "Costo promedio":
        query = """
        SELECT d.proceso,
               AVG(p.costo_tonelada_usd) AS costo_promedio
        FROM preparacion_minerales p
        JOIN dim_procesos d ON p.id_proceso = d.id_proceso
        GROUP BY d.proceso;
        """

    else:
        query = """
        SELECT proceso,
               pureza_inicial_pct,
               pureza_final_pct,
               (pureza_final_pct - pureza_inicial_pct) AS mejora_pureza
        FROM refinacion_metales;
        """

    df = run_query(query)

    st.dataframe(df, use_container_width=True)

# =========================
# 3. SQL LIBRE
# =========================
elif opcion == "SQL libre":

    query = st.text_area("Escribe tu consulta SQL")

    if st.button("Ejecutar"):
        try:
            df = run_query(query)
            st.dataframe(df)
        except:
            st.error("Error en la consulta")