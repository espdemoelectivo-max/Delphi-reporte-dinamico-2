import streamlit as st
import pandas as pd
import requests
from io import StringIO

st.set_page_config(page_title="Reporte Clínico Delphi", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f4f5f9; }
    .report-header { text-align: center; padding: 20px; background: linear-gradient(135deg, #1E2D6B, #2a3d8f); border-radius: 12px; margin-bottom: 20px; }
    .info-box { background-color: #ffffff; padding: 15px; border: 1px solid #e0e0e0; border-radius: 8px; height: 100%; border-top: 3px solid #1E2D6B; }
    .date-box { background-color: #ffffff; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #e0e0e0; border-bottom: 3px solid #E0157A; }
    .metric-title { font-size: 13px; color: #9B9B9B; margin-bottom: 2px; text-transform: uppercase; font-weight: 600; }
    .metric-value { font-size: 26px; font-weight: bold; color: #1E2D6B; }
    .hogar-card { background-color: #fff0f7; padding: 15px; border-radius: 10px; border-left: 5px solid #1E2D6B; margin-top: 10px; }
    .section-title { color: #1E2D6B; border-left: 4px solid #E0157A; padding-left: 10px; }
    div[data-testid="stSidebar"] { background-color: #1E2D6B; }
    div[data-testid="stSidebar"] * { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=30)
def cargar_datos():
    url = "https://docs.google.com/spreadsheets/d/1HdQ0uLeISE-8fdFdyNNu9M5tZu4Ydl17nMdo1M-uXv4/export?format=csv&gid=923584266"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, allow_redirects=True)
    response.raise_for_status()
    data = pd.read_csv(StringIO(response.text), encoding="utf-8")
    data.columns = data.columns.str.strip()
    return data

df = cargar_datos()

def obtener_dato(df_subset, keyword, default="Pendiente"):
    if df_subset.empty:
        return default
    cols = [c for c in df_subset.columns if keyword.lower() in c.lower()]
    if cols:
        val = df_subset.iloc[-1][cols[0]]
        if pd.isna(val) or str(val).strip() == "":
            return default
        return val
    return default

col_nombre = [c for c in df.columns if "nombre" in c.lower()][0]
col_tipo_ev = [c for c in df.columns if "tipo" in c.lower() and "eval" in c.lower()][0]

st.sidebar.image("https://img.icons8.com/color/96/medical-history.png", width=80)
st.sidebar.title("Gestión Delphi")

lista_p = [p for p in df[col_nombre].dropna().unique() if str(p).strip() != ""]
paciente = st.sidebar.selectbox("Seleccionar Paciente:", lista_p)

p_data = df[df[col_nombre] == paciente]
ev_inicial = p_data[p_data[col_tipo_ev].astype(str).str.contains("Inicial", case=False, na=False)]
ev_hito = p_data[p_data[col_tipo_ev].astype(str).str.contains("Hito", case=False, na=False)]
ev_final = p_data[p_data[col_tipo_ev].astype(str).str.contains("Final", case=False, na=False)]

st.markdown(f"""
    <div class="report-header">
        <h1 style="color: white; margin-bottom: 0; letter-spacing: 2px;">CENTRO CLÍNICO DELPHI</h1>
        <p style="color: #E0157A; font-size: 1.1em; font-weight: 600; margin: 4px 0;">Reporte Kinesiológico Estandarizado</p>
        <h3 style="color: #f0f0f0; margin-top: 6px;">PACIENTE: {paciente}</h3>
    </div>
    """, unsafe_allow_html=True)

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.markdown(f"""<div class="info-box">
        <b style="color:#1E2D6B;">Paciente:</b> {paciente}<br>
        <b style="color:#1E2D6B;">RUT:</b> {obtener_dato(ev_inicial, 'Rut', '—')}<br>
        <b style="color:#1E2D6B;">Edad:</b> {obtener_dato(ev_inicial, 'Edad', '—')}
    </div>""", unsafe_allow_html=True)
with col_b:
    st.markdown(f"""<div class="info-box">
        <b style="color:#1E2D6B;">Diagnóstico Médico:</b><br>
        {obtener_dato(ev_inicial, 'Diagnóstico', '—')}<br>
        <b style="color:#1E2D6B;">Visita Médico:</b> {obtener_dato(ev_inicial, 'Visita Médico', '—')}
    </div>""", unsafe_allow_html=True)
with col_c:
    st.markdown(f"""<div class="info-box">
        <b style="color:#1E2D6B;">Médico:</b> {obtener_dato(ev_inicial, 'Médico', '—')}<br>
        <b style="color:#1E2D6B;">Kinesiólogo:</b> {obtener_dato(ev_inicial, 'Kinesiólogo', '—')}<br>
        <b style="color:#1E2D6B;">Contacto:</b> {obtener_dato(ev_inicial, 'Contacto', '—')}
    </div>""", unsafe_allow_html=True)

st.write("")
st.markdown("<p style='color:#1E2D6B; font-weight:700; font-size:15px;'>📅 CRONOLOGÍA DEL TRATAMIENTO</p>", unsafe_allow_html=True)
d1, d2, d3, d4, d5, d6 = st.columns(6)
fechas = [
    ("Visita Médico",   obtener_dato(ev_inicial, 'Visita Médico', '—')),
    ("Inicio Licencia", obtener_dato(ev_inicial, 'Inicio licencia', '—')),
    ("Eval. Inicial",   obtener_dato(ev_inicial, 'Evaluación inicial', 'Pendiente')),
    ("1º Sesión Kine",  "—"),
    ("Hito (Sesión 6)", obtener_dato(ev_hito, 'Sesión hito', 'Pendiente')),
    ("Eval. Final",     obtener_dato(ev_final, 'Evaluación Final', 'Pendiente'))
]
for col, (label, date) in zip([d1, d2, d3, d4, d5, d6], fechas):
    col.markdown(f"""<div class="date-box">
        <small style="color:#9B9B9B; font-weight:600;">{label}</small><br>
        <b style="color:#1E2D6B;">{date}</b>
    </div>""", unsafe_allow_html=True)

st.divider()

PILARES = [
    ("Sedentarismo", "Pilar 1"),
    ("Sueño",        "Pilar 2"),
    ("Estrés",       "Pilar 3"),
    ("Alimentación", "Pilar 4"),
    ("Tóxicos",      "Pilar 5"),
    ("Relaciones",   "Pilar 6"),
]

def mostrar_pilares(df_ev):
    st.markdown("<p style='color:#1E2D6B; font-weight:700; font-size:15px;'>🧩 DIRECTRIZ: PILARES DE SALUD ABORDADOS</p>", unsafe_allow_html=True)

    # Leer los pilares marcados en el checkbox del Forms
    pilares_raw = obtener_dato(df_ev, 'Marcar los pilares', '')
    pilares_activos = []
    if pilares_raw and pilares_raw not in ["Pendiente", "—"]:
        for nombre, _ in PILARES:
            if nombre.lower() in pilares_raw.lower():
                pilares_activos.append(nombre)

    col_tabs, col_hogar = st.columns([3, 1])

    with col_tabs:
        # Labels con emoji de alerta para los activos (los resalta visualmente en el tab)
        tab_labels = []
        for nombre, _ in PILARES:
            if nombre in pilares_activos:
                tab_labels.append(f"🔵 {nombre}")
            else:
                tab_labels.append(nombre)

        tabs = st.tabs(tab_labels)
        for tab, (nombre, keyword) in zip(tabs, PILARES):
            with tab:
                recomendacion = obtener_dato(df_ev, keyword, "Sin indicios / No abordado")
                es_activo = nombre in pilares_activos

                if es_activo:
                    st.markdown(f'''
                        <div style="background-color:#e8eaf6; padding:20px; border-radius:10px;
                                    border-left:6px solid #E0157A; margin-bottom:10px;">
                            <h4 style="color:#1E2D6B; margin-top:0; font-weight:800;">
                                ✅ {nombre} <span style="font-size:13px; color:#E0157A; font-weight:600;">— ABORDADO EN SESIÓN</span>
                            </h4>
                            <p style="font-size:1.08em; margin:0; color:#1E2D6B;">{recomendacion}</p>
                        </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''
                        <div style="background-color:#f7f7f7; padding:20px; border-radius:10px;
                                    border-left:6px solid #cccccc; margin-bottom:10px;">
                            <h4 style="color:#9B9B9B; margin-top:0;">⬜ {nombre}</h4>
                            <p style="font-size:1.05em; margin:0; color:#aaaaaa;">{recomendacion}</p>
                        </div>
                    ''', unsafe_allow_html=True)

    with col_hogar:
        rec_hogar = obtener_dato(df_ev, 'Recomendación para el hogar', 'Pendiente')
        st.markdown(f'''
            <div class="hogar-card">
                <h4 style="color:#1E2D6B; margin-top:0;">🏠 Recomendación para el hogar</h4>
                <p style="font-size:1em; margin:0;">{rec_hogar}</p>
            </div>
        ''', unsafe_allow_html=True)


def mostrar_bloque_evaluacion(titulo, df_ev, keyword_dolor, keyword_groc, is_hito=False, is_final=False):
    st.markdown(f"<h3 class='section-title'>{titulo}</h3>", unsafe_allow_html=True)

    if df_ev.empty:
        st.info("Estado: Pendiente (Aún no registrada)")
        return

    col_eval, col_groc = st.columns([2, 1])

    with col_eval:
        st.subheader("Evaluación Clínica")
        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<p class="metric-title">DOLOR (EVA)</p><p class="metric-value">{obtener_dato(df_ev, keyword_dolor)}</p>', unsafe_allow_html=True)
        m2.markdown(f'<p class="metric-title">RANGO MOV.</p><p class="metric-value">{obtener_dato(df_ev, "Rango de Movimiento")}</p>', unsafe_allow_html=True)
        m3.markdown(f'<p class="metric-title">FUERZA CORE</p><p class="metric-value">{obtener_dato(df_ev, "Fuerza CORE")}</p>', unsafe_allow_html=True)

        if is_hito:
            st.info(f"**Matriz M-A-R (Decisión):** {obtener_dato(df_ev, 'Decisión Clínica')}")
        if is_final:
            st.success(f"**Motivo de Alta:** {obtener_dato(df_ev, 'Motivo del Alta')}")

    with col_groc:
        st.subheader("GROC")
        st.markdown(f'''
            <div style="text-align:center; padding:20px; border:2px solid #E0157A;
                        border-radius:10px; background-color:#fff0f7;">
                <span style="font-size:40px; font-weight:bold; color:#E0157A;">
                    {obtener_dato(df_ev, keyword_groc)}
                </span><br>
                <small style="color:#9B9B9B;">Puntaje de Cambio Percibido</small>
            </div>
        ''', unsafe_allow_html=True)

    st.write("")
    mostrar_pilares(df_ev)
    st.warning(f"**NOTAS PARA EL MÉDICO TRATANTE:** {obtener_dato(df_ev, 'Notas')}")


mostrar_bloque_evaluacion("EVALUACIÓN INICIAL", ev_inicial, "Dolor EVA inicial", "Groc inicial")
st.divider()
mostrar_bloque_evaluacion("SESIÓN HITO (CONTROL DE AVANCE)", ev_hito, "Dolor EVA Actual", "Groc Sesión Hito", is_hito=True)
st.divider()
mostrar_bloque_evaluacion("EVALUACIÓN FINAL Y ALTA", ev_final, "Dolor EVA Actual", "Groc Evaluación Final", is_final=True)
