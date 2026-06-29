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
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}
    response = requests.get(url, headers=headers, allow_redirects=True)
    response.raise_for_status()
    data = pd.read_csv(StringIO(response.text), encoding="utf-8", header=0)
    data.columns = data.columns.str.strip()
    return data

df = cargar_datos()

# Detectar columnas clave dinámicamente
col_nombre = [c for c in df.columns if "nombre" in c.lower()][0]
col_tipo   = [c for c in df.columns if "tipo" in c.lower() and "eval" in c.lower()][0]

# Mapeo exacto de columnas
COL = {
    "diagnostico":   "Diagnóstico médico",
    "medico":        "Médico",
    "kinesiologo":   "Kinesiólogo",
    "contacto":      "Contacto",
    "rut":           "Rut",
    "edad":          "Edad",
    "visita_medico": "Visita Médico",
    "inicio_lic":    "Inicio licencia",
    "eval_ini_f":    "Evaluación inicial",
    "dolor_ini":     "Dolor EVA inicial",
    "rom_ini":       "Rango de Movimiento (ROM)",
    "core_ini":      "Fuerza CORE",
    "groc_ini":      "Groc inicial",
    "pilares_ini":   "(Marcar los pilares abordados en la sesión):",
    "p1_ini":        "Pilar 1 - Sedentarismo",
    "p2_ini":        "Pilar 2 - Sueño",
    "p3_ini":        "Pilar 3 - Estrés",
    "p4_ini":        "Pilar 4 - Alimentación",
    "p5_ini":        "Pilar 5 - Tóxicos",
    "p6_ini":        "Pilar 6 - Relaciones",
    "hogar_ini":     "Recomendación para el hogar",
    "notas_ini":     "Notas para el médico tratante:",
    "sesion_hito":   "Sesión hito",
    "dolor_hito":    "Dolor EVA Actual",
    "rom_hito":      "Rango de Movimiento (ROM).1",
    "core_hito":     "Fuerza CORE.1",
    "groc_hito":     "Groc Sesión Hito",
    "pilares_hito":  "(Marcar los pilares abordados en la sesión):.1",
    "p1_hito":       "Pilar 1 - Sedentarismo.1",
    "p2_hito":       "Pilar 2 - Sueño.1",
    "p3_hito":       "Pilar 3 - Estrés.1",
    "p4_hito":       "Pilar 4 - Alimentación.1",
    "p5_hito":       "Pilar 5 - Tóxicos.1",
    "p6_hito":       "Pilar 6 - Relaciones.1",
    "hogar_hito":    "Recomendación para el hogar (pilares seleccionados)",
    "decision":      "Decisión Clínica (Hito Intermedio):",
    "notas_hito":    "Notas para el médico tratante:.1",
    "eval_final_f":  "Evaluación Final",
    "dolor_final":   "Dolor EVA Actual.1",
    "rom_final":     "Rango de Movimiento (ROM).2",
    "core_final":    "Fuerza CORE.2",
    "groc_final":    "Groc Evaluación Final",
    "pilares_final": "(Marcar los pilares abordados en la sesión):.2",
    "p1_final":      "Pilar 1 - Sedentarismo.2",
    "p2_final":      "Pilar 2 - Sueño.2",
    "p3_final":      "Pilar 3 - Estrés.2",
    "p4_final":      "Pilar 4 - Alimentación.2",
    "p5_final":      "Pilar 5 - Tóxicos.2",
    "p6_final":      "Pilar 6 - Relaciones.2",
    "hogar_final":   "Recomendación para el hogar (pilares seleccionados) ",
    "notas_final":   "Notas para el médico tratante:.2",
    "motivo_alta":   "Motivo del Alta",
}

def get(df_sub, key, default="—"):
    if df_sub.empty:
        return default
    # Buscar por nombre exacto primero
    col = COL.get(key)
    if col and col in df_sub.columns:
        val = df_sub.iloc[-1][col]
        if pd.isna(val) or str(val).strip() == "":
            return default
        return str(val).strip()
    # Si no encuentra, buscar por keyword parcial
    matches = [c for c in df_sub.columns if key.lower().replace("_", " ") in c.lower()]
    if matches:
        val = df_sub.iloc[-1][matches[0]]
        if pd.isna(val) or str(val).strip() == "":
            return default
        return str(val).strip()
    return default

