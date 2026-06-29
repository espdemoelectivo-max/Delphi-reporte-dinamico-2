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

# ── CARGA DE DATOS ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def cargar_datos():
    url = "https://docs.google.com/spreadsheets/d/1HdQ0uLeISE-8fdFdyNNu9M5tZu4Ydl17nMdo1M-uXv4/export?format=csv&gid=923584266"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, allow_redirects=True)
    response.raise_for_status()
    data = pd.read_csv(StringIO(response.text), encoding="utf-8", header=0)
    data.columns = data.columns.str.strip()
    return data

df = cargar_datos()

# ── DETECCIÓN DE COLUMNAS CLAVE ────────────────────────────────────────────────
# Muestra las columnas en sidebar para debug (puedes comentarlo luego)
with st.sidebar.expander("🔧 Columnas detectadas (debug)", expanded=False):
    st.write(list(df.columns))

# Detectar columna de nombre y tipo de evaluación dinámicamente
col_nombre = next((c for c in df.columns if "nombre" in c.lower()), None)
col_tipo   = next((c for c in df.columns if "tipo" in c.lower() and "eval" in c.lower()), None)
col_rut    = next((c for c in df.columns if "rut" in c.lower()), None)

if not col_nombre or not col_tipo or not col_rut:
    st.error(f"No se encontraron columnas clave. Columnas disponibles: {list(df.columns)}")
    st.stop()

# ── FUNCIÓN DE EXTRACCIÓN SEGURA ───────────────────────────────────────────────
def get_val(row, col_name, default="—"):
    """Extrae un valor de una fila (Series) de forma segura."""
    if row is None:
        return default
    if col_name not in row.index:
        return default
    val = row[col_name]
    if pd.isna(val) or str(val).strip() in ("", "nan"):
        return default
    return str(val).strip()

# ── BÚSQUEDA DE COLUMNA POR KEYWORD ───────────────────────────────────────────
def find_col(columns, *keywords):
    """Busca una columna que contenga todas las keywords (case-insensitive)."""
    for col in columns:
        col_lower = col.lower()
        if all(kw.lower() in col_lower for kw in keywords):
            return col
    return None

cols = list(df.columns)

# ── SIDEBAR: SELECCIÓN POR NOMBRE + RUT ───────────────────────────────────────
st.sidebar.image(
    "https://raw.githubusercontent.com/espdemoelectivo-max/delphi-reporte-dinamico-2/main/Delphi Logo.png",
    use_container_width=True
)
st.sidebar.title("Gestión Delphi")

# Construir lista de pacientes únicos por RUT (tomamos el nombre de la primera aparición)
pacientes_df = (
    df[[col_nombre, col_rut]]
    .dropna(subset=[col_rut])
    .drop_duplicates(subset=[col_rut])
    .reset_index(drop=True)
)
pacientes_df["display"] = pacientes_df[col_nombre].str.strip() + "  |  RUT: " + pacientes_df[col_rut].str.strip()

opcion = st.sidebar.selectbox("Seleccionar Paciente:", pacientes_df["display"].tolist())
rut_seleccionado = pacientes_df.loc[pacientes_df["display"] == opcion, col_rut].values[0]
nombre_seleccionado = pacientes_df.loc[pacientes_df["display"] == opcion, col_nombre].values[0]

# ── FILTRAR TODAS LAS FILAS DEL PACIENTE POR RUT ──────────────────────────────
filas_paciente = df[df[col_rut].astype(str).str.strip() == str(rut_seleccionado).strip()]

# Separar por tipo de evaluación (flexible, acepta variaciones de texto)
def filtrar_tipo(df_p, keyword):
    mask = df_p[col_tipo].astype(str).str.contains(keyword, case=False, na=False)
    resultado = df_p[mask]
    return resultado.iloc[-1] if not resultado.empty else None  # última fila de ese tipo

