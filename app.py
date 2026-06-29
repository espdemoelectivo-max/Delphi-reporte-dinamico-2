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

# ═══════════════════════════════════════════════════════════
# MAPEO EXACTO DE COLUMNAS
# (Columnas duplicadas en el Sheet → pandas las renombra con .1 .2)
# ═══════════════════════════════════════════════════════════
C = {
    # Datos generales
    "nombre":       "Nombre del Paciente",
    "rut":          "Rut",
    "edad":         "Edad",
    "tipo_eval":    "Tipo de Evaluación a registrar",
    "diagnostico":  "Diagnóstico médico",
    "medico":       "Médico",
    "kinesiologo":  "Kinesiólogo",
    "contacto":     "Contacto",
    "visita_medico":"Visita Médico",
    "inicio_lic":   "Inicio licencia",

    # ── EVALUACIÓN INICIAL ──────────────────────────────────
    "fecha_ini":    "Evaluación inicial",
    "dolor_ini":    "Dolor EVA inicial",
    "rom_ini":      "Rango de Movimiento (ROM)",
    "core_ini":     "Fuerza CORE",
    "groc_ini":     "Groc inicial",
    "pilares_ini":  "(Marcar los pilares abordados en la sesión):",
    "p1_ini":       "Pilar 1 - Sedentarismo",
    "p2_ini":       "Pilar 2 - Sueño",
    "p3_ini":       "Pilar 3 - Estrés",
    "p4_ini":       "Pilar 4 - Alimentación",
    "p5_ini":       "Pilar 5 - Tóxicos",
    "p6_ini":       "Pilar 6 - Relaciones",
    "hogar_ini":    "Recomendación para el hogar",
    "notas_ini":    "Notas para el médico tratante:",

    # ── SESIÓN HITO ─────────────────────────────────────────
    "fecha_hito":   "Sesión hito",
    "dolor_hito":   "Dolor EVA Actual",
    "rom_hito":     "Rango de Movimiento (ROM).1",
    "core_hito":    "Fuerza CORE.1",
    "groc_hito":    "Groc Sesión Hito",
    "pilares_hito": "(Marcar los pilares abordados en la sesión):.1",
    "p1_hito":      "Pilar 1 - Sedentarismo.1",
    "p2_hito":      "Pilar 2 - Sueño.1",
    "p3_hito":      "Pilar 3 - Estrés.1",
    "p4_hito":      "Pilar 4 - Alimentación.1",
    "p5_hito":      "Pilar 5 - Tóxicos.1",
    "p6_hito":      "Pilar 6 - Relaciones.1",
    "hogar_hito":   "Recomendación para el hogar (pilares seleccionados)",
    "decision":     "Decisión Clínica (Hito Intermedio):",
    "notas_hito":   "Notas para el médico tratante:.1",

    # ── EVALUACIÓN FINAL ────────────────────────────────────
    "fecha_final":  "Evaluación Final",
    "dolor_final":  "Dolor EVA Actual.1",
    "rom_final":    "Rango de Movimiento (ROM).2",
    "core_final":   "Fuerza CORE.2",
    "groc_final":   "Groc Evaluación Final",
    "pilares_final":"(Marcar los pilares abordados en la sesión):.2",
    "p1_final":     "Pilar 1 - Sedentarismo.2",
    "p2_final":     "Pilar 2 - Sueño.2",
    "p3_final":     "Pilar 3 - Estrés.2",
    "p4_final":     "Pilar 4 - Alimentación.2",
    "p5_final":     "Pilar 5 - Tóxicos.2",
    "p6_final":     "Pilar 6 - Relaciones.2",
    "hogar_final":  "Recomendación para el hogar (pilares seleccionados) ",  # tiene espacio al final
    "notas_final":  "Notas para el médico tratante:.2",
    "motivo_alta":  "Motivo del Alta",
}

PILARES = ["Sedentarismo", "Sueño", "Estrés", "Alimentación", "Tóxicos", "Relaciones"]

# ═══════════════════════════════════════════════════════════
# CARGA DE DATOS
# ═══════════════════════════════════════════════════════════
@st.cache_data(ttl=30)
def cargar_datos():
    url = "https://docs.google.com/spreadsheets/d/1HdQ0uLeISE-8fdFdyNNu9M5tZu4Ydl17nMdo1M-uXv4/export?format=csv&gid=923584266"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, allow_redirects=True)
    r.raise_for_status()
    df = pd.read_csv(StringIO(r.text), encoding="utf-8", header=0)
    df.columns = df.columns.str.strip()
    return df

df = cargar_datos()

# ── Verificación de columnas (debug oculto) ──────────────────
cols_reales = set(df.columns.tolist())
cols_esperadas = set(C.values())
faltantes = cols_esperadas - cols_reales

