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
# CARGA DE DATOS — primero, antes de cualquier otra cosa
# ═══════════════════════════════════════════════════════════
@st.cache_data(ttl=30)
def cargar_datos():
    url = "https://docs.google.com/spreadsheets/d/1HdQ0uLeISE-8fdFdyNNu9M5tZu4Ydl17nMdo1M-uXv4/export?format=csv&gid=923584266"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, allow_redirects=True)
    r.raise_for_status()
    df = pd.read_csv(StringIO(r.text), encoding="utf-8", header=0)
    # Strip espacios en nombres de columnas
    df.columns = df.columns.str.strip()
    return df

df = cargar_datos()
COLS = list(df.columns)  # lista real de columnas

# ═══════════════════════════════════════════════════════════
# INSPECTOR SIEMPRE VISIBLE AL INICIO (para debug)
# Cuando todo funcione, cambia expanded=True a False
# ═══════════════════════════════════════════════════════════
with st.expander("🔧 Inspector de columnas reales del Sheet", expanded=False):
    st.write(f"**Total columnas: {len(COLS)}**")
    for i, c in enumerate(COLS):
        st.write(f"`{i:02d}` → `{repr(c)}`")

# ═══════════════════════════════════════════════════════════
# DETECCIÓN AUTOMÁTICA DE LA COLUMNA "TIPO DE EVALUACIÓN"
# Busca por contenido parcial para ser tolerante a variaciones
# ═══════════════════════════════════════════════════════════
def detectar_col(keywords_obligatorias, keywords_excluir=None):
    """Encuentra la primera columna que contenga todas las keywords."""
    for col in COLS:
        col_l = col.lower()
        if all(kw.lower() in col_l for kw in keywords_obligatorias):
            if keywords_excluir and any(kw.lower() in col_l for kw in keywords_excluir):
                continue
            return col
    return None

col_nombre   = detectar_col(["nombre", "paciente"])
col_rut      = detectar_col(["rut"])
col_tipo     = detectar_col(["tipo", "evaluación"]) or detectar_col(["tipo", "evaluacion"])
col_edad     = detectar_col(["edad"])
col_diag     = detectar_col(["diagnóstico"]) or detectar_col(["diagnostico"])
col_medico   = detectar_col(["médico"]) or detectar_col(["medico"])
col_kine     = detectar_col(["kinesiólogo"]) or detectar_col(["kinesiologo"])
col_contacto = detectar_col(["contacto"])
col_vis_med  = detectar_col(["visita", "médico"]) or detectar_col(["visita", "medico"])
col_licencia = detectar_col(["licencia"])

# Validar columnas críticas
if not col_nombre or not col_rut or not col_tipo:
    st.error(f"""
    ❌ No se encontraron columnas clave.
    - col_nombre detectada: `{col_nombre}`
    - col_rut detectada: `{col_rut}`
    - col_tipo detectada: `{col_tipo}`
    
    Revisa el inspector de columnas arriba.
    """)
    st.stop()

# ═══════════════════════════════════════════════════════════
# MAPEO EXACTO POR POSICIÓN (índice) — más robusto que por nombre
# Usa los índices según el orden real del Sheet
# ═══════════════════════════════════════════════════════════
def col_por_indice(idx, default="__missing__"):
    """Retorna nombre de columna por índice; default si no existe."""
    if idx < len(COLS):
        return COLS[idx]
    return default