fila_inicial = filtrar_tipo(filas_paciente, "Inicial")
fila_hito    = filtrar_tipo(filas_paciente, "Hito")
fila_final   = filtrar_tipo(filas_paciente, "Final")

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
    <div class="report-header">
        <h1 style="color:white; margin-bottom:0; letter-spacing:2px;">CENTRO CLÍNICO DELPHI</h1>
        <p style="color:#E0157A; font-size:1.1em; font-weight:600; margin:4px 0;">Reporte Kinesiológico Estandarizado</p>
        <h3 style="color:#f0f0f0; margin-top:6px;">PACIENTE: {nombre_seleccionado.upper()}</h3>
    </div>""", unsafe_allow_html=True)

# ── INFO PERSONAL (desde fila_inicial o cualquier fila disponible) ─────────────
# Usar la primera fila disponible para datos demográficos
fila_demo = fila_inicial if fila_inicial is not None else (fila_hito if fila_hito is not None else fila_final)

col_diag   = find_col(cols, "diagnóstico") or find_col(cols, "diagnostico")
col_medico = find_col(cols, "médico") or find_col(cols, "medico")
col_kine   = find_col(cols, "kinesiólogo") or find_col(cols, "kinesiologo")
col_cont   = find_col(cols, "contacto")
col_edad   = find_col(cols, "edad")
col_vis_med= find_col(cols, "visita", "médico") or find_col(cols, "visita", "medico")
col_lic    = find_col(cols, "licencia")

ca, cb, cc = st.columns(3)
with ca:
    st.markdown(f"""<div class="info-box">
        <b style="color:#1E2D6B;">Paciente:</b> {nombre_seleccionado}<br>
        <b style="color:#1E2D6B;">RUT:</b> {rut_seleccionado}<br>
        <b style="color:#1E2D6B;">Edad:</b> {get_val(fila_demo, col_edad)} años
    </div>""", unsafe_allow_html=True)
with cb:
    st.markdown(f"""<div class="info-box">
        <b style="color:#1E2D6B;">Diagnóstico:</b><br>{get_val(fila_demo, col_diag)}<br>
        <b style="color:#1E2D6B;">Visita Médico:</b> {get_val(fila_demo, col_vis_med)}
    </div>""", unsafe_allow_html=True)
with cc:
    st.markdown(f"""<div class="info-box">
        <b style="color:#1E2D6B;">Médico:</b> {get_val(fila_demo, col_medico)}<br>
        <b style="color:#1E2D6B;">Kinesiólogo:</b> {get_val(fila_demo, col_kine)}<br>
        <b style="color:#1E2D6B;">Contacto:</b> {get_val(fila_demo, col_cont)}
    </div>""", unsafe_allow_html=True)

# ── CRONOLOGÍA ────────────────────────────────────────────────────────────────
st.write("")
st.markdown("<p style='color:#1E2D6B; font-weight:700; font-size:15px;'>📅 CRONOLOGÍA DEL TRATAMIENTO</p>", unsafe_allow_html=True)

col_eval_ini_f  = find_col(cols, "evaluación inicial") or find_col(cols, "evaluacion inicial")
col_sesion_hito = find_col(cols, "sesión hito") or find_col(cols, "sesion hito")
col_eval_fin_f  = find_col(cols, "evaluación final") or find_col(cols, "evaluacion final")

d1,d2,d3,d4,d5,d6 = st.columns(6)
fechas = [
    ("Visita Médico",   get_val(fila_demo, col_vis_med)),
    ("Inicio Licencia", get_val(fila_inicial, col_lic)),
    ("Eval. Inicial",   get_val(fila_inicial, col_eval_ini_f)),
    ("1º Sesión Kine",  "—"),
    ("Hito (Sesión 6)", get_val(fila_hito, col_sesion_hito)),
    ("Eval. Final",     get_val(fila_final, col_eval_fin_f)),
]
for col_ui, (label, date) in zip([d1,d2,d3,d4,d5,d6], fechas):
    col_ui.markdown(f"""<div class="date-box">
        <small style="color:#9B9B9B; font-weight:600;">{label}</small><br>
        <b style="color:#1E2D6B;">{date}</b>
    </div>""", unsafe_allow_html=True)

st.divider()

# ── PILARES ───────────────────────────────────────────────────────────────────
PILARES_NOMBRES = ["Sedentarismo", "Sueño", "Estrés", "Alimentación", "Tóxicos", "Relaciones"]

def encontrar_col_pilar(cols, nombre_pilar, sufijo_extra=""):
    """Busca la columna de un pilar específico, con sufijo opcional para hito/final."""
    for c in cols:
        if nombre_pilar.lower() in c.lower() and "pilar" in c.lower():
            if sufijo_extra == "" or sufijo_extra in c:
                return c
    return None

def mostrar_pilares(fila, sufijo_cols=""):
    """
    sufijo_cols: "" para inicial, ".1" para hito, ".2" para final
    (así maneja los nombres duplicados que pandas auto-renombra con .1 .2)
    """
    if fila is None:
        return

    # Buscar columna de checkboxes de pilares abordados
    col_checkbox = None
    for c in cols:
        if "pilares abordados" in c.lower() or ("marcar" in c.lower() and "pilar" in c.lower()):
            if sufijo_cols == "" and not c.endswith(".1") and not c.endswith(".2"):
                col_checkbox = c
                break
            elif sufijo_cols and c.endswith(sufijo_cols):
                col_checkbox = c
                break

    pilares_raw = get_val(fila, col_checkbox, "")
    pilares_activos = [n for n in PILARES_NOMBRES if n.lower() in pilares_raw.lower()] if pilares_raw != "—" else []

    # Buscar columna de recomendación para el hogar
    col_hogar = None
    for c in cols:
        if "recomendación para el hogar" in c.lower() or "recomendacion para el hogar" in c.lower():
            if sufijo_cols == "" and not c.endswith(".1") and not c.endswith(".2") and not c.endswith(" "):
                col_hogar = c
                break
            elif sufijo_cols and c.endswith(sufijo_cols):
                col_hogar = c
                break
    # fallback: tomar la primera que matchee
    if not col_hogar:
        col_hogar = next((c for c in cols if "recomendación para el hogar" in c.lower() or "recomendacion para el hogar" in c.lower()), None)

    st.markdown("<p style='color:#1E2D6B; font-weight:700; font-size:15px; margin-top:16px;'>🧩 DIRECTRIZ: PILARES DE SALUD ABORDADOS</p>", unsafe_allow_html=True)
    col_tabs_ui, col_hogar_ui = st.columns([3, 1])

    with col_tabs_ui:
        tab_labels = [f"✅ {n}" if n in pilares_activos else f"○ {n}" for n in PILARES_NOMBRES]
        tabs = st.tabs(tab_labels)

        for tab, nombre in zip(tabs, PILARES_NOMBRES):
            with tab:
                # Buscar columna del pilar específico
                col_p = None
                for c in cols:
                    if nombre.lower() in c.lower() and "pilar" in c.lower():
                        if sufijo_cols == "" and not c.endswith(".1") and not c.endswith(".2"):
                            col_p = c
                            break
                        elif sufijo_cols and c.endswith(sufijo_cols):
                            col_p = c
                            break

                recomendacion = get_val(fila, col_p, "Sin indicaciones registradas")

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
        rec_hogar = get_val(fila, col_hogar, "Sin indicaciones")
        st.markdown(f"""
            <div class="hogar-card">
                <h4 style="color:#1E2D6B; margin-top:0;">🏠 Recomendación para el hogar</h4>
                <p style="font-size:1em; margin:0;">{rec_hogar}</p>
            </div>""", unsafe_allow_html=True)


# ── FUNCIÓN DE BLOQUE CLÍNICO ──────────────────────────────────────────────────
def bloque_clinico(titulo, fila, sufijo_cols="", is_hito=False, is_final=False):
    st.markdown(f"<h3 class='section-title'>{titulo}</h3>", unsafe_allow_html=True)

    if fila is None:
        st.info("⏳ Estado: Pendiente — aún no registrada en el sistema.")
        return

    # Buscar columnas de métricas con sufijo
    def fc(*keywords):
        """Encuentra columna por keywords, respetando sufijo."""
        for c in cols:
            c_lower = c.lower()
            if all(kw.lower() in c_lower for kw in keywords):
                if sufijo_cols == "" and not c.endswith(".1") and not c.endswith(".2"):
                    return c
                elif sufijo_cols and c.endswith(sufijo_cols):
                    return c
        return None

    col_dolor = fc("dolor", "eva") or fc("dolor")
    col_rom   = fc("rango", "movimiento") or fc("rom")
    col_core  = fc("fuerza", "core") or fc("core")
    col_groc  = fc("groc")
    col_notas = fc("notas", "médico") or fc("notas", "medico") or fc("notas")
    col_dec   = fc("decisión") or fc("decision")
    col_alta  = fc("motivo", "alta")

    col_eval_c, col_groc_c = st.columns([2, 1])
    with col_eval_c:
        st.subheader("Evaluación Clínica")
        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<p class="metric-title">DOLOR (EVA)</p><p class="metric-value">{get_val(fila, col_dolor)}</p>', unsafe_allow_html=True)
        m2.markdown(f'<p class="metric-title">RANGO MOV.</p><p class="metric-value">{get_val(fila, col_rom)}</p>',   unsafe_allow_html=True)
        m3.markdown(f'<p class="metric-title">FUERZA CORE</p><p class="metric-value">{get_val(fila, col_core)}</p>', unsafe_allow_html=True)
        if is_hito:
            st.info(f"**Decisión Clínica (M-A-R):** {get_val(fila, col_dec)}")
        if is_final:
            st.success(f"**Motivo de Alta:** {get_val(fila, col_alta)}")
    with col_groc_c:
        st.subheader("GROC")
        st.markdown(f"""
            <div style="text-align:center; padding:20px; border:2px solid #E0157A; border-radius:10px; background:#fff0f7;">
                <span style="font-size:40px; font-weight:bold; color:#E0157A;">{get_val(fila, col_groc)}</span><br>
                <small style="color:#9B9B9B;">Puntaje de Cambio Percibido</small>
            </div>""", unsafe_allow_html=True)

    mostrar_pilares(fila, sufijo_cols)

    notas_val = get_val(fila, col_notas)
    if notas_val != "—":
        st.warning(f"**📋 NOTAS PARA EL MÉDICO TRATANTE:** {notas_val}")


# ── RENDERIZADO DE BLOQUES ─────────────────────────────────────────────────────
bloque_clinico("📋 EVALUACIÓN INICIAL",              fila_inicial, sufijo_cols="",   is_hito=False, is_final=False)
st.divider()
bloque_clinico("🔁 SESIÓN HITO (CONTROL DE AVANCE)", fila_hito,    sufijo_cols=".1", is_hito=True,  is_final=False)
st.divider()
bloque_clinico("✅ EVALUACIÓN FINAL Y ALTA",          fila_final,   sufijo_cols=".2", is_hito=False, is_final=True)

# ── FOOTER DEBUG: mostrar columnas detectadas para ajuste fino ─────────────────
with st.expander("🔧 Inspector de columnas (para ajuste)", expanded=False):
    st.write("**Columnas del Google Sheet:**")
    for i, c in enumerate(cols):
        st.write(f"`{i}`: {c}")
