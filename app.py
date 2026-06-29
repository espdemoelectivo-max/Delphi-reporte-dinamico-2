import streamlit as st
import pandas as pd

# 1. Configuración Estética Global
st.set_page_config(page_title="Reporte Clínico Delphi", layout="wide")

# CSS personalizado para emular el estilo (Colores Delphi)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .report-header { text-align: center; padding: 10px; background-color: white; border-radius: 10px; margin-bottom: 20px; }
    .info-box { background-color: #ffffff; padding: 15px; border: 1px solid #e0e0e0; border-radius: 8px; height: 100%; }
    .date-box { background-color: #f1f3f4; padding: 10px; border-radius: 5px; text-align: center; border: 1px solid #dcdcdc; }
    .metric-title { font-size: 14px; color: #666; margin-bottom: 2px; text-transform: uppercase; }
    .metric-value { font-size: 22px; font-weight: bold; color: #1a73e8; }
    .pilar-card { background-color: #e6f4ea; padding: 20px; border-radius: 10px; border-left: 5px solid #34a853; margin-bottom: 10px;}
    </style>
    """, unsafe_allow_html=True)

# 2. Conexión Automatizada (TTL=30 segundos)
import requests
from io import StringIO

@st.cache_data(ttl=30)
def cargar_datos():
    url = "https://docs.google.com/spreadsheets/d/1HdQ0uLeISE-8fdFdyNNu9M5tZu4Ydl17nMdo1M-uXv4/edit?resourcekey=&gid=923584266#gid=923584266"
    response = requests.get(url, allow_redirects=True)
    response.raise_for_status()
    data = pd.read_csv(StringIO(response.text))
    data.columns = data.columns.str.strip()
    return data

df = cargar_datos()

# Función dinámica para extraer datos evitando errores por cambios en los nombres de las columnas
def obtener_dato(df_subset, keyword, default="Pendiente"):
    if df_subset.empty:
        return default
    # Busca la primera columna que contenga la palabra clave
    cols = [c for c in df_subset.columns if keyword.lower() in c.lower()]
    if cols:
        val = df_subset.iloc[-1][cols[0]]
        if pd.isna(val) or str(val).strip() == "":
            return default
        return val
    return default

# Detectar columnas clave para los filtros
st.write(df.columns.tolist())  # línea temporal de diagnóstico
col_tipo_ev = [c for c in df.columns if "Tipo de Evaluación" in c][0]

# 3. Lógica de Selección de Paciente
st.sidebar.image("https://img.icons8.com/color/96/medical-history.png", width=80)
st.sidebar.title("Gestión Delphi")

# Lista de pacientes únicos limpiando vacíos
lista_p = [p for p in df[col_nombre].dropna().unique() if str(p).strip() != ""]
paciente = st.sidebar.selectbox("Seleccionar Paciente:", lista_p)

# Filtrar TODA la información del paciente seleccionado
p_data = df[df[col_nombre] == paciente]

# Separar la información según el tipo de evaluación en 3 variables distintas
ev_inicial = p_data[p_data[col_tipo_ev].astype(str).str.contains("Inicial", case=False, na=False)]
ev_hito = p_data[p_data[col_tipo_ev].astype(str).str.contains("Hito", case=False, na=False)]
ev_final = p_data[p_data[col_tipo_ev].astype(str).str.contains("Final", case=False, na=False)]

# --- ESTRUCTURA VISUAL DEL REPORTE ---

st.markdown(f"""
    <div class="report-header">
        <h1 style="color: #202124; margin-bottom: 0;">CENTRO CLÍNICO DELPHI</h1>
        <p style="color: #5f6368; font-size: 1.1em;">Reporte Kinesiológico Estandarizado</p>
        <h3 style="color: #d93025; margin-top: 0;">PACIENTE: {paciente}</h3>
    </div>
    """, unsafe_allow_html=True)

# BLOQUE 1: Información Personal (Alimentado por la evaluación inicial)
col_a, col_b, col_c = st.columns(3)
with col_a:
    st.markdown(f"""<div class="info-box">
        <b>Paciente:</b> {paciente}<br>
        <b>RUT:</b> {obtener_dato(ev_inicial, 'Rut', '—')}<br>
        <b>Edad:</b> {obtener_dato(ev_inicial, 'Edad', '—')}
    </div>""", unsafe_allow_html=True)
with col_b:
    st.markdown(f"""<div class="info-box">
        <b>Diagnóstico Médico:</b><br>
        {obtener_dato(ev_inicial, 'Diagnóstico', '—')}<br>
        <b>Visita Médico:</b> {obtener_dato(ev_inicial, 'Visita Médico', '—')}
    </div>""", unsafe_allow_html=True)
with col_c:
    st.markdown(f"""<div class="info-box">
        <b>Médico:</b> {obtener_dato(ev_inicial, 'Médico', '—')}<br>
        <b>Kinesiólogo:</b> {obtener_dato(ev_inicial, 'Kinesiólogo', '—')}<br>
        <b>Contacto:</b> {obtener_dato(ev_inicial, 'Contacto', '—')}
    </div>""", unsafe_allow_html=True)

st.write("") 

# BLOQUE 2: Recuadros de Fechas (Timeline general)
st.write("**CRONOLOGÍA DEL TRATAMIENTO**")
d1, d2, d3, d4, d5, d6 = st.columns(6)
fechas = [
    ("Visita Médico", obtener_dato(ev_inicial, 'Visita Médico', '—')),
    ("Inicio Licencia", obtener_dato(ev_inicial, 'Inicio licencia', '—')),
    ("Eval. Inicial", obtener_dato(ev_inicial, 'Evaluación inicial', 'Pendiente')),
    ("1º Sesión Kine", "—"), 
    ("Hito (Sesión 6)", obtener_dato(ev_hito, 'Sesión hito', 'Pendiente')),
    ("Eval. Final", obtener_dato(ev_final, 'Evaluación Final', 'Pendiente'))
]
for col, (label, date) in zip([d1, d2, d3, d4, d5, d6], fechas):
    col.markdown(f"""<div class="date-box"><small>{label}</small><br><b>{date}</b></div>""", unsafe_allow_html=True)

st.divider()

# --- FUNCIÓN DE RENDERIZADO DEL FORMATO M-A-R ---
# Esta función permite crear el mismo bloque exacto sin tener que copiar y pegar el código 3 veces.

def mostrar_bloque_evaluacion(titulo, df_ev, keyword_dolor, keyword_groc, is_hito=False, is_final=False):
    st.markdown(f"<h3 style='color: #1a73e8; margin-top: 20px;'>{titulo}</h3>", unsafe_allow_html=True)
    
    # Si la evaluación no existe aún para el paciente, muestra el banner y corta la ejecución
    if df_ev.empty:
        st.info("Estado: Pendiente (Aún no registrada)")
        return

    # Si existe, renderiza el bloque 3 y 4
    col_eval, col_groc = st.columns([2, 1])
    
    with col_eval:
        st.subheader("1. Evaluación Clínica")
        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<p class="metric-title">DOLOR (EVA)</p><p class="metric-value">{obtener_dato(df_ev, keyword_dolor)}</p>', unsafe_allow_html=True)
        m2.markdown(f'<p class="metric-title">RANGO MOV.</p><p class="metric-value">{obtener_dato(df_ev, "Rango de Movimiento")}</p>', unsafe_allow_html=True)
        m3.markdown(f'<p class="metric-title">FUERZA CORE</p><p class="metric-value">{obtener_dato(df_ev, "Fuerza CORE")}</p>', unsafe_allow_html=True)
        
        # Muestra resultados específicos si es la sesión hito o la final
        if is_hito:
            st.info(f"**Matriz M-A-R (Decisión):** {obtener_dato(df_ev, 'Decisión Clínica')}")
        if is_final:
            st.success(f"**Motivo de Alta:** {obtener_dato(df_ev, 'Motivo del Alta')}")

    with col_groc:
        st.subheader("GROC")
        st.markdown(f'''<div style="text-align: center; padding: 20px; border: 2px solid #1a73e8; border-radius: 10px;">
            <span style="font-size: 40px; font-weight: bold;">{obtener_dato(df_ev, keyword_groc)}</span><br>
            <small>Puntaje de Cambio Percibido</small>
        </div>''', unsafe_allow_html=True)

    st.write("")
    st.subheader("DIRECTRIZ: PILARES DE SALUD ABORDADOS")
    pilares_marcados = obtener_dato(df_ev, 'Pilares')
    st.write(f"**Pilares registrados en esta sesión:** {pilares_marcados}")
    
    tabs = st.tabs(["Sedentarismo", "Sueño", "Estrés", "Alimentación", "Tóxicos", "Relaciones"])
    recomendacion = obtener_dato(df_ev, 'Recomendación para el hogar')
    for tab in tabs:
        with tab:
            st.markdown(f'''
                <div class="pilar-card">
                    <h4>Recomendación Activa</h4>
                    <p style="font-size: 1.1em;">{recomendacion}</p>
                </div>
                ''', unsafe_allow_html=True)

    st.warning(f"**NOTAS PARA EL MÉDICO TRATANTE:** {obtener_dato(df_ev, 'Notas')}")


# --- RENDERIZADO SIMULTÁNEO DE LAS SESIONES ---

mostrar_bloque_evaluacion("EVALUACIÓN INICIAL", ev_inicial, "Dolor EVA inicial", "Groc inicial")
st.divider()

mostrar_bloque_evaluacion("SESIÓN HITO (CONTROL DE AVANCE)", ev_hito, "Dolor EVA Actual", "Groc Sesión Hito", is_hito=True)
st.divider()

mostrar_bloque_evaluacion("EVALUACIÓN FINAL Y ALTA", ev_final, "Dolor EVA Actual", "Groc Evaluación Final", is_final=True)