# ═══════════════════════════════════════════════════════════
# FUNCIÓN DE EXTRACCIÓN SEGURA
# ═══════════════════════════════════════════════════════════
def g(fila, key, default="—"):
    """Extrae valor de una fila (pd.Series) usando la clave del dict C."""
    if fila is None:
        return default
    col_name = C.get(key)
    if not col_name or col_name not in fila.index:
        return default
    val = fila[col_name]
    if pd.isna(val) or str(val).strip() in ("", "nan"):
        return default
    return str(val).strip()

# ═══════════════════════════════════════════════════════════
# SIDEBAR — Selección por RUT
# ═══════════════════════════════════════════════════════════
st.sidebar.image(
    "https://raw.githubusercontent.com/espdemoelectivo-max/delphi-reporte-dinamico-2/main/Delphi Logo.png",
    use_container_width=True
)
st.sidebar.title("Gestión Delphi")

# Un registro por RUT único (nombre de la primera aparición)
pacientes = (
    df[[C["nombre"], C["rut"]]]
    .dropna(subset=[C["rut"]])
    .drop_duplicates(subset=[C["rut"]])
    .reset_index(drop=True)
)
pacientes["display"] = (
    pacientes[C["nombre"]].str.strip() + "  |  " + pacientes[C["rut"]].str.strip()
)

opcion = st.sidebar.selectbox("Seleccionar Paciente:", pacientes["display"].tolist())
rut_sel    = pacientes.loc[pacientes["display"] == opcion, C["rut"]].values[0].strip()
nombre_sel = pacientes.loc[pacientes["display"] == opcion, C["nombre"]].values[0].strip()

# Todas las filas del paciente
filas = df[df[C["rut"]].astype(str).str.strip() == rut_sel]

# Separar por tipo de evaluación (tomar la última fila de cada tipo)
def ultima_fila(tipo_keyword):
    mask = filas[C["tipo_eval"]].astype(str).str.contains(tipo_keyword, case=False, na=False)
    sub = filas[mask]
    return sub.iloc[-1] if not sub.empty else None

fila_ini   = ultima_fila("Inicial")
fila_hito  = ultima_fila("Hito")
fila_final = ultima_fila("Final")

# Fila de referencia para datos demográficos
fila_demo = next((f for f in [fila_ini, fila_hito, fila_final] if f is not None), None)

# ═══════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
    <div class="report-header">
        <h1 style="color:white; margin-bottom:0; letter-spacing:2px;">CENTRO CLÍNICO DELPHI</h1>
        <p style="color:#E0157A; font-size:1.1em; font-weight:600; margin:4px 0;">Reporte Kinesiológico Estandarizado</p>
        <h3 style="color:#f0f0f0; margin-top:6px;">PACIENTE: {nombre_sel.upper()}</h3>
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# BLOQUE INFO PERSONAL
# ═══════════════════════════════════════════════════════════
ca, cb, cc = st.columns(3)
with ca:
    st.markdown(f"""<div class="info-box">
        <b style="color:#1E2D6B;">Paciente:</b> {nombre_sel}<br>
        <b style="color:#1E2D6B;">RUT:</b> {rut_sel}<br>
        <b style="color:#1E2D6B;">Edad:</b> {g(fila_demo, "edad")} años
    </div>""", unsafe_allow_html=True)
with cb:
    st.markdown(f"""<div class="info-box">
        <b style="color:#1E2D6B;">Diagnóstico:</b><br>{g(fila_demo, "diagnostico")}<br><br>
        <b style="color:#1E2D6B;">Visita Médico:</b> {g(fila_demo, "visita_medico")}
    </div>""", unsafe_allow_html=True)