# Construir C usando detección auto + fallback por índice
# Los índices corresponden al orden que me compartiste
C = {
    "nombre":        col_nombre,
    "rut":           col_rut,
    "edad":          col_edad          or col_por_indice(2),
    "tipo_eval":     col_tipo,
    "diagnostico":   col_diag          or col_por_indice(4),
    "medico":        col_medico        or col_por_indice(5),
    "kinesiologo":   col_kine          or col_por_indice(6),
    "contacto":      col_contacto      or col_por_indice(7),
    "visita_medico": col_vis_med       or col_por_indice(8),
    "inicio_lic":    col_licencia      or col_por_indice(9),

    # EVALUACIÓN INICIAL (índices 10–23)
    "fecha_ini":     col_por_indice(10),
    "dolor_ini":     col_por_indice(11),
    "rom_ini":       col_por_indice(12),
    "core_ini":      col_por_indice(13),
    "groc_ini":      col_por_indice(14),
    "pilares_ini":   col_por_indice(15),
    "p1_ini":        col_por_indice(16),
    "p2_ini":        col_por_indice(17),
    "p3_ini":        col_por_indice(18),
    "p4_ini":        col_por_indice(19),
    "p5_ini":        col_por_indice(20),
    "p6_ini":        col_por_indice(21),
    "hogar_ini":     col_por_indice(22),
    "notas_ini":     col_por_indice(23),

    # SESIÓN HITO (índices 24–38)
    "fecha_hito":    col_por_indice(24),
    "dolor_hito":    col_por_indice(25),
    "rom_hito":      col_por_indice(26),
    "core_hito":     col_por_indice(27),
    "groc_hito":     col_por_indice(28),
    "pilares_hito":  col_por_indice(29),
    "p1_hito":       col_por_indice(30),
    "p2_hito":       col_por_indice(31),
    "p3_hito":       col_por_indice(32),
    "p4_hito":       col_por_indice(33),
    "p5_hito":       col_por_indice(34),
    "p6_hito":       col_por_indice(35),
    "hogar_hito":    col_por_indice(36),
    "decision":      col_por_indice(37),
    "notas_hito":    col_por_indice(38),

    # EVALUACIÓN FINAL (índices 39–53)
    "fecha_final":   col_por_indice(39),
    "dolor_final":   col_por_indice(40),
    "rom_final":     col_por_indice(41),
    "core_final":    col_por_indice(42),
    "groc_final":    col_por_indice(43),
    "pilares_final": col_por_indice(44),
    "p1_final":      col_por_indice(45),
    "p2_final":      col_por_indice(46),
    "p3_final":      col_por_indice(47),
    "p4_final":      col_por_indice(48),
    "p5_final":      col_por_indice(49),
    "p6_final":      col_por_indice(50),
    "hogar_final":   col_por_indice(51),
    "notas_final":   col_por_indice(52),
    "motivo_alta":   col_por_indice(53),
}

PILARES = ["Sedentarismo", "Sueño", "Estrés", "Alimentación", "Tóxicos", "Relaciones"]

# ═══════════════════════════════════════════════════════════
# FUNCIÓN DE EXTRACCIÓN SEGURA
# ═══════════════════════════════════════════════════════════
def g(fila, key, default="—"):
    if fila is None:
        return default
    col_name = C.get(key, "__missing__")
    if col_name == "__missing__" or col_name not in fila.index:
        return default
    val = fila[col_name]
    if pd.isna(val) or str(val).strip() in ("", "nan"):
        return default
    return str(val).strip()

# ═══════════════════════════════════════════════════════════
# SIDEBAR — Selección de paciente por RUT
# ═══════════════════════════════════════════════════════════
st.sidebar.image(
    "https://raw.githubusercontent.com/espdemoelectivo-max/delphi-reporte-dinamico-2/main/Delphi Logo.png",
    use_container_width=True
)
st.sidebar.title("Gestión Delphi")

pacientes = (
    df[[C["nombre"], C["rut"]]]
    .dropna(subset=[C["rut"]])
    .drop_duplicates(subset=[C["rut"]])
    .reset_index(drop=True)
)
pacientes["display"] = (
    pacientes[C["nombre"]].str.strip() + "  |  RUT: " + pacientes[C["rut"]].str.strip()
)

opcion     = st.sidebar.selectbox("Seleccionar Paciente:", pacientes["display"].tolist())
rut_sel    = pacientes.loc[pacientes["display"] == opcion, C["rut"]].values[0].strip()
nombre_sel = pacientes.loc[pacientes["display"] == opcion, C["nombre"]].values[0].strip()

# Todas las filas del paciente (por RUT)
filas = df[df[C["rut"]].astype(str).str.strip() == rut_sel]

