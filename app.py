import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO

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
# CARGA DE DATOS — forzar UTF-8 con BOM y latin1 como fallback
# ═══════════════════════════════════════════════════════════
@st.cache_data(ttl=30)
def cargar_datos():
    url = "https://docs.google.com/spreadsheets/d/1HdQ0uLeISE-8fdFdyNNu9M5tZu4Ydl17nMdo1M-uXv4/export?format=csv&gid=923584266"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, allow_redirects=True)
    r.raise_for_status()
    # Intentar encodings en orden hasta que funcionen los acentos
    raw = r.content
    for enc in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            text = raw.decode(enc)
            df = pd.read_csv(StringIO(text), header=0)
            # Verificar que los acentos estén bien (sin Ã)
            sample = " ".join(df.columns.tolist())
            if "Ã" not in sample:
                df.columns = df.columns.str.strip()
                return df
        except Exception:
            continue
    # Último recurso
    df = pd.read_csv(BytesIO(raw), encoding="latin-1", header=0)
    df.columns = df.columns.str.strip()
    return df

df   = cargar_datos()
COLS = list(df.columns)

# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════
def ci(idx):
    """Columna por índice absoluto (contando Marca temporal en 0)."""
    return COLS[idx] if idx < len(COLS) else "__missing__"

# ═══════════════════════════════════════════════════════════
# MAPEO EXACTO POR ÍNDICE
# 00 = Marca temporal  (oculta, no se usa)
# 01 = Nombre del Paciente
# 02 = Rut
# 03 = Edad
# 04 = Tipo de Evaluación a registrar
# 05 = Diagnóstico médico
# 06 = Médico
# 07 = Kinesiólogo
# 08 = Contacto
# 09 = Visita Médico
# 10 = Inicio licencia
# 11 = Evaluación inicial (fecha)
# 12 = Dolor EVA inicial
# 13 = Rango de Movimiento (ROM)
# 14 = Fuerza CORE
# 15 = Groc inicial
# 16 = (Marcar los pilares abordados en la sesión):
# 17 = Pilar 1 - Sedentarismo
# 18 = Pilar 2 - Sueño
# 19 = Pilar 3 - Estrés
# 20 = Pilar 4 - Alimentación
# 21 = Pilar 5 - Tóxicos
# 22 = Pilar 6 - Relaciones
# 23 = Recomendación para el hogar
# 24 = Notas para el médico tratante:
# 25 = Sesión hito (fecha)
# 26 = Dolor EVA Actual
# 27 = Rango de Movimiento (ROM).1
# 28 = Fuerza CORE.1
# 29 = Groc Sesión Hito
# 30 = (Marcar los pilares abordados en la sesión):.1
# 31 = Pilar 1 - Sedentarismo.1
# 32 = Pilar 2 - Sueño.1
# 33 = Pilar 3 - Estrés.1
# 34 = Pilar 4 - Alimentación.1
# 35 = Pilar 5 - Tóxicos.1
# 36 = Pilar 6 - Relaciones.1
# 37 = Recomendación para el hogar (pilares seleccionados)
# 38 = Decisión Clínica (Hito Intermedio):
# 39 = Notas para el médico tratante:.1
# 40 = Evaluación Final (fecha)
# 41 = Dolor EVA Actual.1
# 42 = Rango de Movimiento (ROM).2
# 43 = Fuerza CORE.2
# 44 = Groc Evaluación Final
# 45 = (Marcar los pilares abordados en la sesión):.2
# 46 = Pilar 1 - Sedentarismo.2
# 47 = Pilar 2 - Sueño.2
# 48 = Pilar 3 - Estrés.2
# 49 = Pilar 4 - Alimentación.2
# 50 = Pilar 5 - Tóxicos.2
# 51 = Pilar 6 - Relaciones.2
# 52 = Recomendación para el hogar (pilares seleccionados).1
# 53 = Notas para el médico tratante:.2
# 54 = Motivo del Alta
# ═══════════════════════════════════════════════════════════
C = {
    "nombre":        ci(1),
    "rut":           ci(2),
    "edad":          ci(3),
    "tipo_eval":     ci(4),
    "diagnostico":   ci(5),
    "medico":        ci(6),
    "kinesiologo":   ci(7),
    "contacto":      ci(8),
    "visita_medico": ci(9),
    "inicio_lic":    ci(10),
    # EVALUACIÓN INICIAL
    "fecha_ini":     ci(11),
    "dolor_ini":     ci(12),
    "rom_ini":       ci(13),
    "core_ini":      ci(14),
    "groc_ini":      ci(15),
    "pilares_ini":   ci(16),
    "p1_ini":        ci(17),
    "p2_ini":        ci(18),
    "p3_ini":        ci(19),
    "p4_ini":        ci(20),
    "p5_ini":        ci(21),
    "p6_ini":        ci(22),
    "hogar_ini":     ci(23),
    "notas_ini":     ci(24),
    # SESIÓN HITO
    "fecha_hito":    ci(25),
    "dolor_hito":    ci(26),
    "rom_hito":      ci(27),
    "core_hito":     ci(28),
    "groc_hito":     ci(29),
    "pilares_hito":  ci(30),
    "p1_hito":       ci(31),
    "p2_hito":       ci(32),
    "p3_hito":       ci(33),
    "p4_hito":       ci(34),
    "p5_hito":       ci(35),
    "p6_hito":       ci(36),
    "hogar_hito":    ci(37),
    "decision":      ci(38),
    "notas_hito":    ci(39),
    # EVALUACIÓN FINAL
    "fecha_final":   ci(40),
    "dolor_final":   ci(41),
    "rom_final":     ci(42),
    "core_final":    ci(43),
    "groc_final":    ci(44),
    "pilares_final": ci(45),
    "p1_final":      ci(46),
    "p2_final":      ci(47),
    "p3_final":      ci(48),
    "p4_final":      ci(49),
    "p5_final":      ci(50),
    "p6_final":      ci(51),
    "hogar_final":   ci(52),
    "notas_final":   ci(53),
    "motivo_alta":   ci(54),
}