with cc:
    st.markdown(f"""<div class="info-box">
        <b style="color:#1E2D6B;">Médico:</b> {g(fila_demo, "medico")}<br>
        <b style="color:#1E2D6B;">Kinesiólogo:</b> {g(fila_demo, "kinesiologo")}<br>
        <b style="color:#1E2D6B;">Contacto:</b> {g(fila_demo, "contacto")}
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# CRONOLOGÍA
# ═══════════════════════════════════════════════════════════
st.write("")
st.markdown("<p style='color:#1E2D6B; font-weight:700; font-size:15px;'>📅 CRONOLOGÍA DEL TRATAMIENTO</p>", unsafe_allow_html=True)

d1, d2, d3, d4, d5, d6 = st.columns(6)
fechas = [
    ("Visita Médico",   g(fila_demo,  "visita_medico")),
    ("Inicio Licencia", g(fila_demo,  "inicio_lic")),
    ("Eval. Inicial",   g(fila_ini,   "fecha_ini")),
    ("1º Sesión Kine",  "—"),
    ("Hito (Sesión 6)", g(fila_hito,  "fecha_hito")),
    ("Eval. Final",     g(fila_final, "fecha_final")),
]
for col_ui, (label, date) in zip([d1, d2, d3, d4, d5, d6], fechas):
    col_ui.markdown(f"""<div class="date-box">
        <small style="color:#9B9B9B; font-weight:600;">{label}</small><br>
        <b style="color:#1E2D6B;">{date}</b>
    </div>""", unsafe_allow_html=True)

st.divider()

# ═══════════════════════════════════════════════════════════
# FUNCIÓN PILARES
# ═══════════════════════════════════════════════════════════
def mostrar_pilares(fila, sufijo):
    """sufijo: 'ini' | 'hito' | 'final'"""
    pilares_raw = g(fila, f"pilares_{sufijo}", "")
    pilares_activos = [n for n in PILARES if n.lower() in pilares_raw.lower()] if pilares_raw != "—" else []

    st.markdown("<p style='color:#1E2D6B; font-weight:700; font-size:15px; margin-top:16px;'>🧩 DIRECTRIZ: PILARES DE SALUD ABORDADOS</p>", unsafe_allow_html=True)
    col_tabs_ui, col_hogar_ui = st.columns([3, 1])

    with col_tabs_ui:
        tab_labels = [f"✅ {n}" if n in pilares_activos else f"○ {n}" for n in PILARES]
        tabs = st.tabs(tab_labels)
        claves_pilar = [f"p1_{sufijo}", f"p2_{sufijo}", f"p3_{sufijo}",
                        f"p4_{sufijo}", f"p5_{sufijo}", f"p6_{sufijo}"]
        for tab, nombre, clave in zip(tabs, PILARES, claves_pilar):
            with tab:
                recomendacion = g(fila, clave, "Sin indicaciones registradas")
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
        rec_hogar = g(fila, f"hogar_{sufijo}")
        st.markdown(f"""
            <div class="hogar-card">
                <h4 style="color:#1E2D6B; margin-top:0;">🏠 Recomendación para el hogar</h4>
                <p style="font-size:1em; margin:0;">{rec_hogar}</p>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# FUNCIÓN BLOQUE CLÍNICO
# ═══════════════════════════════════════════════════════════
def bloque_clinico(titulo, fila, sufijo, is_hito=False, is_final=False):
    st.markdown(f"<h3 class='section-title'>{titulo}</h3>", unsafe_allow_html=True)

    if fila is None:
        st.info("⏳ Estado: Pendiente — aún no registrada en el sistema.")
        return

    col_ev, col_gr = st.columns([2, 1])
    with col_ev:
        st.subheader("Evaluación Clínica")
        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<p class="metric-title">DOLOR (EVA)</p><p class="metric-value">{g(fila, f"dolor_{sufijo}")}</p>', unsafe_allow_html=True)
        m2.markdown(f'<p class="metric-title">RANGO MOV.</p><p class="metric-value">{g(fila, f"rom_{sufijo}")}</p>',   unsafe_allow_html=True)
        m3.markdown(f'<p class="metric-title">FUERZA CORE</p><p class="metric-value">{g(fila, f"core_{sufijo}")}</p>', unsafe_allow_html=True)
        if is_hito:
            st.info(f"**Decisión Clínica (M-A-R):** {g(fila, 'decision')}")
        if is_final:
            st.success(f"**Motivo de Alta:** {g(fila, 'motivo_alta')}")

    with col_gr:
        st.subheader("GROC")
        st.markdown(f"""
            <div style="text-align:center; padding:20px; border:2px solid #E0157A; border-radius:10px; background:#fff0f7;">
                <span style="font-size:40px; font-weight:bold; color:#E0157A;">{g(fila, f"groc_{sufijo}")}</span><br>
                <small style="color:#9B9B9B;">Puntaje de Cambio Percibido</small>
            </div>""", unsafe_allow_html=True)

    mostrar_pilares(fila, sufijo)

    notas = g(fila, f"notas_{sufijo}")
    if notas != "—":
        st.warning(f"**📋 NOTAS PARA EL MÉDICO TRATANTE:** {notas}")

# ═══════════════════════════════════════════════════════════
# RENDER BLOQUES
# ═══════════════════════════════════════════════════════════
bloque_clinico("📋 EVALUACIÓN INICIAL",               fila_ini,   "ini")
st.divider()
bloque_clinico("🔁 SESIÓN HITO (CONTROL DE AVANCE)",  fila_hito,  "hito",  is_hito=True)
st.divider()
bloque_clinico("✅ EVALUACIÓN FINAL Y ALTA",           fila_final, "final", is_final=True)

# ═══════════════════════════════════════════════════════════
# DEBUG — Inspector (comentar cuando todo funcione)
# ═══════════════════════════════════════════════════════════
with st.expander("🔧 Inspector de columnas (debug — ocultar cuando funcione)", expanded=False):
    st.write("**Columnas detectadas en el Sheet:**")
    for i, c in enumerate(df.columns):
        st.write(f"`{i}` → `{c}`")
    if faltantes:
        st.error(f"⚠️ Columnas NO encontradas: {faltantes}")
    else:
        st.success("✅ Todas las columnas mapeadas correctamente")