# Separar por tipo de evaluación
def ultima_fila(keyword):
    mask = filas[C["tipo_eval"]].astype(str).str.contains(keyword, case=False, na=False)
    sub  = filas[mask]
    return sub.iloc[-1] if not sub.empty else None

fila_ini   = ultima_fila("Inicial")
fila_hito  = ultima_fila("Hito")
fila_final = ultima_fila("Final")

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
# INFO PERSONAL
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
# PILARES
# ═══════════════════════════════════════════════════════════
def mostrar_pilares(fila, sufijo):
    pilares_raw    = g(fila, f"pilares_{sufijo}", "")
    pilares_activos = [n for n in PILARES if n.lower() in pilares_raw.lower()] if pilares_raw != "—" else []

    st.markdown("<p style='color:#1E2D6B; font-weight:700; font-size:15px; margin-top:16px;'>🧩 DIRECTRIZ: PILARES DE SALUD ABORDADOS</p>", unsafe_allow_html=True)
    col_tabs_ui, col_hogar_ui = st.columns([3, 1])

    with col_tabs_ui:
        tab_labels = [f"✅ {n}" if n in pilares_activos else f"○ {n}" for n in PILARES]
        tabs = st.tabs(tab_labels)
        claves = [f"p1_{sufijo}", f"p2_{sufijo}", f"p3_{sufijo}",
                  f"p4_{sufijo}", f"p5_{sufijo}", f"p6_{sufijo}"]
        for tab, nombre, clave in zip(tabs, PILARES, claves):
            with tab:
                rec = g(fila, clave, "Sin indicaciones registradas")
                if nombre in pilares_activos:
                    st.markdown(f"""
                        <div style="background:#e8eaf6;padding:18px;border-radius:10px;border-left:6px solid #E0157A;">
                            <p style="margin:0;font-size:0.82em;font-weight:700;color:#E0157A;text-transform:uppercase;letter-spacing:1px;">✅ ABORDADO EN SESIÓN</p>
                            <p style="margin:8px 0 0 0;font-size:1.08em;color:#1E2D6B;font-weight:600;">{rec}</p>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style="background:#f7f7f7;padding:18px;border-radius:10px;border-left:6px solid #ccc;">
                            <p style="margin:0;font-size:0.82em;color:#bbb;text-transform:uppercase;letter-spacing:1px;">No abordado</p>
                            <p style="margin:8px 0 0 0;font-size:1.05em;color:#aaa;">{rec}</p>
                        </div>""", unsafe_allow_html=True)

    with col_hogar_ui:
        rec_hogar = g(fila, f"hogar_{sufijo}")
        st.markdown(f"""
            <div class="hogar-card">
                <h4 style="color:#1E2D6B;margin-top:0;">🏠 Recomendación para el hogar</h4>
                <p style="font-size:1em;margin:0;">{rec_hogar}</p>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# BLOQUE CLÍNICO
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
            <div style="text-align:center;padding:20px;border:2px solid #E0157A;border-radius:10px;background:#fff0f7;">
                <span style="font-size:40px;font-weight:bold;color:#E0157A;">{g(fila, f"groc_{sufijo}")}</span><br>
                <small style="color:#9B9B9B;">Puntaje de Cambio Percibido</small>
            </div>""", unsafe_allow_html=True)

    mostrar_pilares(fila, sufijo)

    notas = g(fila, f"notas_{sufijo}")
    if notas != "—":
        st.warning(f"**📋 NOTAS PARA EL MÉDICO TRATANTE:** {notas}")

# ═══════════════════════════════════════════════════════════
# RENDER
# ═══════════════════════════════════════════════════════════
bloque_clinico("📋 EVALUACIÓN INICIAL",               fila_ini,   "ini")
st.divider()
bloque_clinico("🔁 SESIÓN HITO (CONTROL DE AVANCE)",  fila_hito,  "hito",  is_hito=True)
st.divider()
bloque_clinico("✅ EVALUACIÓN FINAL Y ALTA",           fila_final, "final", is_final=True)