PILARES = ["Sedentarismo", "Sueño", "Estrés", "Alimentación", "Tóxicos", "Relaciones"]

# ═══════════════════════════════════════════════════════════
# EXTRACCIÓN SEGURA
# ═══════════════════════════════════════════════════════════
def g(fila, key, default="—"):
    if fila is None:
        return default
    col_name = C.get(key, "__missing__")
    if col_name == "__missing__" or col_name not in fila.index:
        return default
    val = fila[col_name]
    if isinstance(val, pd.Series):
        val = val.iloc[0] if not val.empty else None
    try:
        if pd.isna(val):
            return default
    except (TypeError, ValueError):
        pass
    if str(val).strip() in ("", "nan"):
        return default
    return str(val).strip()

# ═══════════════════════════════════════════════════════════
# SIDEBAR
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

# Todas las filas del paciente por RUT
filas = df[df[C["rut"]].astype(str).str.strip() == rut_sel]

def ultima_fila(keyword):
    mask = filas[C["tipo_eval"]].astype(str).str.contains(keyword, case=False, na=False)
    sub  = filas[mask]
    return sub.iloc[-1] if not sub.empty else None

fila_ini   = ultima_fila("Inicial")
fila_hito  = ultima_fila("Hito")
fila_final = ultima_fila("Final")
fila_demo  = next((f for f in [fila_ini, fila_hito, fila_final] if f is not None), None)

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
    pilares_raw     = g(fila, f"pilares_{sufijo}", "")
    pilares_activos = [n for n in PILARES if n.lower() in pilares_raw.lower()] if pilares_raw != "—" else []

    st.markdown("<p style='color:#1E2D6B; font-weight:700; font-size:15px; margin-top:16px;'>🧩 DIRECTRIZ: PILARES DE SALUD ABORDADOS</p>", unsafe_allow_html=True)
    col_tabs_ui, col_hogar_ui = st.columns([3, 1])

    with col_tabs_ui:
        tab_labels = [f"🔴 {n}" if n in pilares_activos else f"🟢 {n}" for n in PILARES]
        tabs = st.tabs(tab_labels)
        claves = [f"p{i+1}_{sufijo}" for i in range(6)]
        for tab, nombre, clave in zip(tabs, PILARES, claves):
            with tab:
                rec = g(fila, clave, "Sin indicaciones registradas")
                if nombre in pilares_activos:
                    st.markdown(f"""
                        <div style="background:#e8eaf6;padding:18px;border-radius:10px;border-left:6px solid #E0157A;">
                            <p style="margin:0;font-size:0.82em;font-weight:700;color:#E0157A;text-transform:uppercase;">PILAR ABORDADO EN SESIÓN</p>
                            <p style="margin:8px 0 0 0;font-size:1.08em;color:#1E2D6B;font-weight:600;">{rec}</p>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style="background:#f7f7f7;padding:18px;border-radius:10px;border-left:6px solid #ccc;">
                            <p style="margin:0;font-size:0.82em;color:#bbb;text-transform:uppercase;">No abordado</p>
                            <p style="margin:8px 0 0 0;font-size:1.05em;color:#aaa;">{rec}</p>
                        </div>""", unsafe_allow_html=True)

    with col_hogar_ui:
        st.markdown(f"""
            <div class="hogar-card">
                <h4 style="color:#1E2D6B;margin-top:0;">🏠 Recomendación para el hogar</h4>
                <p style="font-size:1em;margin:0;">{g(fila, f"hogar_{sufijo}")}</p>
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
        st.warning(f"**📋 NOTAS:** {notas}")

# ═══════════════════════════════════════════════════════════
# RENDER
# ═══════════════════════════════════════════════════════════
bloque_clinico(" EVALUACIÓN INICIAL",               fila_ini,   "ini")
st.divider()
bloque_clinico(" SESIÓN HITO (CONTROL DE AVANCE)",  fila_hito,  "hito",  is_hito=True)
st.divider()
bloque_clinico(" EVALUACIÓN FINAL",           fila_final, "final", is_final=True)

# ═══════════════════════════════════════════════════════════