# ── SIDEBAR ──────────────────────────────────────────────
st.sidebar.image(
    "https://raw.githubusercontent.com/espdemoelectivo-max/delphi-reporte-dinamico-2/main/Delphi Logo.png",
    use_container_width=True
)
st.sidebar.title("Gestión Delphi")
lista_p = [p for p in df[col_nombre].dropna().unique() if str(p).strip() != ""]
paciente = st.sidebar.selectbox("Seleccionar Paciente:", lista_p)

# Filtrar datos
p_data    = df[df[col_nombre] == paciente]
ev_inicial = p_data[p_data[col_tipo].astype(str).str.contains("Inicial", case=False, na=False)]
ev_hito    = p_data[p_data[col_tipo].astype(str).str.contains("Hito",    case=False, na=False)]
ev_final   = p_data[p_data[col_tipo].astype(str).str.contains("Final",   case=False, na=False)]

# ── HEADER ───────────────────────────────────────────────
st.markdown(f"""
    <div class="report-header">
        <h1 style="color:white; margin-bottom:0; letter-spacing:2px;">CENTRO CLÍNICO DELPHI</h1>
        <p style="color:#E0157A; font-size:1.1em; font-weight:600; margin:4px 0;">Reporte Kinesiológico Estandarizado</p>
        <h3 style="color:#f0f0f0; margin-top:6px;">PACIENTE: {paciente}</h3>
    </div>""", unsafe_allow_html=True)

# ── INFO PERSONAL ─────────────────────────────────────────
col_a, col_b, col_c = st.columns(3)
with col_a:
    st.markdown(f"""<div class="info-box">
        <b style="color:#1E2D6B;">Paciente:</b> {paciente}<br>
        <b style="color:#1E2D6B;">RUT:</b> {get(ev_inicial,'rut')}<br>
        <b style="color:#1E2D6B;">Edad:</b> {get(ev_inicial,'edad')}
    </div>""", unsafe_allow_html=True)
with col_b:
    st.markdown(f"""<div class="info-box">
        <b style="color:#1E2D6B;">Diagnóstico:</b><br>{get(ev_inicial,'diagnostico')}<br>
        <b style="color:#1E2D6B;">Visita Médico:</b> {get(ev_inicial,'visita_medico')}
    </div>""", unsafe_allow_html=True)
with col_c:
    st.markdown(f"""<div class="info-box">
        <b style="color:#1E2D6B;">Médico:</b> {get(ev_inicial,'medico')}<br>
        <b style="color:#1E2D6B;">Kinesiólogo:</b> {get(ev_inicial,'kinesiologo')}<br>
        <b style="color:#1E2D6B;">Contacto:</b> {get(ev_inicial,'contacto')}
    </div>""", unsafe_allow_html=True)

# ── CRONOLOGÍA ────────────────────────────────────────────
st.write("")
st.markdown("<p style='color:#1E2D6B; font-weight:700; font-size:15px;'>📅 CRONOLOGÍA DEL TRATAMIENTO</p>", unsafe_allow_html=True)
d1,d2,d3,d4,d5,d6 = st.columns(6)
fechas = [
    ("Visita Médico",   get(ev_inicial, 'visita_medico')),
    ("Inicio Licencia", get(ev_inicial, 'inicio_lic')),
    ("Eval. Inicial",   get(ev_inicial, 'eval_ini_f')),
    ("1º Sesión Kine",  "—"),
    ("Hito (Sesión 6)", get(ev_hito,    'sesion_hito')),
    ("Eval. Final",     get(ev_final,   'eval_final_f')),
]
for col,(label,date) in zip([d1,d2,d3,d4,d5,d6], fechas):
    col.markdown(f"""<div class="date-box">
        <small style="color:#9B9B9B; font-weight:600;">{label}</small><br>
        <b style="color:#1E2D6B;">{date}</b>
    </div>""", unsafe_allow_html=True)

st.divider()

# ── PILARES ───────────────────────────────────────────────
PILARES_NOMBRES = ["Sedentarismo","Sueño","Estrés","Alimentación","Tóxicos","Relaciones"]

