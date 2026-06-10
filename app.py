import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import os
from datetime import datetime

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="PasaLosRamos 🎓",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS personalizado ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Inter:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
h1, h2, h3, .stTabs [data-baseweb="tab"] {
    font-family: 'Space Grotesk', sans-serif !important;
}

.stApp { background: #0f1117; }

.titulo-app {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #6c63ff, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.subtitulo-app {
    color: #8b8fa8;
    font-size: .9rem;
    margin-bottom: 1.5rem;
}

.nota-card {
    background: #1a1d27;
    border: 1px solid #2e3350;
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}

.auth-card {
    background: #1a1d27;
    border: 1px solid #2e3350;
    border-radius: 18px;
    padding: 2rem 2.5rem;
    margin: 2rem auto;
    max-width: 420px;
}

.user-badge {
    background: #6c63ff22;
    border: 1px solid #6c63ff55;
    border-radius: 10px;
    padding: 0.4rem 0.9rem;
    color: #a78bfa;
    font-size: .85rem;
    font-weight: 600;
    display: inline-block;
}

.historial-card {
    background: #1a1d27;
    border: 1px solid #2e3350;
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
}

.ramo-header {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #a78bfa;
}

.semestre-badge {
    background: #6c63ff33;
    border-radius: 8px;
    padding: 2px 10px;
    color: #a78bfa;
    font-size: .78rem;
    font-weight: 600;
}

.res-aprobado {
    background: #34d39912;
    border: 2px solid #34d399;
    border-radius: 14px;
    padding: 1.5rem;
    text-align: center;
}
.res-examen {
    background: #fbbf2412;
    border: 2px solid #fbbf24;
    border-radius: 14px;
    padding: 1.5rem;
    text-align: center;
}
.res-reprobado {
    background: #f8717112;
    border: 2px solid #f87171;
    border-radius: 14px;
    padding: 1.5rem;
    text-align: center;
}
.nota-grande {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3.5rem;
    font-weight: 700;
    line-height: 1;
}
.badge-ok   { color: #34d399; font-weight: 700; }
.badge-warn { color: #fbbf24; font-weight: 700; }
.badge-bad  { color: #f87171; font-weight: 700; }

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #1a1d27;
    border-radius: 12px;
    padding: 6px;
    border: 1px solid #2e3350;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #8b8fa8 !important;
    font-weight: 600 !important;
    font-size: .88rem !important;
    padding: .5rem 1rem !important;
}
.stTabs [aria-selected="true"] {
    background: #6c63ff !important;
    color: #fff !important;
}

div[data-testid="stForm"] {
    background: transparent;
    border: none;
}
</style>
""", unsafe_allow_html=True)


# ── Base de datos SQLite ─────────────────────────────────────────────────────
DB_PATH = "pasalosramos.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            carrera TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS ramos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            semestre TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ramo_id INTEGER NOT NULL,
            descripcion TEXT,
            nota REAL NOT NULL,
            ponderacion REAL NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (ramo_id) REFERENCES ramos(id)
        )
    """)
    conn.commit()
    conn.close()

init_db()


# ── Helpers de autenticación ─────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def registrar_usuario(nombre, email, password, carrera):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO usuarios (nombre, email, password_hash, carrera) VALUES (?, ?, ?, ?)",
            (nombre.strip(), email.strip().lower(), hash_password(password), carrera.strip())
        )
        conn.commit()
        return True, "Cuenta creada exitosamente."
    except sqlite3.IntegrityError:
        return False, "Ese correo ya está registrado."
    finally:
        conn.close()

def login_usuario(email, password):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM usuarios WHERE email = ? AND password_hash = ?",
        (email.strip().lower(), hash_password(password))
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# ── Helpers de ramos y notas ─────────────────────────────────────────────────
def get_ramos(usuario_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM ramos WHERE usuario_id = ? ORDER BY semestre, nombre",
        (usuario_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def crear_ramo(usuario_id, nombre, semestre):
    conn = get_conn()
    conn.execute(
        "INSERT INTO ramos (usuario_id, nombre, semestre) VALUES (?, ?, ?)",
        (usuario_id, nombre.strip(), semestre.strip())
    )
    conn.commit()
    conn.close()

def eliminar_ramo(ramo_id):
    conn = get_conn()
    conn.execute("DELETE FROM notas WHERE ramo_id = ?", (ramo_id,))
    conn.execute("DELETE FROM ramos WHERE id = ?", (ramo_id,))
    conn.commit()
    conn.close()

def get_notas(ramo_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM notas WHERE ramo_id = ? ORDER BY created_at",
        (ramo_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def guardar_notas(ramo_id, notas_list):
    """notas_list = [{'descripcion': str, 'nota': float, 'ponderacion': float}, ...]"""
    conn = get_conn()
    conn.execute("DELETE FROM notas WHERE ramo_id = ?", (ramo_id,))
    for item in notas_list:
        conn.execute(
            "INSERT INTO notas (ramo_id, descripcion, nota, ponderacion) VALUES (?, ?, ?, ?)",
            (ramo_id, item["descripcion"], item["nota"], item["ponderacion"])
        )
    conn.commit()
    conn.close()


# ── Estado de sesión ─────────────────────────────────────────────────────────
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "auth_tab" not in st.session_state:
    st.session_state.auth_tab = "login"
if "ramo_editando" not in st.session_state:
    st.session_state.ramo_editando = None


# ════════════════════════════════════════════════════════════════════════════
# PANTALLA DE AUTH (no logueado)
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.usuario is None:
    st.markdown('<div class="titulo-app">🎓 PasaLosRamos</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-app">Tu calculadora de notas universitaria</div>', unsafe_allow_html=True)

    tab_login, tab_reg = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])

    # ── Login ────────────────────────────────────────────────────────────────
    with tab_login:
        st.markdown("")
        with st.form("form_login"):
            email_l = st.text_input("Correo electrónico", placeholder="tu@correo.com")
            pass_l  = st.text_input("Contraseña", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Entrar →", use_container_width=True)

        if submitted:
            if not email_l or not pass_l:
                st.error("Completa todos los campos.")
            else:
                user = login_usuario(email_l, pass_l)
                if user:
                    st.session_state.usuario = user
                    st.rerun()
                else:
                    st.error("Correo o contraseña incorrectos.")

    # ── Registro ─────────────────────────────────────────────────────────────
    with tab_reg:
        st.markdown("")
        with st.form("form_registro"):
            nombre_r  = st.text_input("Nombre completo", placeholder="Tu nombre")
            email_r   = st.text_input("Correo electrónico", placeholder="tu@correo.com")
            carrera_r = st.text_input("Carrera universitaria", placeholder="ej: Ingeniería Civil Informática")
            pass_r    = st.text_input("Contraseña", type="password", placeholder="Mínimo 6 caracteres")
            pass_r2   = st.text_input("Repetir contraseña", type="password", placeholder="Repite tu contraseña")
            submitted_r = st.form_submit_button("Crear cuenta →", use_container_width=True)

        if submitted_r:
            if not all([nombre_r, email_r, carrera_r, pass_r, pass_r2]):
                st.error("Completa todos los campos.")
            elif len(pass_r) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres.")
            elif pass_r != pass_r2:
                st.error("Las contraseñas no coinciden.")
            else:
                ok, msg = registrar_usuario(nombre_r, email_r, pass_r, carrera_r)
                if ok:
                    st.success(msg + " Ahora inicia sesión.")
                else:
                    st.error(msg)

    st.stop()


# ════════════════════════════════════════════════════════════════════════════
# APP PRINCIPAL (logueado)
# ════════════════════════════════════════════════════════════════════════════
user = st.session_state.usuario

# Header con usuario
col_titulo, col_user = st.columns([3, 1])
with col_titulo:
    st.markdown('<div class="titulo-app">🎓 PasaLosRamos</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-app">Calculadora de notas con ponderación</div>', unsafe_allow_html=True)
with col_user:
    st.markdown(f'<div style="padding-top:1rem"><div class="user-badge">👤 {user["nombre"].split()[0]}</div></div>', unsafe_allow_html=True)
    if st.button("Salir", key="logout_btn"):
        st.session_state.usuario = None
        st.session_state.ramo_editando = None
        st.rerun()

# ── Tabs principales ─────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🧮 Mis Notas",
    "📝 ¿Voy a Examen?",
    "📚 Historial",
    "📊 Tabla de Escala",
    "➕ Calculadora Libre"
])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — MIS NOTAS
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Configuración de escala")
    col1, col2, col3 = st.columns(3)
    with col1:
        esc_min  = st.number_input("Nota mínima",     value=1.0, min_value=0.0, max_value=6.9, step=0.1, key="esc_min")
    with col2:
        esc_max  = st.number_input("Nota máxima",     value=7.0, min_value=1.0, max_value=10.0, step=0.1, key="esc_max")
    with col3:
        esc_apro = st.number_input("Nota aprobación", value=4.0, min_value=1.0, max_value=7.0,  step=0.1, key="esc_apro")

    st.divider()
    st.subheader("Notas y ponderaciones")
    st.caption("Todas las ponderaciones deben sumar exactamente 100% para calcular.")

    if "n_notas" not in st.session_state:
        st.session_state.n_notas = 3

    col_a, col_b = st.columns([1, 4])
    with col_a:
        if st.button("＋ Agregar nota", use_container_width=True):
            st.session_state.n_notas += 1
    with col_b:
        if st.button("🗑 Limpiar todo", use_container_width=True):
            st.session_state.n_notas = 3
            for i in range(20):
                st.session_state.pop(f"nota_{i}", None)
                st.session_state.pop(f"pond_{i}", None)
                st.session_state.pop(f"desc_{i}", None)

    h1, h2, h3 = st.columns([3, 2, 2])
    h1.markdown("**Descripción**")
    h2.markdown("**Nota**")
    h3.markdown("**Ponderación (%)**")

    notas_vals = []
    pond_vals  = []
    desc_vals  = []
    suma_pond  = 0.0

    for i in range(st.session_state.n_notas):
        c1, c2, c3 = st.columns([3, 2, 2])
        with c1:
            d = st.text_input(f"Desc {i+1}", value="", placeholder=f"ej: Prueba {i+1}",
                              key=f"desc_{i}", label_visibility="collapsed")
        with c2:
            n = st.number_input(f"Nota {i+1}", min_value=float(esc_min), max_value=float(esc_max),
                                value=None, step=0.1, placeholder="ej: 5.5",
                                key=f"nota_{i}", label_visibility="collapsed")
        with c3:
            p = st.number_input(f"Pond {i+1}", min_value=0.0, max_value=100.0,
                                value=None, step=1.0, placeholder="ej: 30",
                                key=f"pond_{i}", label_visibility="collapsed")
        notas_vals.append(n)
        pond_vals.append(p)
        desc_vals.append(d)
        if p: suma_pond += p

    if suma_pond > 0:
        restante = 100 - suma_pond
        if abs(restante) < 0.01:
            st.success(f"✅ Ponderación completa: 100%")
        elif suma_pond < 100:
            st.warning(f"⚠️ Ponderación actual: {suma_pond:.1f}% — faltan {restante:.1f}%")
        else:
            st.error(f"❌ Ponderación excede 100%: {suma_pond:.1f}%")

    st.divider()

    promedio = None
    items_validos = []
    if abs(suma_pond - 100) < 0.01:
        suma_weighted = 0.0
        for i in range(st.session_state.n_notas):
            n = notas_vals[i]
            p = pond_vals[i]
            if n is not None and p is not None:
                suma_weighted += n * (p / 100)
                items_validos.append({"descripcion": desc_vals[i] or f"Nota {i+1}", "nota": n, "ponderacion": p})

        if items_validos:
            promedio = round(suma_weighted, 1)
            st.session_state["promedio_semestral"] = promedio

            if promedio >= esc_apro:
                estado = "aprobado"; emoji = "🎉 APROBADO"; color = "#34d399"
            elif promedio >= esc_apro - 0.9:
                estado = "examen"; emoji = "⚠️ ZONA DE EXAMEN"; color = "#fbbf24"
            else:
                estado = "reprobado"; emoji = "❌ REPROBADO"; color = "#f87171"

            st.markdown(f"""
            <div class="res-{estado}">
                <div style="font-size:.85rem;font-weight:600;opacity:.7;margin-bottom:.4rem">{emoji}</div>
                <div class="nota-grande" style="color:{color}">{promedio:.1f}</div>
                <div style="margin-top:.5rem;font-size:.88rem">Promedio ponderado final</div>
            </div>
            """, unsafe_allow_html=True)

            df = pd.DataFrame(items_validos)
            df["Aporte"] = (df["nota"] * df["ponderacion"] / 100).round(3)
            df.columns = ["Descripción", "Nota", "Ponderación (%)", "Aporte"]
            st.dataframe(df, use_container_width=True, hide_index=True)

            # ── Guardar en historial ─────────────────────────────────────────
            st.divider()
            st.subheader("💾 Guardar en historial")

            ramos = get_ramos(user["id"])
            semestres_disp = sorted(set(r["semestre"] for r in ramos)) if ramos else []

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                modo_ramo = st.radio("Ramo", ["Seleccionar existente", "Crear nuevo"], horizontal=True, key="modo_ramo")
            
            ramo_id_guardar = None
            if modo_ramo == "Crear nuevo" or not ramos:
                with col_s2:
                    nuevo_semestre = st.text_input("Semestre", placeholder="ej: 2025-1", key="nuevo_semestre_t1")
                nuevo_nombre_ramo = st.text_input("Nombre del ramo", placeholder="ej: Cálculo I", key="nuevo_ramo_nombre")
                
                if st.button("💾 Guardar notas", use_container_width=True, key="guardar_nuevo"):
                    if not nuevo_nombre_ramo.strip() or not nuevo_semestre.strip():
                        st.error("Ingresa nombre del ramo y semestre.")
                    else:
                        crear_ramo(user["id"], nuevo_nombre_ramo, nuevo_semestre)
                        ramos_act = get_ramos(user["id"])
                        ramo_nuevo = [r for r in ramos_act if r["nombre"] == nuevo_nombre_ramo.strip()]
                        if ramo_nuevo:
                            guardar_notas(ramo_nuevo[-1]["id"], items_validos)
                            st.success(f"✅ Notas guardadas en **{nuevo_nombre_ramo}** (Semestre {nuevo_semestre})")
            else:
                with col_s2:
                    sem_filtro = st.selectbox("Filtrar por semestre", ["Todos"] + semestres_disp, key="sem_filtro_t1")
                ramos_filtrados = ramos if sem_filtro == "Todos" else [r for r in ramos if r["semestre"] == sem_filtro]
                ramo_opts = {f"{r['nombre']} [{r['semestre']}]": r["id"] for r in ramos_filtrados}
                
                if ramo_opts:
                    ramo_sel = st.selectbox("Selecciona el ramo", list(ramo_opts.keys()), key="ramo_sel_guardar")
                    ramo_id_guardar = ramo_opts[ramo_sel]
                    if st.button("💾 Guardar / actualizar notas", use_container_width=True, key="guardar_existente"):
                        guardar_notas(ramo_id_guardar, items_validos)
                        st.success(f"✅ Notas actualizadas en **{ramo_sel}**")
                else:
                    st.info("No hay ramos en ese semestre. Crea uno nuevo.")
    else:
        st.info("Completa las notas y ponderaciones hasta llegar a 100% para ver el resultado.")


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — ¿VOY A EXAMEN?
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("¿Necesito ir a examen?")

    promedio_tab2 = st.session_state.get("promedio_semestral", None)
    nota_apro_ex = st.number_input("Nota de aprobación", value=4.0, min_value=1.0, max_value=7.0, step=0.1, key="ex_apro")

    if promedio_tab2 is None:
        st.info("Primero ingresa tus notas en la pestaña **🧮 Mis Notas** y completa la ponderación al 100%.")
    else:
        col1, col2 = st.columns(2)
        col1.metric("Tu promedio semestral", f"{promedio_tab2:.1f}")
        va_examen = promedio_tab2 < nota_apro_ex

        if va_examen:
            st.error(f"⚠️ **Debes ir a examen.** Tu promedio ({promedio_tab2:.1f}) es menor a {nota_apro_ex}.")
        else:
            st.success(f"✅ **Puedes eximirte.** Tu promedio ({promedio_tab2:.1f}) supera {nota_apro_ex}.")

        st.divider()
        st.subheader("Simulador de examen")

        col_s, col_e = st.columns(2)
        with col_s:
            pond_sem = st.number_input("Ponderación semestre (%)", value=70, min_value=1, max_value=99, step=5, key="pond_sem_ex")
        with col_e:
            pond_ex  = st.number_input("Ponderación examen (%)",   value=30, min_value=1, max_value=99, step=5, key="pond_ex_ex")

        if pond_sem + pond_ex != 100:
            st.warning(f"⚠️ La suma de ponderaciones es {pond_sem + pond_ex}%, debe ser 100%.")
        else:
            min_ex = (nota_apro_ex - promedio_tab2 * (pond_sem / 100)) / (pond_ex / 100)

            col1, col2 = st.columns(2)
            col1.metric("Nota mínima en examen para aprobar",
                        f"{min_ex:.1f}" if 1 <= min_ex <= 7 else ("🚫 Imposible" if min_ex > 7 else "✅ Cualquier nota"))
            if min_ex > 7:
                st.error("Aunque saques la nota máxima, no alcanzarás a aprobar con esta ponderación.")

            st.markdown("**¿Qué nota final sacaré si saco...?**")
            nota_sim = st.slider("Nota de examen", min_value=1.0, max_value=7.0, value=4.0, step=0.1)
            final = round(promedio_tab2 * (pond_sem / 100) + nota_sim * (pond_ex / 100), 2)
            apro  = final >= nota_apro_ex

            if apro:
                st.success(f"Con nota {nota_sim:.1f} en el examen → **Nota final: {final:.2f}** ✅ Aprobado")
            else:
                st.error(f"Con nota {nota_sim:.1f} en el examen → **Nota final: {final:.2f}** ❌ Reprobado")


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — HISTORIAL PERSONAL
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader(f"📚 Historial de {user['nombre'].split()[0]}")
    st.caption(f"Carrera: **{user['carrera']}**")

    ramos = get_ramos(user["id"])

    if not ramos:
        st.info("Aún no tienes ramos guardados. Ve a **🧮 Mis Notas**, calcula y guarda tus notas.")
    else:
        # Filtros
        semestres = sorted(set(r["semestre"] for r in ramos), reverse=True)
        col_f1, col_f2 = st.columns([2, 3])
        with col_f1:
            sem_sel = st.selectbox("Semestre", ["Todos"] + semestres, key="hist_sem_sel")
        with col_f2:
            buscar = st.text_input("Buscar ramo", placeholder="ej: Cálculo", key="hist_buscar")

        ramos_filtrados = ramos
        if sem_sel != "Todos":
            ramos_filtrados = [r for r in ramos_filtrados if r["semestre"] == sem_sel]
        if buscar.strip():
            ramos_filtrados = [r for r in ramos_filtrados if buscar.lower() in r["nombre"].lower()]

        # Agregar ramo desde historial
        with st.expander("➕ Agregar nuevo ramo"):
            col_nr1, col_nr2 = st.columns(2)
            with col_nr1:
                nuevo_ramo_h = st.text_input("Nombre del ramo", key="hist_nuevo_ramo")
            with col_nr2:
                nuevo_sem_h  = st.text_input("Semestre", placeholder="ej: 2025-1", key="hist_nuevo_sem")
            if st.button("Crear ramo", key="hist_crear_ramo"):
                if nuevo_ramo_h.strip() and nuevo_sem_h.strip():
                    crear_ramo(user["id"], nuevo_ramo_h, nuevo_sem_h)
                    st.success(f"Ramo **{nuevo_ramo_h}** creado.")
                    st.rerun()
                else:
                    st.error("Completa nombre y semestre.")

        st.divider()

        if not ramos_filtrados:
            st.info("No hay ramos que coincidan con el filtro.")
        else:
            # Agrupar por semestre
            sem_grupos = {}
            for r in ramos_filtrados:
                sem_grupos.setdefault(r["semestre"], []).append(r)

            for sem in sorted(sem_grupos.keys(), reverse=True):
                st.markdown(f"### 📅 Semestre {sem}")
                for ramo in sem_grupos[sem]:
                    notas = get_notas(ramo["id"])

                    with st.container():
                        col_ramo, col_acciones = st.columns([4, 1])
                        with col_ramo:
                            if notas:
                                promedio_r = round(sum(n["nota"] * n["ponderacion"] / 100 for n in notas), 1)
                                color_p = "#34d399" if promedio_r >= 4.0 else ("#fbbf24" if promedio_r >= 3.1 else "#f87171")
                                st.markdown(f"""
                                <div class="historial-card">
                                    <div style="display:flex;justify-content:space-between;align-items:center">
                                        <span class="ramo-header">📖 {ramo['nombre']}</span>
                                        <span style="font-family:'Space Grotesk';font-size:1.6rem;font-weight:700;color:{color_p}">{promedio_r:.1f}</span>
                                    </div>
                                    <div style="color:#8b8fa8;font-size:.82rem;margin-top:.3rem">{len(notas)} evaluación{'es' if len(notas)!=1 else ''} registradas</div>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div class="historial-card">
                                    <div class="ramo-header">📖 {ramo['nombre']}</div>
                                    <div style="color:#8b8fa8;font-size:.82rem;margin-top:.3rem">Sin notas registradas</div>
                                </div>
                                """, unsafe_allow_html=True)

                        with col_acciones:
                            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
                            if st.button("✏️", key=f"edit_{ramo['id']}", help="Editar notas"):
                                st.session_state.ramo_editando = ramo["id"]
                            if st.button("🗑️", key=f"del_{ramo['id']}", help="Eliminar ramo"):
                                eliminar_ramo(ramo["id"])
                                st.rerun()

                    # Panel de edición inline
                    if st.session_state.ramo_editando == ramo["id"]:
                        with st.expander(f"✏️ Editar notas de {ramo['nombre']}", expanded=True):
                            notas_actuales = get_notas(ramo["id"])
                            n_edit_key = f"n_edit_{ramo['id']}"
                            if n_edit_key not in st.session_state:
                                st.session_state[n_edit_key] = max(len(notas_actuales), 1)

                            col_ea, col_eb = st.columns([1, 4])
                            with col_ea:
                                if st.button("＋", key=f"add_edit_{ramo['id']}"):
                                    st.session_state[n_edit_key] += 1
                            with col_eb:
                                pass

                            h1e, h2e, h3e = st.columns([3, 2, 2])
                            h1e.markdown("**Descripción**")
                            h2e.markdown("**Nota**")
                            h3e.markdown("**Ponderación (%)**")

                            edit_items = []
                            suma_edit = 0.0
                            for i in range(st.session_state[n_edit_key]):
                                default_desc = notas_actuales[i]["descripcion"] if i < len(notas_actuales) else ""
                                default_nota = float(notas_actuales[i]["nota"]) if i < len(notas_actuales) else None
                                default_pond = float(notas_actuales[i]["ponderacion"]) if i < len(notas_actuales) else None

                                ce1, ce2, ce3 = st.columns([3, 2, 2])
                                with ce1:
                                    d_e = st.text_input("Desc", value=default_desc, key=f"ed_desc_{ramo['id']}_{i}", label_visibility="collapsed")
                                with ce2:
                                    n_e = st.number_input("Nota", min_value=1.0, max_value=7.0, value=default_nota, step=0.1,
                                                          key=f"ed_nota_{ramo['id']}_{i}", label_visibility="collapsed")
                                with ce3:
                                    p_e = st.number_input("Pond", min_value=0.0, max_value=100.0, value=default_pond, step=1.0,
                                                          key=f"ed_pond_{ramo['id']}_{i}", label_visibility="collapsed")
                                if n_e is not None and p_e is not None:
                                    edit_items.append({"descripcion": d_e or f"Nota {i+1}", "nota": n_e, "ponderacion": p_e})
                                    suma_edit += p_e

                            if abs(suma_edit - 100) < 0.01:
                                st.success("✅ Ponderación: 100%")
                            elif suma_edit > 0:
                                st.warning(f"⚠️ Ponderación: {suma_edit:.1f}%")

                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.button("💾 Guardar cambios", key=f"save_edit_{ramo['id']}", use_container_width=True):
                                    guardar_notas(ramo["id"], edit_items)
                                    st.session_state.ramo_editando = None
                                    st.success("Notas actualizadas.")
                                    st.rerun()
                            with col_btn2:
                                if st.button("Cancelar", key=f"cancel_edit_{ramo['id']}", use_container_width=True):
                                    st.session_state.ramo_editando = None
                                    st.rerun()

                            # Mostrar tabla de resultado si ponderación OK
                            if edit_items and abs(suma_edit - 100) < 0.01:
                                prom_edit = round(sum(it["nota"] * it["ponderacion"] / 100 for it in edit_items), 1)
                                color_e = "#34d399" if prom_edit >= 4.0 else ("#fbbf24" if prom_edit >= 3.1 else "#f87171")
                                st.metric("Promedio calculado", f"{prom_edit:.1f}")


# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — TABLA DE ESCALA
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("⚙️ Configuración de la prueba")

    col1, col2, col3 = st.columns(3)
    with col1:
        max_pts   = st.number_input("Puntaje máximo",              value=100, min_value=1,  step=1,   key="esc_maxpts")
    with col2:
        min_apro  = st.number_input("Puntaje mínimo para aprobar", value=60,  min_value=0,  step=1,   key="esc_minapro")
    with col3:
        nota_apro_esc = st.number_input("Nota de aprobación",      value=4.0, min_value=1.0, max_value=7.0, step=0.1, key="esc_notaapro")

    col4, col5, col6 = st.columns(3)
    with col4:
        nota_min_esc = st.number_input("Nota mínima (puntaje 0)",     value=1.0, min_value=1.0, max_value=6.9, step=0.1, key="esc_notamin")
    with col5:
        nota_max_esc = st.number_input("Nota máxima (puntaje 100%)",  value=7.0, min_value=1.0, max_value=10.0, step=0.1, key="esc_notamax")
    with col6:
        decimales    = st.number_input("Decimales en nota",            value=1,   min_value=0,  max_value=2,   step=1,   key="esc_decs")

    st.divider()
    st.subheader("🔍 Buscar tu puntaje")
    puntaje_buscar = st.number_input("Tu puntaje obtenido", min_value=0, max_value=int(max_pts), step=1, value=None, placeholder="ej: 72", key="esc_buscar")

    def pts_a_nota(pts, max_p, min_apro_p, n_apro, n_min, n_max):
        if max_p == min_apro_p:
            return n_apro if pts >= min_apro_p else n_min
        if pts >= min_apro_p:
            return n_apro + (pts - min_apro_p) / (max_p - min_apro_p) * (n_max - n_apro)
        else:
            if min_apro_p == 0: return n_min
            return n_min + (pts / min_apro_p) * (n_apro - n_min)

    if puntaje_buscar is not None:
        nota_res = pts_a_nota(puntaje_buscar, max_pts, min_apro, nota_apro_esc, nota_min_esc, nota_max_esc)
        apro_res = puntaje_buscar >= min_apro
        pct_res  = (puntaje_buscar / max_pts * 100) if max_pts > 0 else 0
        col1, col2, col3 = st.columns(3)
        col1.metric("Puntaje", f"{puntaje_buscar} / {max_pts}")
        col2.metric("Porcentaje", f"{pct_res:.1f}%")
        col3.metric("Nota", f"{nota_res:.{decimales}f}")
        if apro_res:
            st.success("✅ Aprobado")
        else:
            st.error("❌ Reprobado")

    st.divider()
    st.subheader("📋 Tabla completa")

    filas = []
    for p in range(int(max_pts), -1, -1):
        nota = pts_a_nota(p, max_pts, min_apro, nota_apro_esc, nota_min_esc, nota_max_esc)
        pct  = (p / max_pts * 100) if max_pts > 0 else 0
        apro = p >= min_apro
        filas.append({
            "Puntaje": p,
            "% del total": f"{pct:.1f}%",
            "Nota": round(nota, decimales),
            "Estado": "✅ Aprueba" if apro else "❌ Reprueba"
        })

    df_escala = pd.DataFrame(filas)

    def colorear(row):
        nota = row["Nota"]
        if nota >= nota_apro_esc + 1.5:
            color = "color: #a78bfa; font-weight: bold"
        elif nota >= nota_apro_esc:
            color = "color: #34d399; font-weight: bold"
        elif nota >= nota_apro_esc - 0.9:
            color = "color: #fbbf24; font-weight: bold"
        else:
            color = "color: #f87171; font-weight: bold"
        return ["", "", color, ""]

    st.dataframe(
        df_escala.style.apply(colorear, axis=1),
        use_container_width=True,
        hide_index=True,
        height=400
    )


# ════════════════════════════════════════════════════════════════════════════
# TAB 5 — CALCULADORA LIBRE
# ════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("➕ Calculadora Libre de Notas")
    st.caption("Mezcla notas con distintas ponderaciones. No necesitan sumar 100%. Agrega décimas al final.")

    if "n_libre" not in st.session_state:
        st.session_state.n_libre = 2

    col_a, col_b = st.columns([1, 4])
    with col_a:
        if st.button("＋ Agregar", use_container_width=True, key="libre_add"):
            st.session_state.n_libre += 1
    with col_b:
        if st.button("🗑 Limpiar", use_container_width=True, key="libre_clear"):
            st.session_state.n_libre = 2
            for i in range(20):
                st.session_state.pop(f"libre_desc_{i}", None)
                st.session_state.pop(f"libre_nota_{i}", None)
                st.session_state.pop(f"libre_pond_{i}", None)
            st.session_state.pop("libre_decimas", None)

    h1, h2, h3 = st.columns([3, 2, 2])
    h1.markdown("**Descripción**")
    h2.markdown("**Nota**")
    h3.markdown("**Ponderación (%)**")

    libre_items = []
    suma_pond_libre = 0.0

    for i in range(st.session_state.n_libre):
        c1, c2, c3 = st.columns([3, 2, 2])
        with c1:
            desc = st.text_input(f"Desc {i+1}", value="", placeholder=f"ej: Prueba {i+1}",
                                 key=f"libre_desc_{i}", label_visibility="collapsed")
        with c2:
            nota_l = st.number_input(f"Nota libre {i+1}", min_value=1.0, max_value=7.0,
                                     value=None, step=0.1, placeholder="ej: 5.5",
                                     key=f"libre_nota_{i}", label_visibility="collapsed")
        with c3:
            pond_l = st.number_input(f"Pond libre {i+1}", min_value=0.0, max_value=100.0,
                                     value=None, step=1.0, placeholder="ej: 25",
                                     key=f"libre_pond_{i}", label_visibility="collapsed")
        if nota_l is not None and pond_l is not None and pond_l > 0:
            libre_items.append({
                "Descripción": desc if desc else f"Nota {i+1}",
                "Nota": nota_l,
                "Ponderación (%)": pond_l,
                "Aporte": round(nota_l * pond_l / 100, 3)
            })
            suma_pond_libre += pond_l

    st.divider()
    st.subheader("⭐ Décimas adicionales")
    decimas = st.number_input("Décimas a sumar", min_value=0.0, max_value=2.0,
                               value=0.0, step=0.1, key="libre_decimas",
                               help="Se suman directamente a tu nota final")

    if libre_items:
        st.divider()
        st.subheader("📋 Desglose del cálculo")

        df_libre = pd.DataFrame(libre_items)
        st.dataframe(df_libre, use_container_width=True, hide_index=True)

        suma_aporte = sum(it["Aporte"] for it in libre_items)

        ponderacion_completa = abs(suma_pond_libre - 100) < 0.01
        if ponderacion_completa:
            nota_base = suma_aporte
        else:
            nota_base = suma_aporte / (suma_pond_libre / 100) if suma_pond_libre > 0 else 0

        nota_final = min(7.0, nota_base + decimas)
        aprobado   = nota_final >= 4.0

        col1, col2, col3 = st.columns(3)
        col1.metric("Ponderación total", f"{suma_pond_libre:.1f}%")
        col2.metric("Nota base", f"{nota_base:.2f}")
        col3.metric("Nota final (con décimas)", f"{nota_final:.2f}",
                    delta=f"+{decimas:.1f} décimas" if decimas > 0 else None)

        if not ponderacion_completa:
            st.warning(f"⚠️ La ponderación total es {suma_pond_libre:.1f}% (no 100%). La nota se calculó de forma proporcional al total ingresado.")

        if aprobado:
            st.success(f"✅ **Aprobado** con nota final **{nota_final:.2f}**")
        else:
            st.error(f"❌ **Reprobado** con nota final **{nota_final:.2f}**")
    else:
        st.info("Ingresa al menos una nota con su ponderación para ver el resultado.")
