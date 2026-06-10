import streamlit as st
import pandas as pd

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

/* Fondo oscuro */
.stApp { background: #0f1117; }

/* Título principal */
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

/* Cards */
.nota-card {
    background: #1a1d27;
    border: 1px solid #2e3350;
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}

/* Resultado */
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

/* Tabs */
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
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<div class="titulo-app">🎓 PasaLosRamos</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo-app">Calculadora de notas con ponderación</div>', unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🧮 Mis Notas",
    "📝 ¿Voy a Examen?",
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

    # Número de notas
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

    # Cabecera de columnas
    h1, h2, h3 = st.columns([3, 2, 1])
    h1.markdown("**Nota**")
    h2.markdown("**Ponderación (%)**")

    notas_vals = []
    pond_vals  = []
    suma_pond  = 0.0

    for i in range(st.session_state.n_notas):
        c1, c2 = st.columns([3, 2])
        with c1:
            n = st.number_input(f"Nota {i+1}", min_value=float(esc_min), max_value=float(esc_max),
                                value=None, step=0.1, placeholder="ej: 5.5",
                                key=f"nota_{i}", label_visibility="collapsed")
        with c2:
            p = st.number_input(f"Pond {i+1}", min_value=0.0, max_value=100.0,
                                value=None, step=1.0, placeholder="ej: 30",
                                key=f"pond_{i}", label_visibility="collapsed")
        notas_vals.append(n)
        pond_vals.append(p)
        if p: suma_pond += p

    # Indicador ponderación
    if suma_pond > 0:
        restante = 100 - suma_pond
        if abs(restante) < 0.01:
            st.success(f"✅ Ponderación completa: 100%")
        elif suma_pond < 100:
            st.warning(f"⚠️ Ponderación actual: {suma_pond:.1f}% — faltan {restante:.1f}%")
        else:
            st.error(f"❌ Ponderación excede 100%: {suma_pond:.1f}%")

    st.divider()

    # Calcular
    if abs(suma_pond - 100) < 0.01:
        suma_weighted = 0.0
        items_validos = []
        for i in range(st.session_state.n_notas):
            n = notas_vals[i]
            p = pond_vals[i]
            if n is not None and p is not None:
                suma_weighted += n * (p / 100)
                items_validos.append((n, p))

        if items_validos:
            promedio = round(suma_weighted, 1)
            st.session_state["promedio_semestral"] = promedio

            if promedio >= esc_apro:
                estado = "aprobado"
                emoji  = "🎉 APROBADO"
                color  = "#34d399"
            elif promedio >= esc_apro - 0.9:
                estado = "examen"
                emoji  = "⚠️ ZONA DE EXAMEN"
                color  = "#fbbf24"
            else:
                estado = "reprobado"
                emoji  = "❌ REPROBADO"
                color  = "#f87171"

            st.markdown(f"""
            <div class="res-{estado}">
                <div style="font-size:.85rem;font-weight:600;opacity:.7;margin-bottom:.4rem">{emoji}</div>
                <div class="nota-grande" style="color:{color}">{promedio:.1f}</div>
                <div style="margin-top:.5rem;font-size:.88rem">Promedio ponderado final</div>
            </div>
            """, unsafe_allow_html=True)

            # Tabla de desglose
            df = pd.DataFrame(items_validos, columns=["Nota", "Ponderación (%)"])
            df["Aporte"] = (df["Nota"] * df["Ponderación (%)"] / 100).round(3)
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Completa las notas y ponderaciones hasta llegar a 100% para ver el resultado.")


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — ¿VOY A EXAMEN?
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("¿Necesito ir a examen?")

    promedio = st.session_state.get("promedio_semestral", None)
    nota_apro_ex = st.number_input("Nota de aprobación", value=4.0, min_value=1.0, max_value=7.0, step=0.1, key="ex_apro")

    if promedio is None:
        st.info("Primero ingresa tus notas en la pestaña **🧮 Mis Notas** y completa la ponderación al 100%.")
    else:
        col1, col2 = st.columns(2)
        col1.metric("Tu promedio semestral", f"{promedio:.1f}")
        va_examen = promedio < nota_apro_ex

        if va_examen:
            st.error(f"⚠️ **Debes ir a examen.** Tu promedio ({promedio:.1f}) es menor a {nota_apro_ex}.")
        else:
            st.success(f"✅ **Puedes eximirte.** Tu promedio ({promedio:.1f}) supera {nota_apro_ex}.")

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
            # Nota mínima para aprobar
            min_ex = (nota_apro_ex - promedio * (pond_sem / 100)) / (pond_ex / 100)

            col1, col2 = st.columns(2)
            col1.metric("Nota mínima en examen para aprobar",
                        f"{min_ex:.1f}" if 1 <= min_ex <= 7 else ("🚫 Imposible" if min_ex > 7 else "✅ Cualquier nota"))
            if min_ex > 7:
                st.error("Aunque saques la nota máxima, no alcanzarás a aprobar con esta ponderación.")

            st.markdown("**¿Qué nota final sacaré si saco...?**")
            nota_sim = st.slider("Nota de examen", min_value=1.0, max_value=7.0, value=4.0, step=0.1)
            final = round(promedio * (pond_sem / 100) + nota_sim * (pond_ex / 100), 2)
            apro  = final >= nota_apro_ex

            if apro:
                st.success(f"Con nota {nota_sim:.1f} en el examen → **Nota final: {final:.2f}** ✅ Aprobado")
            else:
                st.error(f"Con nota {nota_sim:.1f} en el examen → **Nota final: {final:.2f}** ❌ Reprobado")


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — TABLA DE ESCALA
# ════════════════════════════════════════════════════════════════════════════
with tab3:
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

    # Buscador
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

    # Generar tabla
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
# TAB 4 — CALCULADORA LIBRE
# ════════════════════════════════════════════════════════════════════════════
with tab4:
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

    # Cabeceras
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

    # Resultado
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