def mostrar_pilares(df_ev, sufijo):
    keys_pilar   = [f"p1{sufijo}",f"p2{sufijo}",f"p3{sufijo}",f"p4{sufijo}",f"p5{sufijo}",f"p6{sufijo}"]
    key_checkbox = f"pilares{sufijo}"
    key_hogar    = f"hogar{sufijo}"

    pilares_raw = get(df_ev, key_checkbox, "")
    pilares_activos = [n for n in PILARES_NOMBRES if n.lower() in pilares_raw.lower()] if pilares_raw != "—" else []

    st.markdown("<p style='color:#1E2D6B; font-weight:700; font-size:15px; margin-top:16px;'>🧩 DIRECTRIZ: PILARES DE SALUD ABORDADOS</p>", unsafe_allow_html=True)
    col_tabs, col_hogar_ui = st.columns([3, 1])

    with col_tabs:
        tab_labels = [f"✅ {n}" if n in pilares_activos else f"○ {n}" for n in PILARES_NOMBRES]
        tabs = st.tabs(tab_labels)
        for tab, nombre, key in zip(tabs, PILARES_NOMBRES, keys_pilar):
            with tab:
                recomendacion = get(df_ev, key, "Sin indicios / No abordado")
                if nombre in pilares_activos:
                    st.markdown(f"""
                        <div style="background:#e8eaf6; padding:18px; border-radius:10px; border-left:6px solid #E0157A;">
                            <p style="margin:0; font-size:0.82em; font-weight:700; color:#E0157A; text-transform:uppercase; letter-spacing:1px;">✅ ABORDADO EN SESIÓN</p>
                            <p style="margin:8px 0 0 0; font-size:1.08em; color:#1E2D6B; font-weight:600;">{recomendacion}</p>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style="background:#f7f7f7; padding:18px; border-radius:10px; border-left:6px solid #cccccc;">
                            <p style="margin:0; font-size:0.82em; color:#bbbbbb; text-transform:uppercase; letter-spacing:1px;">No abordado</p>
                            <p style="margin:8px 0 0 0; font-size:1.05em; color:#aaaaaa;">{recomendacion}</p>
                        </div>""", unsafe_allow_html=True)

    with col_hogar_ui:
        rec_hogar = get(df_ev, key_hogar, "—")
        st.markdown(f"""
            <div class="hogar-card">
                <h4 style="color:#1E2D6B; margin-top:0;">🏠 Recomendación para el hogar</h4>
                <p style="font-size:1em; margin:0;">{rec_hogar}</p>
            </div>""", unsafe_allow_html=True)

# ── BLOQUES ───────────────────────────────────────────────
def bloque(titulo, df_ev, key_dolor, key_rom, key_core, key_groc, sufijo, is_hito=False, is_final=False):
    st.markdown(f"<h3 class='section-title'>{titulo}</h3>", unsafe_allow_html=True)
    if df_ev.empty:
        st.info("Estado: Pendiente (Aún no registrada)")
        return

    col_eval, col_groc = st.columns([2,1])
    with col_eval:
        st.subheader("Evaluación Clínica")
        m1,m2,m3 = st.columns(3)
        m1.markdown(f'<p class="metric-title">DOLOR (EVA)</p><p class="metric-value">{get(df_ev,key_dolor)}</p>', unsafe_allow_html=True)
        m2.markdown(f'<p class="metric-title">RANGO MOV.</p><p class="metric-value">{get(df_ev,key_rom)}</p>',   unsafe_allow_html=True)
        m3.markdown(f'<p class="metric-title">FUERZA CORE</p><p class="metric-value">{get(df_ev,key_core)}</p>', unsafe_allow_html=True)
        if is_hito:
            st.info(f"**Decisión Clínica:** {get(df_ev,'decision')}")
        if is_final:
            st.success(f"**Motivo de Alta:** {get(df_ev,'motivo_alta')}")
    with col_groc:
        st.subheader("GROC")
        st.markdown(f"""
            <div style="text-align:center; padding:20px; border:2px solid #E0157A; border-radius:10px; background:#fff0f7;">
                <span style="font-size:40px; font-weight:bold; color:#E0157A;">{get(df_ev,key_groc)}</span><br>
                <small style="color:#9B9B9B;">Puntaje de Cambio Percibido</small>
            </div>""", unsafe_allow_html=True)

    mostrar_pilares(df_ev, sufijo)

    key_notas = "notas_ini" if sufijo=="_ini" else ("notas_hito" if sufijo=="_hito" else "notas_final")
    st.warning(f"**NOTAS PARA EL MÉDICO TRATANTE:** {get(df_ev, key_notas)}")

bloque("EVALUACIÓN INICIAL",             ev_inicial, "dolor_ini",  "rom_ini",   "core_ini",   "groc_ini",   "_ini")
st.divider()
bloque("SESIÓN HITO (CONTROL DE AVANCE)", ev_hito,   "dolor_hito", "rom_hito",  "core_hito",  "groc_hito",  "_hito", is_hito=True)
st.divider()
bloque("EVALUACIÓN FINAL Y ALTA",         ev_final,  "dolor_final","rom_final", "core_final", "groc_final", "_final", is_final=True)
