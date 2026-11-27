import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
import sqlite3

from database import init_db, get_connection
import importlib
import baker_math
importlib.reload(baker_math)

# Configuración de página
st.set_page_config(
    page_title="PALVETI - Panadería Artesanal",
    page_icon="🥖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar Base de Datos con soporte COP y nuevas tablas
init_db()

# Funciones de limpieza de números para evitar ceros innecesarios (ej: '3003545,0000' -> '3003545')
def clean_phone_or_code(val):
    """Limpia números de teléfono, identificadores o códigos para que no muestren comas ni ceros decimales."""
    if val is None or pd.isna(val):
        return ""
    s = str(val).strip()
    if s.endswith(".0"):
        s = s[:-2]
    s = s.replace(",0000", "").replace(".0000", "").replace(",00", "").replace(".00", "")
    return s

def format_stock_qty(qty, unidad):
    """
    Formatea cantidades numéricas:
    - Para pesos (g, kg, libra, lb, ml, l), permite decimales si los tiene (ej: 40.000 g o 1.5 kg).
    - Para unidades u otros elementos no de peso, formatea como entero estricto sin comas ni ceros decimales.
    """
    if qty is None or pd.isna(qty):
        return "0"
    try:
        f_val = float(qty)
        u_lower = str(unidad).lower()
        if any(w in u_lower for w in ["g", "kg", "gramo", "kilo", "libra", "lb", "ml", "l", "litro"]):
            if f_val.is_integer():
                return f"{int(f_val):,}".replace(",", ".")
            return f"{f_val:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            return str(int(round(f_val)))
    except (ValueError, TypeError):
        return str(qty)

# Estilos CSS con Tailwind Red-800 (#991b1b) para Sidebar y diseño artesanal
st.markdown("""
<style>
    :root {
        --primary-color: #991b1b; /* Tailwind red-800 */
        --primary-dark: #7f1d1d;  /* Tailwind red-900 */
        --primary-light: #b91c1c; /* Tailwind red-700 */
        --bg-light: #FBF9F5;
        --accent-gold: #D4A373;
    }

    /* SIDEBAR: TAILWIND RED-800 (#991b1b) */
    [data-testid="stSidebar"], 
    [data-testid="stSidebar"] > div:first-child,
    section[data-testid="stSidebar"],
    [data-testid="stSidebarContent"],
    div[data-testid="stSidebarUserContent"] {
        background-color: #991b1b !important;
        color: #fef2f2 !important;
    }

    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label {
        color: #fef2f2 !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(254, 226, 226, 0.25) !important;
        margin: 12px 0 !important;
    }

    .brand-title {
        font-family: 'Georgia', serif;
        font-size: 1.85rem;
        font-weight: 800;
        color: #ffffff !important;
        letter-spacing: 0.5px;
        margin-bottom: 2px;
    }

    .brand-subtitle {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 0.92rem;
        color: #fecaca !important;
        font-weight: 500;
        margin-bottom: 10px;
    }

    .nav-header-text {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #fca5a5 !important;
        margin-bottom: 6px;
    }

    /* MÓDULOS EN SIDEBAR */
    [data-testid="stSidebar"] [data-testid="stRadio"] > label {
        display: none !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 5px !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        background-color: rgba(255, 255, 255, 0.08) !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        margin-bottom: 3px !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: rgba(255, 255, 255, 0.18) !important;
        border-color: rgba(255, 255, 255, 0.35) !important;
        transform: translateX(3px);
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"],
    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
        background-color: #7f1d1d !important;
        border: 1.5px solid #fca5a5 !important;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.35) !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label p,
    [data-testid="stSidebar"] div[role="radiogroup"] label span {
        color: #ffffff !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] input[type="radio"] {
        accent-color: #ffffff !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] svg {
        fill: #ffffff !important;
    }

    /* ALERTAS Y TARJETAS */
    .success-stock-banner {
        background-color: #ECFDF5;
        border: 2px solid #10B981;
        border-radius: 8px;
        padding: 14px 18px;
        color: #065F46;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(16, 185, 129, 0.15);
    }

    .main-header {
        font-family: 'Georgia', serif;
        font-size: 2.2rem;
        color: #991b1b;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .sub-header {
        font-family: 'Helvetica Neue', sans-serif;
        color: #8C6D58;
        font-size: 1.05rem;
        margin-top: -5px;
        margin-bottom: 25px;
    }

    .stock-alert {
        background-color: #FDEDEC;
        border-left: 5px solid #E74C3C;
        padding: 10px 15px;
        margin-bottom: 15px;
        border-radius: 4px;
        color: #922B21;
    }

    .badge-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-minorista { background-color: #E0E7FF; color: #3730A3; }
    .badge-mayorista { background-color: #FEF3C7; color: #92400E; }
    .badge-vencido { background-color: #FEE2E2; color: #991B1B; font-weight: 700; }
    .badge-proximo { background-color: #FEF3C7; color: #B45309; font-weight: 700; }
    .badge-aldia { background-color: #D1FAE5; color: #065F46; font-weight: 700; }

    /* ANIMACIÓN HOVER ZOOM Y CONTENEDORES PARA EL CALENDARIO */
    .cal-day-cell {
        min-height: 96px;
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 6px;
        margin-bottom: 5px;
        transition: transform 0.22s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.22s ease, border-color 0.22s ease !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        position: relative;
        cursor: pointer;
    }

    .cal-day-cell:hover {
        transform: scale(1.04) translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(153, 27, 27, 0.15) !important;
        border-color: #991b1b !important;
        z-index: 25 !important;
    }

    /* CONTENEDOR DE CADA RECUA DRO DEL CALENDARIO MENSUAL */
    div[data-testid="stColumn"] div[data-testid="stVerticalBlockBorderWrapper"] {
        transition: transform 0.22s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.22s ease, border-color 0.22s ease !important;
        border-radius: 8px !important;
        background-color: #FFFFFF !important;
        padding: 4px 6px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    }

    div[data-testid="stColumn"] div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: scale(1.04) translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(153, 27, 27, 0.15) !important;
        border-color: #991b1b !important;
        z-index: 20 !important;
    }

    /* REDUCCIÓN DE ESPACIADO INTERNO EN CADA CELDA */
    div[data-testid="stColumn"] div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlock"] {
        gap: 0.15rem !important;
    }

    /* DESTACADO PARA EL DÍA DE HOY */
    div[data-testid="stColumn"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.cal-badge-hoy) {
        border: 2px solid #991b1b !important;
        background-color: #FFFDFD !important;
    }

    /* BOTONES COMPACTOS DENTRO DE LAS CELDAS (+ Y EDITAR) EN LA ESQUINA SUPERIOR DERECHA */
    div[data-testid="stColumn"] div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stButton"] {
        text-align: right !important;
    }

    div[data-testid="stColumn"] div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stButton"] button {
        min-height: 22px !important;
        height: 24px !important;
        padding: 0 6px !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        line-height: 1 !important;
        border-radius: 5px !important;
        border: 1px solid #CBD5E1 !important;
        background-color: #F8FAFC !important;
        color: #475569 !important;
        box-shadow: none !important;
        float: right !important;
    }

    div[data-testid="stColumn"] div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stButton"] button:hover {
        border-color: #991B1B !important;
        color: #991B1B !important;
        background-color: #FEF2F2 !important;
    }
</style>
""", unsafe_allow_html=True)

# Barra Lateral
st.sidebar.markdown("""
<div class="brand-title">🥖 PALVETI</div>
<div class="brand-subtitle">Gestión Artesanal de Masa Madre (COP)</div>
<hr>
<div class="nav-header-text">Módulos del Sistema:</div>
""", unsafe_allow_html=True)

# Alertas de Stock en Sidebar
alertas_stock = baker_math.get_low_stock_alerts()
if alertas_stock:
    st.sidebar.markdown(f"⚠️ **Atención:** {len(alertas_stock)} insumo(s) con stock bajo.")
    with st.sidebar.expander("Ver insumos por reabastecer"):
        for a in alertas_stock:
            st.error(f"**{a['nombre']}**: {a['stock_actual']:,.0f} {a['unidad_medida']} (Mínimo: {a['stock_minimo']:,.0f})")

menu = st.sidebar.radio(
    "Navegación:",
    [
        "🥖 1. Calculadora & Recetas (Núcleo)",
        "💰 2. Costos & Fijación de Precios",
        "📦 3. Inventario & Materia Prima",
        "📋 4. Pedidos & Preventa (Lotes)",
        "🌡️ 5. Bitácora de Fermentación & Calidad",
        "📊 6. Finanzas & Reportes",
        "📅 7. Calendario de Actividades",
        "🛠️ 8. Mantenimiento de Equipos"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("""
<hr>
<div style="font-size: 0.8rem; color: #fca5a5; text-align: center;">
    <b>PALVETI v2.0</b><br>
    Pesos Colombianos (COP)<br>
    Obrador Local SQLite
</div>
""", unsafe_allow_html=True)

# ==========================================================
# BARRA SUPERIOR Y CENTRO DE NOTIFICACIONES (VISIBLE EN TODOS LOS MÓDULOS)
# ==========================================================
notifs = baker_math.get_all_system_notifications()
total_alertas = notifs["total"]

top_bar_left, top_bar_right = st.columns([3.8, 1.4])
with top_bar_left:
    dias_semana_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    meses_es = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    f_hoy = date.today()
    fecha_bonita = f"{dias_semana_es[f_hoy.weekday()]}, {f_hoy.day} de {meses_es[f_hoy.month - 1]} de {f_hoy.year}"
    st.markdown(f"<div style='padding-top: 6px; color: #64748B; font-size: 0.95rem; font-weight: 500;'>📍 <b>Obrador PALVETI</b> &nbsp;•&nbsp; 📅 {fecha_bonita}</div>", unsafe_allow_html=True)

with top_bar_right:
    btn_notif_label = f"🔔 Alertas Activas ({total_alertas})" if total_alertas > 0 else "🔔 Alertas (0)"
    with st.popover(btn_notif_label, use_container_width=True):
        st.markdown("### 🔔 Centro de Alertas PALVETI")
        if total_alertas == 0:
            st.success("🎉 **¡Todo al día!** No tienes alertas pendientes de mantenimiento, insumos, pedidos ni actividades del calendario.")
        else:
            st.markdown(f"Tienes **{total_alertas} alerta(s) activa(s)** que requieren tu atención:")

            # 1. Avisos de Calendario (antelación de 1 a 2 días o el mismo día)
            if notifs["calendario"]:
                st.markdown("#### 📅 Avisos de Calendario (Anticipación)")
                for c in notifs["calendario"]:
                    if "HOY" in c["titulo"]:
                        st.error(f"**{c['titulo']}**\n\n{c['detalle']}")
                    elif "MAÑANA" in c["titulo"]:
                        st.warning(f"**{c['titulo']}**\n\n{c['detalle']}")
                    else:
                        st.info(f"**{c['titulo']}**\n\n{c['detalle']}")

            # 2. Alertas de Pedidos
            if notifs["pedidos"]:
                st.markdown("#### 🛒 Alertas de Pedidos")
                for p in notifs["pedidos"]:
                    st.warning(f"**{p['titulo']}**\n\n{p['detalle']}")

            # 3. Alertas de Insumos
            if notifs["inventario"]:
                st.markdown("#### 📦 Reabastecimiento de Insumos")
                for s in notifs["inventario"]:
                    st.error(f"**{s['titulo']}**\n\n{s['detalle']}")

            # 4. Alertas de Mantenimiento
            if notifs["mantenimiento"]:
                st.markdown("#### 🛠️ Mantenimiento de Equipos")
                for m in notifs["mantenimiento"]:
                    if "VENCIDO" in m["titulo"]:
                        st.error(f"**{m['titulo']}**\n\n{m['detalle']}")
                    else:
                        st.warning(f"**{m['titulo']}**\n\n{m['detalle']}")

st.markdown("<hr style='margin-top: 4px; margin-bottom: 22px; border-color: #E2E8F0;'>", unsafe_allow_html=True)

# ==========================================================
# MÓDULO 1: CALCULADORA DE PRODUCCIÓN Y RECETAS
# ==========================================================
if menu == "🥖 1. Calculadora & Recetas (Núcleo)":
    st.markdown('<div class="main-header">🥖 Calculadora de Producción & Recetas</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Porcentajes de panadero dinámicos y escalado exacto por hogaza (Valores en COP)</div>', unsafe_allow_html=True)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, peso_unitario_crudo FROM recetas ORDER BY nombre")
    recetas_disponibles = cursor.fetchall()
    conn.close()

    if not recetas_disponibles:
        st.warning("No hay recetas registradas.")
    else:
        col_rec, col_unid, col_peso = st.columns([2, 1, 1])
        with col_rec:
            receta_map = {r["nombre"]: r["id"] for r in recetas_disponibles}
            receta_sel_nombre = st.selectbox("Seleccionar Receta Estándar:", list(receta_map.keys()))
            receta_id = receta_map[receta_sel_nombre]

        receta_default_peso = [r["peso_unitario_crudo"] for r in recetas_disponibles if r["id"] == receta_id][0]

        with col_unid:
            unidades_deseadas = st.number_input("Hogazas / Unidades a hornear:", min_value=1, max_value=500, value=15, step=1)
        with col_peso:
            peso_por_hogaza = st.number_input("Peso masa en crudo (g):", min_value=100.0, max_value=3000.0, value=float(receta_default_peso), step=50.0)

        resultado = baker_math.calculate_production_batch(receta_id, unidades_deseadas, peso_por_hogaza)

        if resultado and resultado["ingredientes"]:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Masa Total Requerida", f"{resultado['total_masa_requerida_g']:,.0f} g", f"{resultado['total_masa_requerida_g']/1000:.2f} kg")
            m2.metric("Harina Base Total (100%)", f"{resultado['harina_base_total_g']:,.0f} g", f"{resultado['harina_base_total_g']/1000:.2f} kg")
            m3.metric("Hidratación Estimada", f"{resultado['hidratacion_porcentaje']}%")
            m4.metric("Costo Total Materia Prima", baker_math.format_cop(resultado['costo_total_lote']), f"{baker_math.format_cop(resultado['costo_por_hogaza'])} / pan")

            st.markdown("#### ⚖️ Tabla de Pesaje de Ingredientes (Receta Estandarizada)")
            
            df_calc = pd.DataFrame(resultado["ingredientes"])
            df_display = df_calc[["nombre", "porcentaje", "gramos_por_hogaza", "gramos_lote", "unidad", "costo_linea", "stock_actual", "stock_suficiente"]].copy()
            df_display.columns = ["Ingrediente", "% Panadero", "Por Hogaza", "Total para el Lote", "Unidad", "Costo (COP)", "Stock en Bodega", "¿Hay Stock?"]
            
            # Formatear costo en COP
            df_display["Costo (COP)"] = df_display["Costo (COP)"].apply(baker_math.format_cop)
            df_display["¿Hay Stock?"] = df_display["¿Hay Stock?"].apply(lambda x: "✅ Sí" if x else "❌ Insuficiente")
            
            # Formatear cantidades respetando si es peso o unidades enteras
            df_display["Por Hogaza"] = df_display.apply(lambda r: format_stock_qty(r["Por Hogaza"], r["Unidad"]), axis=1)
            df_display["Total para el Lote"] = df_display.apply(lambda r: format_stock_qty(r["Total para el Lote"], r["Unidad"]), axis=1)
            df_display["Stock en Bodega"] = df_display.apply(lambda r: format_stock_qty(r["Stock en Bodega"], r["Unidad"]), axis=1)
            df_display["% Panadero"] = df_display["% Panadero"].apply(lambda x: f"{x:g}%" if x > 0 else "-")

            st.dataframe(
                df_display,
                column_config={
                    "Ingrediente": st.column_config.TextColumn("Ingrediente"),
                    "% Panadero": st.column_config.TextColumn("% Panadero"),
                    "Por Hogaza": st.column_config.TextColumn("Por Hogaza"),
                    "Total para el Lote": st.column_config.TextColumn("Total para el Lote"),
                    "Unidad": st.column_config.TextColumn("Unidad"),
                    "Costo (COP)": st.column_config.TextColumn("Costo (COP)"),
                    "Stock en Bodega": st.column_config.TextColumn("Stock en Bodega"),
                    "¿Hay Stock?": st.column_config.TextColumn("¿Hay Stock?")
                },
                use_container_width=True
            )

            st.markdown("---")
            col_lote1, col_lote2 = st.columns([2, 1])
            with col_lote1:
                cod_lote_propuesto = f"LOTE-{datetime.now().strftime('%Y%m%d')}-{receta_sel_nombre[:3].upper()}"
                codigo_nuevo_lote = st.text_input("Código para este nuevo Lote de Producción:", value=cod_lote_propuesto)
                fecha_horneado_prevista = st.date_input("Fecha prevista de horneado:", value=date.today())

            with col_lote2:
                st.write("")
                st.write("")
                if st.button("🚀 Crear Lote y Planificar Producción", type="primary"):
                    conn = get_connection()
                    cur = conn.cursor()
                    try:
                        cur.execute("""
                        INSERT INTO lotes_produccion (codigo_lote, receta_id, unidades_programadas, peso_hogaza_g, fecha_amasado, fecha_horneado, estado, costo_total_lote)
                        VALUES (?, ?, ?, ?, ?, ?, 'PLANIFICADO', ?)
                        """, (codigo_nuevo_lote, receta_id, unidades_deseadas, peso_por_hogaza, date.today().strftime("%Y-%m-%d"), fecha_horneado_prevista.strftime("%Y-%m-%d"), resultado["costo_total_lote"]))
                        
                        nuevo_lote_id = cur.lastrowid
                        cur.execute("INSERT INTO bitacora_fermentacion (lote_id, temp_ambiente_amasado_c) VALUES (?, 24)", (nuevo_lote_id,))
                        conn.commit()
                        st.success(f"✅ ¡Lote **{codigo_nuevo_lote}** registrado con éxito! Costo estimado: {baker_math.format_cop(resultado['costo_total_lote'])}")
                    except sqlite3.IntegrityError:
                        st.error(f"El código de lote {codigo_nuevo_lote} ya existe. Modifícalo antes de guardar.")
                    finally:
                        conn.close()
        else:
            st.warning(f"⚠️ La receta **'{receta_sel_nombre}'** aún no tiene ingredientes vinculados. Añade sus ingredientes en la sección inferior para ver su tabla de pesaje y calcular su producción.")

        # ==========================================================
        # GESTIÓN Y ADICIÓN DE INGREDIENTES EN LA RECETA ACTUAL
        # ==========================================================
        with st.expander(f"📝 Gestionar / Añadir Ingredientes a '{receta_sel_nombre}'"):
            st.caption("Añade, edita o elimina ingredientes específicos de esta receta usando porcentajes de panadero o cantidades fijas.")
            
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, categoria, unidad_medida, costo_unitario FROM ingredientes ORDER BY categoria, nombre")
            todos_insumos = cur.fetchall()
            
            # Obtener ingredientes actuales de esta receta
            cur.execute("""
            SELECT ri.id as ri_id, ri.es_harina_base, ri.porcentaje_panadero, ri.cantidad_fija_por_unidad,
                   i.id as ing_id, i.nombre as ing_nombre, i.unidad_medida, i.categoria
            FROM receta_ingredientes ri
            JOIN ingredientes i ON ri.ingrediente_id = i.id
            WHERE ri.receta_id = ?
            ORDER BY ri.es_harina_base DESC, ri.porcentaje_panadero DESC
            """, (receta_id,))
            ings_receta_actual = cur.fetchall()
            conn.close()

            # Mostrar ingredientes existentes con opción de eliminar
            if ings_receta_actual:
                st.markdown("##### 📋 Ingredientes Actuales de la Receta")
                for ing_item in ings_receta_actual:
                    c_info, c_val, c_del = st.columns([3, 2, 1])
                    with c_info:
                        badge = "🌾 Harina Base (100%)" if ing_item["es_harina_base"] else ("📦 Empaque/Fijo" if ing_item["cantidad_fija_por_unidad"] > 0 else "💧 Ingrediente Masa")
                        st.write(f"**{ing_item['ing_nombre']}** `({badge})`")
                    with c_val:
                        if ing_item["porcentaje_panadero"] > 0:
                            st.write(f"**{ing_item['porcentaje_panadero']:g}%** Panadero")
                        else:
                            st.write(f"**{ing_item['cantidad_fija_por_unidad']:g}** {ing_item['unidad_medida']} / pan")
                    with c_del:
                        if st.button("🗑️ Quitar", key=f"del_ing_rec_{ing_item['ri_id']}"):
                            from database import remove_ingredient_from_recipe
                            remove_ingredient_from_recipe(ing_item["ri_id"])
                            st.success(f"Eliminado '{ing_item['ing_nombre']}' de la receta.")
                            st.rerun()

            st.markdown("---")
            st.markdown("##### ➕ Agregar un Ingrediente a esta Receta")
            with st.form(f"form_add_ing_a_receta_{receta_id}"):
                map_insumos_disp = {f"{i['nombre']} ({i['categoria']} - {i['unidad_medida']})": i for i in todos_insumos}
                sel_ins_label = st.selectbox("Seleccionar Insumo del Inventario:", list(map_insumos_disp.keys()))
                ins_seleccionado = map_insumos_disp[sel_ins_label]

                tipo_ing_rec = st.radio(
                    "Tipo de uso en la receta:",
                    ["Masa con Porcentaje de Panadero (%)", "Artículo Fijo por Hogaza (ej: 1 Bolsa, 1 Etiqueta)"],
                    horizontal=True
                )

                c_ing1, c_ing2 = st.columns(2)
                if "Porcentaje" in tipo_ing_rec:
                    with c_ing1:
                        pct_panadero_val = st.number_input("% Panadero sobre Harina Base (%):", min_value=0.1, max_value=200.0, value=100.0 if ins_seleccionado["categoria"] == "harina" else 20.0, step=0.5)
                    with c_ing2:
                        es_harina_chk = st.checkbox("¿Es Harina Base Principal de la masa?", value=True if ins_seleccionado["categoria"] == "harina" and not ings_receta_actual else False)
                    cant_fija_val = 0.0
                else:
                    with c_ing1:
                        cant_fija_val = st.number_input(f"Cantidad por hogaza ({ins_seleccionado['unidad_medida']}):", min_value=0.1, max_value=50.0, value=1.0, step=1.0)
                    with c_ing2:
                        es_harina_chk = False
                    pct_panadero_val = 0.0

                btn_add_ing = st.form_submit_button("➕ Añadir Ingrediente a la Receta", type="primary")
                if btn_add_ing:
                    from database import add_ingredient_to_recipe
                    add_ingredient_to_recipe(receta_id, ins_seleccionado["id"], es_harina_chk, pct_panadero_val, cant_fija_val)
                    st.success(f"✅ ¡Ingrediente '{ins_seleccionado['nombre']}' añadido/actualizado en la receta!")
                    st.rerun()

            # Opción de eliminar receta si está vacía o se desea retirar
            st.markdown("---")
            with st.expander("⚠️ Eliminar esta receta"):
                st.warning(f"¿Deseas eliminar la receta **'{receta_sel_nombre}'**? Esta acción no se puede deshacer.")
                if st.button("🗑️ Confirmar y Eliminar Receta", key=f"btn_del_rec_{receta_id}"):
                    from database import delete_recipe
                    delete_recipe(receta_id)
                    st.success(f"Receta '{receta_sel_nombre}' eliminada.")
                    st.rerun()

    # ==========================================================
    # CREAR NUEVA RECETA ESTANDARIZADA CON INGREDIENTES
    # ==========================================================
    with st.expander("➕ Crear Nueva Receta Estandarizada con sus Ingredientes"):
        st.markdown("### 🥖 Creador de Receta con Porcentajes de Panadero")
        st.caption("Configura los datos base de tu nuevo pan y selecciona sus ingredientes para generar automáticamente la tabla técnica de producción.")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, categoria, unidad_medida FROM ingredientes ORDER BY categoria, nombre")
        insumos_db = cur.fetchall()
        conn.close()

        harinas_list = [i for i in insumos_db if i["categoria"] == "harina"]
        liquidos_list = [i for i in insumos_db if i["categoria"] == "liquido"]
        fermentos_list = [i for i in insumos_db if i["categoria"] == "fermento"]
        aditivos_list = [i for i in insumos_db if i["categoria"] == "aditivo"]
        empaques_list = [i for i in insumos_db if i["categoria"] in ("empaque", "servicio")]

        with st.form("form_nueva_receta_completa"):
            st.markdown("#### 1. Ficha Técnica del Pan")
            c_nom, c_sug = st.columns([2, 1])
            with c_nom:
                n_nombre = st.text_input("Nombre de la Receta (ej: Hogaza Rústica de Nueces y Dátiles):")
            with c_sug:
                n_precio_sug = st.number_input("Precio de Venta Sugerido inicial ($ COP):", min_value=1000, value=25000, step=1000)

            n_desc = st.text_area("Descripción de la Receta (corteza, greñado, notas de sabor):", value="Hogaza artesanal de fermentación lenta en frío con masa madre.")
            
            c_p1, c_p2, c_p3, c_p4 = st.columns(4)
            with c_p1:
                n_peso_crudo = st.number_input("Peso masa en crudo (g):", min_value=100.0, max_value=3000.0, value=850.0, step=50.0)
            with c_p2:
                n_peso_horneado = st.number_input("Peso horneado estimado (g):", min_value=100.0, max_value=3000.0, value=750.0, step=50.0)
            with c_p3:
                n_tiempo_h = st.number_input("Tiempo de horneado (min):", min_value=10, max_value=120, value=35, step=5)
            with c_p4:
                n_temp_h = st.number_input("Temp. Horno (°C):", min_value=150, max_value=300, value=230, step=5)

            st.markdown("---")
            st.markdown("#### 2. Composición de Ingredientes (% de Panadero)")
            st.caption("La harina base representa el 100%. Todos los demás ingredientes se calculan en proporción a la harina.")

            # Harina Base Principal
            c_h1, c_h2 = st.columns([3, 1])
            with c_h1:
                map_harinas = {h["nombre"]: h["id"] for h in harinas_list}
                sel_harina_base = st.selectbox("🌾 Harina Base Principal (100%):", list(map_harinas.keys()) if map_harinas else ["Harina de Fuerza 13% Proteína"])
            with c_h2:
                pct_h_base = st.number_input("% Harina Base:", value=100.0, disabled=True)

            # Segunda Harina (opcional)
            c_h2_1, c_h2_2 = st.columns([3, 1])
            with c_h2_1:
                opciones_seg_harina = ["(Ninguna - Solo harina base)"] + list(map_harinas.keys())
                sel_seg_harina = st.selectbox("🌾 Segunda Harina (opcional, ej: Centeno):", opciones_seg_harina)
            with c_h2_2:
                pct_seg_harina = st.number_input("% Segunda Harina:", min_value=0.0, max_value=100.0, value=20.0 if sel_seg_harina != "(Ninguna - Solo harina base)" else 0.0, step=5.0)

            # Agua / Líquido
            c_l1, c_l2 = st.columns([3, 1])
            with c_l1:
                map_liq = {l["nombre"]: l["id"] for l in liquidos_list}
                sel_liquido = st.selectbox("💧 Agua / Líquido Principal:", list(map_liq.keys()) if map_liq else ["Agua Filtrada"])
            with c_l2:
                pct_agua = st.number_input("% Hidratación (Agua):", min_value=40.0, max_value=110.0, value=75.0, step=1.0)

            # Fermento / Masa Madre
            c_f1, c_f2 = st.columns([3, 1])
            with c_f1:
                map_ferm = {f["nombre"]: f["id"] for f in fermentos_list}
                sel_fermento = st.selectbox("🥣 Prefermento / Masa Madre Activa:", list(map_ferm.keys()) if map_ferm else ["Masa Madre Activa 100% Hidratación"])
            with c_f2:
                pct_fermento = st.number_input("% Masa Madre:", min_value=5.0, max_value=50.0, value=20.0, step=1.0)

            # Sal
            c_s1, c_s2 = st.columns([3, 1])
            with c_s1:
                map_sal = {s["nombre"]: s["id"] for s in aditivos_list if "sal" in s["nombre"].lower()}
                opciones_sal = list(map_sal.keys()) if map_sal else [a["nombre"] for a in aditivos_list]
                sel_sal = st.selectbox("🧂 Sal Marina:", opciones_sal if opciones_sal else ["Sal Marina Fina"])
            with c_s2:
                pct_sal = st.number_input("% Sal Marina:", min_value=1.0, max_value=4.0, value=2.0, step=0.1)

            # Aditivo extra opcional (Semillas, Aceite, Dátiles, etc.)
            c_ad1, c_ad2 = st.columns([3, 1])
            with c_ad1:
                map_adit = {a["nombre"]: a["id"] for a in aditivos_list if "sal" not in a["nombre"].lower()}
                opciones_adit = ["(Ninguno)"] + list(map_adit.keys())
                sel_aditivo = st.selectbox("🌰 Aditivo Extra Opcional (Semillas, Frutos, etc.):", opciones_adit)
            with c_ad2:
                pct_aditivo = st.number_input("% del Aditivo Extra:", min_value=0.0, max_value=50.0, value=15.0 if sel_aditivo != "(Ninguno)" else 0.0, step=1.0)

            # Material de Empaque / Bolsa
            c_emp1, c_emp2 = st.columns([3, 1])
            with c_emp1:
                map_emp = {e["nombre"]: e["id"] for e in empaques_list}
                opciones_emp = ["(Ninguno)"] + list(map_emp.keys())
                sel_empaque = st.selectbox("📦 Empaque por Hogaza (opcional):", opciones_emp, index=1 if len(opciones_emp) > 1 else 0)
            with c_emp2:
                cant_empaque = st.number_input("Unidades x pan:", min_value=0.0, max_value=10.0, value=1.0 if sel_empaque != "(Ninguno)" else 0.0, step=1.0)

            submit_receta_completa = st.form_submit_button("🚀 Guardar Receta Completa con sus Ingredientes", type="primary")

            if submit_receta_completa and n_nombre:
                conn = get_connection()
                cur = conn.cursor()
                
                # 1. Guardar receta principal
                cur.execute("""
                INSERT INTO recetas (nombre, descripcion, peso_unitario_crudo, peso_unitario_horneado, precio_venta_sugerido, tiempo_horneado_minutos, temperatura_horno_c)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (n_nombre, n_desc, n_peso_crudo, n_peso_horneado, n_precio_sug, n_tiempo_h, n_temp_h))
                nueva_rec_id = cur.lastrowid

                # Diccionario rápido de IDs por nombre
                cur.execute("SELECT id, nombre FROM ingredientes")
                all_ings_dict = {row["nombre"]: row["id"] for row in cur.fetchall()}

                # 2. Guardar Harina Base (100%)
                if sel_harina_base in all_ings_dict:
                    cur.execute("""
                    INSERT INTO receta_ingredientes (receta_id, ingrediente_id, es_harina_base, porcentaje_panadero, cantidad_fija_por_unidad)
                    VALUES (?, ?, 1, ?, 0)
                    """, (nueva_rec_id, all_ings_dict[sel_harina_base], 100.0 if sel_seg_harina == "(Ninguna - Solo harina base)" else (100.0 - pct_seg_harina)))

                # 3. Guardar Segunda Harina (si aplica)
                if sel_seg_harina != "(Ninguna - Solo harina base)" and sel_seg_harina in all_ings_dict and pct_seg_harina > 0:
                    cur.execute("""
                    INSERT INTO receta_ingredientes (receta_id, ingrediente_id, es_harina_base, porcentaje_panadero, cantidad_fija_por_unidad)
                    VALUES (?, ?, 1, ?, 0)
                    """, (nueva_rec_id, all_ings_dict[sel_seg_harina], pct_seg_harina))

                # 4. Guardar Agua / Líquido
                if sel_liquido in all_ings_dict and pct_agua > 0:
                    cur.execute("""
                    INSERT INTO receta_ingredientes (receta_id, ingrediente_id, es_harina_base, porcentaje_panadero, cantidad_fija_por_unidad)
                    VALUES (?, ?, 0, ?, 0)
                    """, (nueva_rec_id, all_ings_dict[sel_liquido], pct_agua))

                # 5. Guardar Prefermento / Masa Madre
                if sel_fermento in all_ings_dict and pct_fermento > 0:
                    cur.execute("""
                    INSERT INTO receta_ingredientes (receta_id, ingrediente_id, es_harina_base, porcentaje_panadero, cantidad_fija_por_unidad)
                    VALUES (?, ?, 0, ?, 0)
                    """, (nueva_rec_id, all_ings_dict[sel_fermento], pct_fermento))

                # 6. Guardar Sal
                if sel_sal in all_ings_dict and pct_sal > 0:
                    cur.execute("""
                    INSERT INTO receta_ingredientes (receta_id, ingrediente_id, es_harina_base, porcentaje_panadero, cantidad_fija_por_unidad)
                    VALUES (?, ?, 0, ?, 0)
                    """, (nueva_rec_id, all_ings_dict[sel_sal], pct_sal))

                # 7. Guardar Aditivo extra (si aplica)
                if sel_aditivo != "(Ninguno)" and sel_aditivo in all_ings_dict and pct_aditivo > 0:
                    cur.execute("""
                    INSERT INTO receta_ingredientes (receta_id, ingrediente_id, es_harina_base, porcentaje_panadero, cantidad_fija_por_unidad)
                    VALUES (?, ?, 0, ?, 0)
                    """, (nueva_rec_id, all_ings_dict[sel_aditivo], pct_aditivo))

                # 8. Guardar Empaque (si aplica)
                if sel_empaque != "(Ninguno)" and sel_empaque in all_ings_dict and cant_empaque > 0:
                    cur.execute("""
                    INSERT INTO receta_ingredientes (receta_id, ingrediente_id, es_harina_base, porcentaje_panadero, cantidad_fija_por_unidad)
                    VALUES (?, ?, 0, 0, ?)
                    """, (nueva_rec_id, all_ings_dict[sel_empaque], cant_empaque))

                conn.commit()
                conn.close()
                st.success(f"🎉 ¡Receta '{n_nombre}' guardada con éxito con todos sus ingredientes vinculados!")
                st.rerun()

# ==========================================================
# MÓDULO 2: COSTOS Y FIJACIÓN DE PRECIOS
# ==========================================================
elif menu == "💰 2. Costos & Fijación de Precios":
    st.markdown('<div class="main-header">💰 Módulo Financiero de Costos y Rentabilidad</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Cálculo al gramo del costo de producción por tanda y hogaza, simulador de precios y análisis de rentabilidad en COP</div>', unsafe_allow_html=True)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, peso_unitario_crudo, precio_venta_sugerido FROM recetas ORDER BY nombre")
    recetas = cur.fetchall()
    conn.close()

    if not recetas:
        st.warning("No hay recetas disponibles.")
    else:
        rec_map = {r["nombre"]: r for r in recetas}
        
        # 1. Parámetros de la Tanda y Receta
        st.markdown("#### ⚙️ 1. Parámetros de Producción de la Tanda")
        col_sel_rec, col_unidades, col_peso = st.columns([2, 1, 1])
        with col_sel_rec:
            sel_rec_nombre = st.selectbox("Seleccionar Pan / Receta Estandarizada:", list(rec_map.keys()))
            rec_data = rec_map[sel_rec_nombre]
        with col_unidades:
            tanda_unidades = st.number_input("Hogazas en la Tanda:", min_value=1, max_value=500, value=15, step=1, help="Número de unidades producidas en esta hornada/tanda.")
        with col_peso:
            tanda_peso = st.number_input("Peso por pieza en crudo (g):", min_value=100.0, max_value=3000.0, value=float(rec_data["peso_unitario_crudo"]), step=50.0)

        # 2. Cálculo Automático de la Producción
        calc_lote = baker_math.calculate_production_batch(rec_data["id"], tanda_unidades, tanda_peso)

        if calc_lote and calc_lote["costo_total_lote"] > 0:
            costo_total_tanda = calc_lote["costo_total_lote"]
            costo_unitario_pan = calc_lote["costo_por_hogaza"]
            precio_actual_receta = float(rec_data["precio_venta_sugerido"] or 0.0)

            # Análisis del precio actual registrado en la receta
            analisis_actual = baker_math.analyze_manual_price(costo_unitario_pan, precio_actual_receta)

            # 3. Métricas Principales (KPIs)
            st.markdown("---")
            kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
            kpi1.metric("🥖 Costo x Hogaza", baker_math.format_cop(costo_unitario_pan), f"{calc_lote['peso_por_hogaza_g']}g crudo")
            kpi2.metric("🏷️ Costo Total Tanda", baker_math.format_cop(costo_total_tanda), f"{tanda_unidades} hogazas")
            kpi3.metric("💵 Precio Actual Receta", baker_math.format_cop(precio_actual_receta))
            kpi4.metric("📈 Ganancia Actual / Pan", baker_math.format_cop(analisis_actual['ganancia_neta']))
            kpi5.metric("📊 Margen Actual", f"{analisis_actual['margen_sobre_venta_pct']:.1f}%", f"{analisis_actual['factor_multiplicador']}x Costo")

            # 4. Desglose Detallado de Materia Prima y Materiales
            st.markdown("### 📋 Desglose de Costos de Materia Prima y Materiales")
            df_ing = pd.DataFrame(calc_lote["ingredientes"])
            
            def fmt_unit_cost(row):
                if row["unidad"] == "g":
                    return f"{baker_math.format_cop(row['costo_unitario_compra'] * 1000)}/kg ({row['costo_unitario_compra']} $/g)"
                else:
                    return f"{baker_math.format_cop(row['costo_unitario_compra'])} / {row['unidad']}"

            df_ing["Costo Adquisición"] = df_ing.apply(fmt_unit_cost, axis=1)
            df_ing["Cant. por Pan"] = df_ing.apply(lambda r: format_stock_qty(r["gramos_por_hogaza"], r["unidad"]), axis=1)
            df_ing["Total Tanda"] = df_ing.apply(lambda r: format_stock_qty(r["gramos_lote"], r["unidad"]), axis=1)
            df_ing["Costo en Tanda"] = df_ing["costo_linea"].apply(baker_math.format_cop)
            df_ing["Costo por Pan"] = df_ing["costo_por_hogaza"].apply(baker_math.format_cop)
            df_ing["% del Costo"] = df_ing["pct_costo_total"].apply(lambda p: f"{p:.1f}%")

            st.dataframe(
                df_ing[["nombre", "Cant. por Pan", "Total Tanda", "Costo Adquisición", "Costo por Pan", "Costo en Tanda", "% del Costo"]].rename(
                    columns={
                        "nombre": "Insumo / Material",
                        "Cant. por Pan": "Porción x Pan",
                        "Total Tanda": f"Total Tanda ({tanda_unidades} u)",
                        "Costo Adquisición": "Costo de Adquisición",
                        "Costo por Pan": "Costo x Pan (COP)",
                        "Costo en Tanda": "Costo Tanda (COP)",
                        "% del Costo": "% Participación"
                    }
                ),
                column_config={
                    "Insumo / Material": st.column_config.TextColumn("Insumo / Material"),
                    "Porción x Pan": st.column_config.TextColumn("Porción x Pan"),
                    f"Total Tanda ({tanda_unidades} u)": st.column_config.TextColumn(f"Total Tanda ({tanda_unidades} u)"),
                    "Costo de Adquisición": st.column_config.TextColumn("Costo de Adquisición"),
                    "Costo x Pan (COP)": st.column_config.TextColumn("Costo x Pan (COP)"),
                    "Costo Tanda (COP)": st.column_config.TextColumn("Costo Tanda (COP)"),
                    "% Participación": st.column_config.TextColumn("% Participación")
                },
                use_container_width=True
            )

            st.markdown("---")
            
            # 5. Fijación y Simulación de Precios de Venta
            col_sugerencia, col_manual = st.columns([1, 1], gap="large")

            with col_sugerencia:
                st.markdown("### 🧮 Sugerencia Automática de Precio de Venta")
                st.caption("Calcula el precio óptimo a partir de tu margen deseado o factor multiplicador.")

                metodo_fijacion = st.radio(
                    "Estrategia de Fijación de Ganancia:",
                    [
                        "✖️ Factor Multiplicador de Costo (ej: 2.5x, 3.0x, 3.5x)",
                        "📊 Margen Porcentual sobre Precio de Venta (%)",
                        "📈 Markup Porcentual sobre Costo de Producción (%)",
                        "💵 Ganancia Neta Fija Deseada ($ COP / pan)"
                    ]
                )

                if "Factor Multiplicador" in metodo_fijacion:
                    val_param = st.slider("Factor Multiplicador (Costo × Factor):", min_value=1.5, max_value=6.0, value=3.0, step=0.1, help="Ejemplo: Factor 3.0x significa que el precio es 3 veces el costo de producción.")
                    tipo_param = "factor_multiplicador"
                elif "Margen Porcentual" in metodo_fijacion:
                    val_param = st.slider("Margen de Ganancia deseado sobre Venta (%):", min_value=15, max_value=85, value=65, step=5, help="Porcentaje del precio final de venta que te queda como ganancia bruta.")
                    tipo_param = "porcentual_margen"
                elif "Markup Porcentual" in metodo_fijacion:
                    val_param = st.slider("Markup sobre el Costo (%):", min_value=50, max_value=500, value=200, step=10, help="Porcentaje adicional que le sumas al costo unitario.")
                    tipo_param = "porcentual_markup"
                else:
                    val_param = st.number_input("Ganancia neta fija deseada por hogaza ($ COP):", min_value=1000, max_value=100000, value=15000, step=1000)
                    tipo_param = "monto_fijo"

                calc_sug = baker_math.calculate_pricing(costo_unitario_pan, tipo_param, val_param)
                precio_sug = calc_sug["precio_venta"]
                ganancia_sug = calc_sug["ganancia_por_unidad"]
                ganancia_tanda_sug = ganancia_sug * tanda_unidades

                st.markdown(f"""
                <div style="background-color: #F8FAFC; border: 1.5px solid #CBD5E1; border-radius: 10px; padding: 15px; margin-top: 10px;">
                    <div style="font-size: 0.85rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Precio de Venta Sugerido:</div>
                    <div style="font-size: 2.1rem; color: #991B1B; font-weight: 800; margin: 4px 0;">{baker_math.format_cop(precio_sug)}</div>
                    <div style="display: flex; gap: 15px; margin-top: 10px; font-size: 0.95rem;">
                        <div><b>Ganancia x Pan:</b> <span style="color: #16A34A; font-weight: 700;">+{baker_math.format_cop(ganancia_sug)}</span></div>
                        <div><b>Margen:</b> <span style="color: #0284C7; font-weight: 700;">{calc_sug['margen_real_pct']}%</span></div>
                        <div><b>Multiplicador:</b> <span style="font-weight: 700;">{calc_sug['factor_multiplicador']}x</span></div>
                    </div>
                    <div style="margin-top: 8px; font-size: 0.9rem; color: #475569;">
                        <b>Utilidad Proyectada Tanda ({tanda_unidades} panes):</b> <span style="color: #16A34A; font-weight: 700;">+{baker_math.format_cop(ganancia_tanda_sug)}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("💾 Fijar Precio Sugerido como Oficial de la Receta", key="btn_fijar_sugerido", type="primary"):
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("UPDATE recetas SET precio_venta_sugerido = ? WHERE id = ?", (precio_sug, rec_data["id"]))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Precio oficial de {baker_math.format_cop(precio_sug)} guardado para {sel_rec_nombre}.")
                    st.rerun()

            with col_manual:
                st.markdown("### 🎯 Simulador de Precio de Venta Fijo Manual")
                st.caption("Ingresa un precio de venta fijo y evalúa en tiempo real tu ganancia neta y margen.")

                precio_manual_input = st.number_input(
                    "Ingresa el Precio de Venta a Evaluar ($ COP / pan):",
                    min_value=500,
                    max_value=200000,
                    value=int(precio_actual_receta) if precio_actual_receta > 500 else 22000,
                    step=500,
                    help="Escribe el precio de venta al público que deseas analizar."
                )

                analisis_manual = baker_math.analyze_manual_price(costo_unitario_pan, precio_manual_input)
                ganancia_manual_tanda = analisis_manual["ganancia_neta"] * tanda_unidades

                st.markdown(f"""
                <div style="background-color: {analisis_manual['color_fondo']}; border: 1.5px solid {analisis_manual['color_borde']}; border-radius: 10px; padding: 15px; margin-top: 10px;">
                    <div style="font-size: 0.95rem; font-weight: 700; color: {analisis_manual['color_texto']}; display: flex; align-items: center; justify-content: space-between;">
                        <span>{analisis_manual['semaforo']}</span>
                        <span style="font-size: 1.3rem; font-weight: 800;">{baker_math.format_cop(analisis_manual['precio_manual'])}</span>
                    </div>
                    <p style="font-size: 0.85rem; color: {analisis_manual['color_texto']}; margin: 6px 0 12px 0;">{analisis_manual['mensaje']}</p>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; background: white; border-radius: 8px; padding: 10px;">
                        <div>
                            <span style="font-size: 0.8rem; color: #64748B;">Ganancia Neta x Pan:</span><br>
                            <b style="font-size: 1.05rem; color: {'#16A34A' if analisis_manual['ganancia_neta'] > 0 else '#DC2626'};">
                                {baker_math.format_cop(analisis_manual['ganancia_neta'])}
                            </b>
                        </div>
                        <div>
                            <span style="font-size: 0.8rem; color: #64748B;">Margen Real sobre Venta:</span><br>
                            <b style="font-size: 1.05rem; color: #0284C7;">{analisis_manual['margen_sobre_venta_pct']}%</b>
                        </div>
                        <div>
                            <span style="font-size: 0.8rem; color: #64748B;">Markup sobre Costo:</span><br>
                            <b style="font-size: 1.05rem; color: #475569;">+{analisis_manual['markup_sobre_costo_pct']}%</b>
                        </div>
                        <div>
                            <span style="font-size: 0.8rem; color: #64748B;">Factor Multiplicador:</span><br>
                            <b style="font-size: 1.05rem; color: #475569;">{analisis_manual['factor_multiplicador']}x Costo</b>
                        </div>
                    </div>
                    <div style="margin-top: 10px; font-size: 0.9rem; color: {analisis_manual['color_texto']};">
                        <b>Ganancia Total Tanda ({tanda_unidades} panes):</b> <b>{baker_math.format_cop(ganancia_manual_tanda)}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("💾 Guardar este Precio Manual como Oficial de la Receta", key="btn_fijar_manual"):
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("UPDATE recetas SET precio_venta_sugerido = ? WHERE id = ?", (precio_manual_input, rec_data["id"]))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Precio oficial de {baker_math.format_cop(precio_manual_input)} guardado para {sel_rec_nombre}.")
                    st.rerun()
        else:
            st.info("Esta receta aún no tiene ingredientes vinculados o los costos están en cero. Puedes agregarle ingredientes en el Módulo 1 o actualizar costos en el Módulo 3.")

# ==========================================================
# MÓDULO 3: INVENTARIO Y MATERIA PRIMA
# ==========================================================
elif menu == "📦 3. Inventario & Materia Prima":
    st.markdown('<div class="main-header">📦 Inventario & Materia Prima</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Control de existencias, compras, alerta de mínimos y descuento automático</div>', unsafe_allow_html=True)

    # Mensaje de confirmación visual persistente al agregar stock
    if "ultimo_reabastecimiento" in st.session_state:
        info_r = st.session_state["ultimo_reabastecimiento"]
        st.markdown(f"""
        <div class="success-stock-banner">
            <h4 style="margin: 0 0 5px 0; color: #065F46;">✅ ¡Entrada de Insumo Registrada con Éxito!</h4>
            <b>Insumo:</b> {info_r['insumo']}<br>
            <b>Cantidad Añadida:</b> +{info_r['cantidad']:,.1f} {info_r['unidad']}<br>
            <b>Stock Anterior:</b> {info_r['stock_antiguo']:,.1f} {info_r['unidad']} ➔ <b>Nuevo Stock Actualizado:</b> <span style="font-size: 1.1rem; color: #047857; font-weight: 700;">{info_r['nuevo_stock']:,.1f} {info_r['unidad']}</span><br>
            <span style="font-size: 0.85rem; color: #047857;">Referencia: {info_r['referencia']}</span>
        </div>
        """, unsafe_allow_html=True)

    # Alertas visibles de stock mínimo
    alertas = baker_math.get_low_stock_alerts()
    if alertas:
        st.markdown(f'<div class="stock-alert">⚠️ <b>ALERTA DE REABASTECIMIENTO:</b> Hay {len(alertas)} insumo(s) en o por debajo del stock mínimo.</div>', unsafe_allow_html=True)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ingredientes ORDER BY categoria, nombre")
    ingredientes = cur.fetchall()
    
    # Consultar últimos 5 movimientos de entrada
    cur.execute("""
    SELECT m.fecha, i.nombre as insumo, m.cantidad, i.unidad_medida, m.referencia
    FROM movimientos_inventario m
    JOIN ingredientes i ON m.ingrediente_id = i.id
    WHERE m.tipo_movimiento = 'ENTRADA_COMPRA'
    ORDER BY m.id DESC LIMIT 5
    """)
    ultimas_entradas = cur.fetchall()
    conn.close()

    df_stock = pd.DataFrame([dict(i) for i in ingredientes])
    
    def calcular_estado(row):
        if row["stock_actual"] <= 0:
            return "🔴 Agotado"
        elif row["stock_actual"] <= row["stock_minimo"]:
            return "🟡 Stock Bajo"
        return "🟢 Normal"

    df_stock["Estado"] = df_stock.apply(calcular_estado, axis=1)
    df_stock["Costo COP"] = df_stock["costo_unitario"].apply(baker_math.format_cop)
    df_stock["Costo Referencia"] = df_stock.apply(
        lambda r: f"{baker_math.format_cop(r['costo_unitario'] * 1000)} / kg" if r["unidad_medida"] == "g" else f"{baker_math.format_cop(r['costo_unitario'])} / {r['unidad_medida']}",
        axis=1
    )
    df_stock["id_limpio"] = df_stock["id"].apply(clean_phone_or_code)
    df_stock["Stock Actual Formateado"] = df_stock.apply(lambda r: format_stock_qty(r["stock_actual"], r["unidad_medida"]), axis=1)
    df_stock["Stock Mínimo Formateado"] = df_stock.apply(lambda r: format_stock_qty(r["stock_minimo"], r["unidad_medida"]), axis=1)

    st.markdown("### 📋 Existencias y Costos de Compra en Bodega")
    st.dataframe(
        df_stock[["id_limpio", "nombre", "categoria", "Stock Actual Formateado", "Stock Mínimo Formateado", "unidad_medida", "Costo Referencia", "Estado"]].rename(
            columns={
                "id_limpio": "ID", "nombre": "Insumo / Material", "categoria": "Categoría",
                "Stock Actual Formateado": "Stock Actual", "Stock Mínimo Formateado": "Stock Mínimo",
                "unidad_medida": "Unidad", "Costo Referencia": "Costo de Compra (Kilo / Unidad)",
                "Estado": "Estado"
            }
        ),
        column_config={
            "ID": st.column_config.TextColumn("ID"),
            "Insumo / Material": st.column_config.TextColumn("Insumo / Material"),
            "Categoría": st.column_config.TextColumn("Categoría"),
            "Stock Actual": st.column_config.TextColumn("Stock Actual"),
            "Stock Mínimo": st.column_config.TextColumn("Stock Mínimo"),
            "Unidad": st.column_config.TextColumn("Unidad"),
            "Costo de Compra (Kilo / Unidad)": st.column_config.TextColumn("Costo de Compra (Kilo / Unidad)"),
            "Estado": st.column_config.TextColumn("Estado")
        },
        use_container_width=True
    )

    # ==========================================================
    # ACTUALIZADOR RÁPIDO DE COSTOS DE MATERIA PRIMA Y MATERIALES
    # ==========================================================
    st.markdown("---")
    st.markdown("### 💵 Actualizador de Costos de Materia Prima y Materiales")
    st.caption("Modifica o actualiza el costo de adquisición de cualquier harina, empaque (bolsas, etiquetas) o servicios proporcionales (gas/energía).")

    with st.form("form_actualizador_costos_insumo"):
        ing_dict_costos = {i["nombre"]: i for i in ingredientes}
        sel_insumo_costo = st.selectbox("Seleccionar Insumo o Material a Actualizar:", list(ing_dict_costos.keys()), key="sel_ins_costo_rapido")
        obj_insumo = ing_dict_costos[sel_insumo_costo]
        
        unidad_ins = obj_insumo["unidad_medida"]
        costo_act = float(obj_insumo["costo_unitario"])
        
        c_cost1, c_cost2 = st.columns([1, 2])
        
        with c_cost1:
            st.info(f"**Insumo:** {obj_insumo['nombre']}\n\n**Categoría:** {obj_insumo['categoria']}\n\n**Unidad:** {unidad_ins}\n\n**Costo Actual Registrado:**\n\n### {baker_math.format_cop(costo_act * 1000 if unidad_ins == 'g' else costo_act)} {'/ kg' if unidad_ins == 'g' else 'por ' + unidad_ins}")
            
        with c_cost2:
            if unidad_ins == "g":
                modo_ingreso = st.radio(
                    "¿Cómo compras este insumo?",
                    ["Precio por Kilo ($ COP / kg)", "Precio por Bulto / Saco ($ COP)", "Precio por Gramo directo ($ COP / g)"],
                    horizontal=True
                )
                if "por Kilo" in modo_ingreso:
                    precio_kg = st.number_input("Precio de compra por Kilo ($ COP):", min_value=100.0, value=float(max(500.0, costo_act * 1000.0)), step=100.0, help="Ej: $4.500 COP por un kilo de harina de fuerza")
                    costo_calculado_gramo = precio_kg / 1000.0
                    st.caption(f"➔ Equivale a: **{costo_calculado_gramo:g} COP por gramo** (se usará en el costeo automático de recetas)")
                elif "por Bulto" in modo_ingreso:
                    c_b1, c_b2 = st.columns(2)
                    with c_b1:
                        precio_bulto = st.number_input("Precio del Bulto / Saco ($ COP):", min_value=1000.0, value=120000.0, step=1000.0, help="Ej: $120.000 COP por el bulto")
                    with c_b2:
                        kilos_bulto = st.number_input("Kilos del Bulto / Saco (kg):", min_value=1.0, value=25.0, step=1.0, help="Peso total del saco en kg (ej: 25 kg o 50 kg)")
                    costo_calculado_gramo = precio_bulto / (kilos_bulto * 1000.0) if kilos_bulto > 0 else 0.0
                    st.caption(f"➔ Equivale a: **{baker_math.format_cop(precio_bulto / kilos_bulto)} por kilo** ({costo_calculado_gramo:g} COP por gramo)")
                else:
                    costo_calculado_gramo = st.number_input("Precio por Gramo directo ($ COP / g):", min_value=0.01, value=float(max(0.1, costo_act)), step=0.5)
            else:
                costo_calculado_gramo = st.number_input(f"Precio de compra por {unidad_ins} ($ COP):", min_value=1.0, value=float(max(10.0, costo_act)), step=50.0, help="Ej: $1.200 por bolsa de papel kraft, $350 por etiqueta, $1.500 por gas/energía por pan")

            btn_act_costo = st.form_submit_button("💾 Guardar y Actualizar Costo de Compra", type="primary")
            if btn_act_costo:
                from database import update_ingredient_cost
                update_ingredient_cost(obj_insumo["id"], costo_calculado_gramo)
                st.success(f"✅ ¡Costo actualizado para '{obj_insumo['nombre']}'! Nuevo valor: {baker_math.format_cop(costo_calculado_gramo * 1000 if unidad_ins == 'g' else costo_calculado_gramo)} {'/ kg' if unidad_ins == 'g' else 'por ' + unidad_ins}")
                st.rerun()

    st.markdown("---")
    col_inv1, col_inv2 = st.columns(2)

    with col_inv1:
        st.markdown("### 📥 Entrada de Insumos (Registrar Compra)")
        with st.form("form_entrada_stock"):
            ing_map_nombres = {i["nombre"]: i for i in ingredientes}
            sel_ing_compra = st.selectbox("Seleccionar Insumo:", list(ing_map_nombres.keys()))
            insumo_obj = ing_map_nombres[sel_ing_compra]
            
            cant_ing_compra = st.number_input(f"Cantidad a sumar ({insumo_obj['unidad_medida']}):", min_value=0.1, value=10000.0, step=1000.0)
            
            # Helper de costo de compra
            if insumo_obj["unidad_medida"] == "g":
                costo_kg_default = float(insumo_obj["costo_unitario"] * 1000.0)
                nuevo_costo_kg = st.number_input("Costo de compra por Kilo en COP (actualizar si cambió):", min_value=0.0, value=costo_kg_default, step=100.0)
                nuevo_costo = nuevo_costo_kg / 1000.0 if nuevo_costo_kg > 0 else 0.0
            else:
                nuevo_costo = st.number_input(f"Costo por {insumo_obj['unidad_medida']} en COP (actualizar si cambió):", min_value=0.0, value=float(insumo_obj["costo_unitario"]), step=50.0)
            
            referencia_compra = st.text_input("Nota / Factura de Proveedor:", value="Compra semanal molino")

            submit_compra = st.form_submit_button("✅ Registrar Entrada y Actualizar Stock", type="primary")
            if submit_compra:
                stock_ant = insumo_obj["stock_actual"]
                nuevo_stock = stock_ant + cant_ing_compra
                
                conn = get_connection()
                cur = conn.cursor()
                if nuevo_costo > 0:
                    cur.execute("UPDATE ingredientes SET stock_actual = stock_actual + ?, costo_unitario = ? WHERE id = ?", (cant_ing_compra, nuevo_costo, insumo_obj["id"]))
                else:
                    cur.execute("UPDATE ingredientes SET stock_actual = stock_actual + ? WHERE id = ?", (cant_ing_compra, insumo_obj["id"]))
                
                cur.execute("""
                INSERT INTO movimientos_inventario (ingrediente_id, tipo_movimiento, cantidad, referencia)
                VALUES (?, 'ENTRADA_COMPRA', ?, ?)
                """, (insumo_obj["id"], cant_ing_compra, referencia_compra))
                conn.commit()
                conn.close()

                st.session_state["ultimo_reabastecimiento"] = {
                    "insumo": sel_ing_compra,
                    "cantidad": cant_ing_compra,
                    "unidad": insumo_obj["unidad_medida"],
                    "stock_antiguo": stock_ant,
                    "nuevo_stock": nuevo_stock,
                    "referencia": referencia_compra
                }
                st.rerun()

    with col_inv2:
        st.markdown("### ➕ Registrar Nuevo Insumo o Material")
        with st.form("form_nuevo_insumo"):
            n_insumo_nombre = st.text_input("Nombre del Insumo / Material (ej: Harina Integral Orgánica, Bolsa Kraft, Etiquetas)")
            n_cat = st.selectbox("Categoría:", ["harina", "liquido", "fermento", "aditivo", "empaque", "servicio"])
            n_unidad = st.selectbox("Unidad de Medida:", ["g", "kg", "unidad", "ml"])
            c_s1, c_s2 = st.columns(2)
            with c_s1:
                n_stock_ini = st.number_input("Stock Inicial:", min_value=0.0, value=25000.0 if n_unidad == "g" else 100.0, step=100.0)
            with c_s2:
                n_stock_min = st.number_input("Stock Mínimo Alerta:", min_value=0.0, value=5000.0 if n_unidad == "g" else 20.0, step=10.0)
            
            if n_unidad == "g":
                n_costo_kg = st.number_input("Costo de compra por Kilo ($ COP / kg):", min_value=0.0, value=5000.0, step=100.0)
                n_costo_u = n_costo_kg / 1000.0
            else:
                n_costo_u = st.number_input(f"Costo por {n_unidad} en COP ($):", min_value=0.0, value=1200.0, step=50.0)

            submit_insumo = st.form_submit_button("Crear Insumo / Material")
            if submit_insumo and n_insumo_nombre:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                INSERT INTO ingredientes (nombre, categoria, unidad_medida, stock_actual, stock_minimo, costo_unitario)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (n_insumo_nombre, n_cat, n_unidad, n_stock_ini, n_stock_min, n_costo_u))
                conn.commit()
                conn.close()
                st.success(f"Insumo '{n_insumo_nombre}' registrado.")
                st.rerun()

    # Tabla de últimos movimientos de compra
    if ultimas_entradas:
        st.markdown("---")
        st.markdown("#### 📜 Registro de Últimas Entradas de Insumos")
        df_ue = pd.DataFrame([dict(e) for e in ultimas_entradas])
        df_ue["Cantidad Formateada"] = df_ue.apply(lambda r: "+" + format_stock_qty(r["cantidad"], r["unidad_medida"]), axis=1)
        st.dataframe(
            df_ue[["fecha", "insumo", "Cantidad Formateada", "unidad_medida", "referencia"]].rename(
                columns={"fecha": "Fecha y Hora", "insumo": "Insumo", "Cantidad Formateada": "Cantidad Ingresada", "unidad_medida": "Unidad", "referencia": "Referencia"}
            ),
            column_config={
                "Fecha y Hora": st.column_config.TextColumn("Fecha y Hora"),
                "Insumo": st.column_config.TextColumn("Insumo"),
                "Cantidad Ingresada": st.column_config.TextColumn("Cantidad Ingresada"),
                "Unidad": st.column_config.TextColumn("Unidad"),
                "Referencia": st.column_config.TextColumn("Referencia")
            },
            use_container_width=True
        )

# ==========================================================
# MÓDULO 4: GESTIÓN DE PEDIDOS Y LOTES (PREVENTA)
# ==========================================================
elif menu == "📋 4. Pedidos & Preventa (Lotes)":
    st.markdown('<div class="main-header">📋 Pedidos & Preventa de Lotes</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Edición y eliminación de pedidos, gestión de lotes y clientes separados (Mayoristas / Minoristas)</div>', unsafe_allow_html=True)

    tab_lotes, tab_pedidos, tab_clientes = st.tabs(["🔥 Lotes de Producción", "🛒 Gestión de Pedidos (Editar/Eliminar)", "👥 Directorio de Clientes"])

    # 1. LOTES
    with tab_lotes:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
        SELECT l.*, r.nombre as receta_nombre,
               (SELECT COUNT(*) FROM pedidos p WHERE p.lote_id = l.id) as total_pedidos,
               (SELECT COALESCE(SUM(p.unidades), 0) FROM pedidos p WHERE p.lote_id = l.id) as unidades_reservadas
        FROM lotes_produccion l
        JOIN recetas r ON l.receta_id = r.id
        ORDER BY l.fecha_horneado DESC
        """)
        lotes = cur.fetchall()
        conn.close()

        if not lotes:
            st.info("No hay lotes creados. Puedes crearlos desde la Calculadora de Producción.")
        else:
            for lote in lotes:
                with st.expander(f"🍞 Lote {lote['codigo_lote']} - {lote['receta_nombre']} ({lote['fecha_horneado']}) - Estado: {lote['estado']}"):
                    c1, c2, c3, c4 = st.columns(4)
                    c1.write(f"**Programado:** {int(lote['unidades_programadas'])} hogazas ({lote['peso_hogaza_g']:g}g)")
                    c2.write(f"**Reservado en preventa:** {int(lote['unidades_reservadas'])} hogazas")
                    c3.write(f"**Costo Estimado Lote:** {baker_math.format_cop(lote['costo_total_lote'])}")
                    c4.write(f"**Inventario:** {'✅ Descontado' if lote['inventario_descontado'] == 1 else '❌ Pendiente'}")

                    col_accion1, col_accion2 = st.columns(2)
                    with col_accion1:
                        nuevo_estado = st.selectbox(
                            f"Cambiar Estado Lote {lote['codigo_lote']}:",
                            ["PLANIFICADO", "EN_FERMENTACION", "HORNEADO", "FINALIZADO"],
                            index=["PLANIFICADO", "EN_FERMENTACION", "HORNEADO", "FINALIZADO"].index(lote["estado"]),
                            key=f"estado_lote_{lote['id']}"
                        )
                        if st.button("Guardar Estado Lote", key=f"btn_est_lote_{lote['id']}"):
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute("UPDATE lotes_produccion SET estado = ? WHERE id = ?", (nuevo_estado, lote["id"]))
                            conn.commit()
                            conn.close()
                            st.success(f"Estado actualizado a {nuevo_estado}.")
                            st.rerun()

                    with col_accion2:
                        if lote["inventario_descontado"] == 0:
                            if st.button("📉 Descontar Ingredientes de Bodega", type="secondary", key=f"desc_inv_{lote['id']}"):
                                ok, msg = baker_math.discount_inventory_for_batch(lote["id"])
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                        else:
                            st.info("Insumos de este lote ya descontados.")

    # 2. PEDIDOS (CON EDICIÓN Y ELIMINACIÓN)
    with tab_pedidos:
        st.markdown("### 🛒 Listado de Pedidos Activos")
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
        SELECT p.*, c.nombre as cliente_nombre, c.telefono as cliente_telefono, c.tipo_cliente, r.nombre as pan_nombre, l.codigo_lote
        FROM pedidos p
        JOIN clientes c ON p.cliente_id = c.id
        JOIN recetas r ON p.receta_id = r.id
        LEFT JOIN lotes_produccion l ON p.lote_id = l.id
        ORDER BY p.fecha_entrega DESC, p.id DESC
        """)
        pedidos = cur.fetchall()

        cur.execute("SELECT id, nombre, tipo_cliente FROM clientes ORDER BY nombre")
        todos_clientes = cur.fetchall()
        cur.execute("SELECT id, nombre, precio_venta_sugerido FROM recetas ORDER BY nombre")
        todas_recetas = cur.fetchall()
        cur.execute("SELECT id, codigo_lote FROM lotes_produccion ORDER BY id DESC")
        todos_lotes = cur.fetchall()
        conn.close()

        if not pedidos:
            st.info("No hay pedidos registrados.")
        else:
            for p in pedidos:
                badge_tipo = "badge-mayorista" if p["tipo_cliente"] == "Mayorista" else "badge-minorista"
                with st.container():
                    col_info, col_est, col_acc = st.columns([3, 1.5, 1.5])
                    with col_info:
                        tel_display = f" ({clean_phone_or_code(p['cliente_telefono'])})" if p['cliente_telefono'] else ""
                        st.markdown(f"**Pedido #{clean_phone_or_code(p['id'])} - {p['cliente_nombre']}**{tel_display} <span class='badge-tag {badge_tipo}'>{p['tipo_cliente']}</span>", unsafe_allow_html=True)
                        st.markdown(f"🥖 **{int(p['unidades'])}x {p['pan_nombre']}** | 📅 Entrega: **{p['fecha_entrega']}** | Lote: `{p['codigo_lote'] or 'Sin asignar'}`")
                        nota_str = f" | Nota: {p['notas']}" if p["notas"] else ""
                        st.markdown(f"💰 Total: **{baker_math.format_cop(p['total_cobrado'])}** ({p['metodo_pago']}){nota_str}")
                    
                    with col_est:
                        estados_pedido = ["REGISTRADO", "PAGADO", "EN_FERMENTACION", "HORNEADO", "ENTREGADO"]
                        idx_est = estados_pedido.index(p["estado"]) if p["estado"] in estados_pedido else 0
                        sel_est = st.selectbox("Estado:", estados_pedido, index=idx_est, key=f"ped_est_quick_{p['id']}")
                        if sel_est != p["estado"]:
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute("UPDATE pedidos SET estado = ? WHERE id = ?", (sel_est, p["id"]))
                            conn.commit()
                            conn.close()
                            st.success(f"Pedido #{p['id']} actualizado.")
                            st.rerun()

                    with col_acc:
                        st.write("")
                        # Botón para abrir modal de edición / eliminación
                        exp_edit = st.expander(f"⚙️ Modificar #{p['id']}")
                        with exp_edit:
                            st.markdown(f"**Editar Pedido #{p['id']}**")
                            with st.form(f"form_edit_ped_{p['id']}"):
                                c_map_edit = {c["nombre"]: c["id"] for c in todos_clientes}
                                r_map_edit = {r["nombre"]: r["id"] for r in todas_recetas}
                                l_map_edit = {l["codigo_lote"]: l["id"] for l in todos_lotes}
                                l_map_edit["(Sin lote)"] = None

                                # Valores actuales
                                default_c_idx = list(c_map_edit.values()).index(p["cliente_id"]) if p["cliente_id"] in c_map_edit.values() else 0
                                default_r_idx = list(r_map_edit.values()).index(p["receta_id"]) if p["receta_id"] in r_map_edit.values() else 0
                                default_l_idx = list(l_map_edit.values()).index(p["lote_id"]) if p["lote_id"] in l_map_edit.values() else 0

                                ed_cliente = st.selectbox("Cliente:", list(c_map_edit.keys()), index=default_c_idx)
                                ed_receta = st.selectbox("Pan:", list(r_map_edit.keys()), index=default_r_idx)
                                ed_lote = st.selectbox("Lote:", list(l_map_edit.keys()), index=default_l_idx)
                                ed_cant = st.number_input("Unidades:", min_value=1, value=int(p["unidades"]), step=1)
                                ed_precio = st.number_input("Total Cobrado (COP):", min_value=0.0, value=float(p["total_cobrado"]), step=1000.0)
                                ed_fecha = st.date_input("Fecha Entrega:", value=datetime.strptime(p["fecha_entrega"], "%Y-%m-%d").date())
                                ed_pago = st.selectbox("Método de Pago:", ["Transferencia", "Efectivo", "Tarjeta"], index=["Transferencia", "Efectivo", "Tarjeta"].index(p["metodo_pago"]) if p["metodo_pago"] in ["Transferencia", "Efectivo", "Tarjeta"] else 0)
                                ed_notas = st.text_input("Notas:", value=p["notas"] or "")

                                btn_guardar_ed = st.form_submit_button("💾 Guardar Cambios")
                                if btn_guardar_ed:
                                    conn = get_connection()
                                    cur = conn.cursor()
                                    cur.execute("""
                                    UPDATE pedidos 
                                    SET cliente_id = ?, receta_id = ?, lote_id = ?, unidades = ?, total_cobrado = ?, fecha_entrega = ?, metodo_pago = ?, notas = ?
                                    WHERE id = ?
                                    """, (c_map_edit[ed_cliente], r_map_edit[ed_receta], l_map_edit[ed_lote], ed_cant, ed_precio, ed_fecha.strftime("%Y-%m-%d"), ed_pago, ed_notas, p["id"]))
                                    conn.commit()
                                    conn.close()
                                    st.success(f"Pedido #{p['id']} modificado con éxito.")
                                    st.rerun()

                            st.markdown("---")
                            st.write("⚠️ **Zona de peligro:**")
                            if st.button(f"🗑️ Eliminar Definitivamente #{p['id']}", key=f"btn_del_ped_{p['id']}", type="secondary"):
                                conn = get_connection()
                                cur = conn.cursor()
                                cur.execute("DELETE FROM pedidos WHERE id = ?", (p["id"],))
                                conn.commit()
                                conn.close()
                                st.warning(f"Pedido #{p['id']} eliminado.")
                                st.rerun()

                    st.divider()

        # Formulario para Nuevo Pedido
        with st.expander("➕ Registrar Nuevo Pedido"):
            with st.form("form_nuevo_pedido"):
                c_map = {f"{c['nombre']} ({c['tipo_cliente']})": c["id"] for c in todos_clientes}
                r_map = {r["nombre"]: (r["id"], r["precio_venta_sugerido"]) for r in todas_recetas}
                l_map = {l["codigo_lote"]: l["id"] for l in todos_lotes}
                l_map["(Sin lote asignado)"] = None

                np_cliente = st.selectbox("Cliente:", list(c_map.keys()))
                np_pan = st.selectbox("Pan Solicitado:", list(r_map.keys()))
                np_lote = st.selectbox("Asignar a Lote de Horneado:", list(l_map.keys()))
                
                cp1, cp2, cp3 = st.columns(3)
                with cp1:
                    np_cant = st.number_input("Unidades:", min_value=1, value=1, step=1)
                with cp2:
                    precio_sug = r_map[np_pan][1]
                    np_total = st.number_input("Total a Cobrar en COP ($):", min_value=0.0, value=float(precio_sug * np_cant), step=1000.0)
                with cp3:
                    np_pago = st.selectbox("Método de Pago:", ["Transferencia", "Efectivo", "Tarjeta"])

                np_fecha = st.date_input("Fecha de Entrega:", value=date.today())
                np_notas = st.text_input("Notas de entrega (ej: rebanado, recoger en obrador)")

                submit_pedido = st.form_submit_button("Guardar Pedido", type="primary")
                if submit_pedido:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("""
                    INSERT INTO pedidos (cliente_id, lote_id, receta_id, unidades, fecha_entrega, estado, total_cobrado, metodo_pago, notas)
                    VALUES (?, ?, ?, ?, ?, 'REGISTRADO', ?, ?, ?)
                    """, (c_map[np_cliente], l_map[np_lote], r_map[np_pan][0], np_cant, np_fecha.strftime("%Y-%m-%d"), np_total, np_pago, np_notas))
                    conn.commit()
                    conn.close()
                    st.success("¡Pedido registrado exitosamente!")
                    st.rerun()

    # 3. CLIENTES SEPARADOS (MAYORISTAS VS MINORISTAS)
    with tab_clientes:
        st.markdown("### 👥 Directorio de Clientes Organizado")
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM clientes ORDER BY nombre")
        clientes_todos = cur.fetchall()
        conn.close()

        clientes_min = [dict(c) for c in clientes_todos if c["tipo_cliente"] == "Minorista"]
        clientes_may = [dict(c) for c in clientes_todos if c["tipo_cliente"] == "Mayorista"]

        subtab_min, subtab_may = st.tabs([f"🛒 Particulares / Minoristas ({len(clientes_min)})", f"🏢 Clientes al Por Mayor / B2B ({len(clientes_may)})"])

        with subtab_min:
            st.markdown("#### Clientes Particulares (Hogares y Consumo Individual)")
            if clientes_min:
                df_min = pd.DataFrame(clientes_min)
                df_min["telefono_limpio"] = df_min["telefono"].apply(clean_phone_or_code)
                st.dataframe(
                    df_min[["nombre", "telefono_limpio", "direccion", "preferencias"]].rename(
                        columns={"nombre": "Nombre", "telefono_limpio": "Teléfono / WhatsApp", "direccion": "Dirección", "preferencias": "Preferencias de Pan"}
                    ),
                    column_config={
                        "Nombre": st.column_config.TextColumn("Nombre"),
                        "Teléfono / WhatsApp": st.column_config.TextColumn("Teléfono / WhatsApp"),
                        "Dirección": st.column_config.TextColumn("Dirección"),
                        "Preferencias de Pan": st.column_config.TextColumn("Preferencias de Pan")
                    },
                    use_container_width=True
                )
            else:
                st.info("No hay clientes minoristas registrados.")

        with subtab_may:
            st.markdown("#### Clientes al Por Mayor (Cafeterías, Bistrós, Restaurantes, Hoteles)")
            if clientes_may:
                df_may = pd.DataFrame(clientes_may)
                df_may["telefono_limpio"] = df_may["telefono"].apply(clean_phone_or_code)
                st.dataframe(
                    df_may[["nombre", "telefono_limpio", "direccion", "preferencias"]].rename(
                        columns={"nombre": "Razón Social / Nombre", "telefono_limpio": "Contacto / WhatsApp", "direccion": "Dirección de Entrega", "preferencias": "Condiciones / Preferencias Comerciales"}
                    ),
                    column_config={
                        "Razón Social / Nombre": st.column_config.TextColumn("Razón Social / Nombre"),
                        "Contacto / WhatsApp": st.column_config.TextColumn("Contacto / WhatsApp"),
                        "Dirección de Entrega": st.column_config.TextColumn("Dirección de Entrega"),
                        "Condiciones / Preferencias Comerciales": st.column_config.TextColumn("Condiciones / Preferencias Comerciales")
                    },
                    use_container_width=True
                )
            else:
                st.info("No hay clientes mayoristas registrados.")

        with st.expander("➕ Añadir Nuevo Cliente"):
            with st.form("form_nuevo_cliente"):
                col_c1, col_c2 = st.columns([2, 1])
                with col_c1:
                    nc_nom = st.text_input("Nombre / Razón Social:")
                with col_c2:
                    nc_tipo = st.selectbox("Tipo de Cliente:", ["Minorista", "Mayorista"])

                nc_tel = st.text_input("Teléfono / WhatsApp:")
                nc_dir = st.text_input("Dirección de Entrega:")
                nc_pref = st.text_area("Preferencias (ej: rebanado, entrega temprano, días de pedido fijo)")

                submit_cliente = st.form_submit_button("Guardar Cliente")
                if submit_cliente and nc_nom:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("""
                    INSERT INTO clientes (nombre, telefono, direccion, preferencias, tipo_cliente)
                    VALUES (?, ?, ?, ?, ?)
                    """, (nc_nom, nc_tel, nc_dir, nc_pref, nc_tipo))
                    conn.commit()
                    conn.close()
                    st.success(f"Cliente '{nc_nom}' ({nc_tipo}) agregado con éxito.")
                    st.rerun()

# ==========================================================
# MÓDULO 5: BITÁCORA DE FERMENTACIÓN Y CALIDAD
# ==========================================================
elif menu == "🌡️ 5. Bitácora de Fermentación & Calidad":
    st.markdown('<div class="main-header">🌡️ Bitácora de Fermentación & Control de Calidad</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Registro técnico sin ceros innecesarios en temperaturas y estandarización ante el clima</div>', unsafe_allow_html=True)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT l.id, l.codigo_lote, r.nombre as receta_nombre, l.fecha_horneado,
           b.temp_ambiente_amasado_c, b.temp_final_masa_c, b.duracion_autolisis_min,
           b.tiempo_bloque_horas, b.pliegues_realizados, b.tiempo_retardo_frio_horas,
           b.temp_nevera_c, b.evaluacion_calidad, b.observaciones_calidad
    FROM lotes_produccion l
    JOIN recetas r ON l.receta_id = r.id
    LEFT JOIN bitacora_fermentacion b ON l.id = b.lote_id
    ORDER BY l.id DESC
    """)
    registros = cur.fetchall()
    conn.close()

    if not registros:
        st.warning("No hay lotes creados para registrar en la bitácora.")
    else:
        lote_sel_dict = {f"{r['codigo_lote']} - {r['receta_nombre']} ({r['fecha_horneado']})": r for r in registros}
        sel_lote_nombre = st.selectbox("Seleccionar Lote a Documentar o Revisar:", list(lote_sel_dict.keys()))
        reg = lote_sel_dict[sel_lote_nombre]

        with st.form("form_bitacora"):
            st.markdown(f"### 📝 Hoja de Control Técnico: `{reg['codigo_lote']}`")

            col_temp1, col_temp2, col_temp3 = st.columns(3)
            # Quitar ceros decimales innecesarios con format="%g" y valores limpios
            val_t_amb = float(reg["temp_ambiente_amasado_c"]) if reg["temp_ambiente_amasado_c"] else 24.0
            val_t_masa = float(reg["temp_final_masa_c"]) if reg["temp_final_masa_c"] else 25.0
            val_t_nevera = float(reg["temp_nevera_c"]) if reg["temp_nevera_c"] else 4.0

            with col_temp1:
                t_amb = st.number_input("Temperatura Ambiente (°C):", value=val_t_amb, step=0.5, format="%g")
            with col_temp2:
                t_masa = st.number_input("Temperatura Masa (°C):", value=val_t_masa, step=0.5, format="%g")
            with col_temp3:
                t_nevera = st.number_input("Temperatura Nevera (°C):", value=val_t_nevera, step=0.5, format="%g")

            st.markdown("#### ⏱️ Tiempos de Fermentación")
            col_t1, col_t2, col_t3, col_t4 = st.columns(4)
            with col_t1:
                autolisis = st.number_input("Autólisis (min):", value=int(reg["duracion_autolisis_min"] or 30), step=5)
            with col_t2:
                bloque_hrs = st.number_input("Fermentación Bloque (horas):", value=float(reg["tiempo_bloque_horas"] or 4.0), step=0.5, format="%g")
            with col_t3:
                pliegues = st.number_input("Pliegues (folds):", value=int(reg["pliegues_realizados"] or 3), step=1)
            with col_t4:
                frio_hrs = st.number_input("Retardo Frío (horas):", value=float(reg["tiempo_retardo_frio_horas"] or 16.0), step=1.0, format="%g")

            st.markdown("#### ⭐ Evaluación Organoléptica de Calidad")
            col_q1, col_q2 = st.columns([1, 2])
            with col_q1:
                estrellas = st.slider("Calificación Global (1 a 5 estrellas):", min_value=1, max_value=5, value=int(reg["evaluacion_calidad"] or 5))
            with col_q2:
                obs = st.text_area("Observaciones técnicas (greña, alveolado, acidez, salto de horno):", value=reg["observaciones_calidad"] or "")

            submit_bitacora = st.form_submit_button("💾 Guardar Datos en Bitácora", type="primary")
            if submit_bitacora:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                INSERT INTO bitacora_fermentacion 
                (lote_id, temp_ambiente_amasado_c, temp_final_masa_c, duracion_autolisis_min, tiempo_bloque_horas, pliegues_realizados, tiempo_retardo_frio_horas, temp_nevera_c, evaluacion_calidad, observaciones_calidad)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(lote_id) DO UPDATE SET
                    temp_ambiente_amasado_c = excluded.temp_ambiente_amasado_c,
                    temp_final_masa_c = excluded.temp_final_masa_c,
                    duracion_autolisis_min = excluded.duracion_autolisis_min,
                    tiempo_bloque_horas = excluded.tiempo_bloque_horas,
                    pliegues_realizados = excluded.pliegues_realizados,
                    tiempo_retardo_frio_horas = excluded.tiempo_retardo_frio_horas,
                    temp_nevera_c = excluded.temp_nevera_c,
                    evaluacion_calidad = excluded.evaluacion_calidad,
                    observaciones_calidad = excluded.observaciones_calidad
                """, (reg["id"], t_amb, t_masa, autolisis, bloque_hrs, pliegues, frio_hrs, t_nevera, estrellas, obs))
                conn.commit()
                conn.close()
                st.success(f"Bitácora guardada para el lote {reg['codigo_lote']}.")
                st.rerun()

        # Histórico limpio sin ceros innecesarios
        st.markdown("---")
        st.markdown("### 📊 Histórico de Fermentaciones para Estandarización")
        df_hist = pd.DataFrame([dict(r) for r in registros if r["evaluacion_calidad"] is not None])
        if not df_hist.empty:
            # Formatear columnas para quitar ceros decimales
            def clean_temp(val):
                return f"{float(val):g} °C" if pd.notnull(val) and val != 0 else "-"
            def clean_hours(val):
                return f"{float(val):g} h" if pd.notnull(val) and val != 0 else "-"

            df_hist["T. Amb"] = df_hist["temp_ambiente_amasado_c"].apply(clean_temp)
            df_hist["T. Masa"] = df_hist["temp_final_masa_c"].apply(clean_temp)
            df_hist["Bloque"] = df_hist["tiempo_bloque_horas"].apply(clean_hours)
            df_hist["Frío"] = df_hist["tiempo_retardo_frio_horas"].apply(clean_hours)

            st.dataframe(
                df_hist[["codigo_lote", "receta_nombre", "T. Amb", "T. Masa", "Bloque", "Frío", "evaluacion_calidad", "observaciones_calidad"]].rename(
                    columns={
                        "codigo_lote": "Lote", "receta_nombre": "Pan",
                        "evaluacion_calidad": "Estrellas (1-5)", "observaciones_calidad": "Observaciones"
                    }
                ),
                column_config={
                    "Lote": st.column_config.TextColumn("Lote"),
                    "Pan": st.column_config.TextColumn("Pan"),
                    "T. Amb": st.column_config.TextColumn("T. Amb"),
                    "T. Masa": st.column_config.TextColumn("T. Masa"),
                    "Bloque": st.column_config.TextColumn("Bloque"),
                    "Frío": st.column_config.TextColumn("Frío"),
                    "Estrellas (1-5)": st.column_config.TextColumn("Estrellas (1-5)"),
                    "Observaciones": st.column_config.TextColumn("Observaciones")
                },
                use_container_width=True
            )

# ==========================================================
# MÓDULO 6: FINANZAS Y REPORTES (CON FILTRO POR MES / FECHAS)
# ==========================================================
elif menu == "📊 6. Finanzas & Reportes":
    st.markdown('<div class="main-header">📊 Finanzas & Reportes Operativos</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Métricas en COP con filtro mensual y calendario de fechas para gastos e ingresos</div>', unsafe_allow_html=True)

    # 1. Selector de Filtro de Fechas / Mes
    col_filtro1, col_filtro2 = st.columns([1, 1])
    with col_filtro1:
        tipo_filtro = st.radio("Método de Filtrado:", ["Filtrar por Mes Específico", "Rango de Fechas Personalizado"], horizontal=True)

    conn = get_connection()
    cur = conn.cursor()

    if tipo_filtro == "Filtrar por Mes Específico":
        with col_filtro2:
            # Obtener lista de meses con movimientos
            cur.execute("""
            SELECT DISTINCT strftime('%Y-%m', fecha) as mes FROM gastos_operativos
            UNION
            SELECT DISTINCT strftime('%Y-%m', fecha_entrega) as mes FROM pedidos
            ORDER BY mes DESC
            """)
            meses_db = [r[0] for r in cur.fetchall() if r[0] is not None]
            mes_actual = datetime.now().strftime("%Y-%m")
            if mes_actual not in meses_db:
                meses_db.insert(0, mes_actual)
            
            sel_mes = st.selectbox("Seleccionar Mes a Consultar:", meses_db)
            fecha_inicio_filtro = f"{sel_mes}-01"
            # Fin de mes
            y, m = map(int, sel_mes.split("-"))
            if m == 12:
                fecha_fin_filtro = f"{y}-12-31"
            else:
                fecha_fin_filtro = (date(y, m+1, 1) - timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        with col_filtro2:
            hoy = date.today()
            inicio_mes_def = date(hoy.year, hoy.month, 1)
            rango_fechas = st.date_input("Seleccionar Rango de Fechas:", value=(inicio_mes_def, hoy))
            if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
                fecha_inicio_filtro = rango_fechas[0].strftime("%Y-%m-%d")
                fecha_fin_filtro = rango_fechas[1].strftime("%Y-%m-%d")
            else:
                fecha_inicio_filtro = inicio_mes_def.strftime("%Y-%m-%d")
                fecha_fin_filtro = hoy.strftime("%Y-%m-%d")

    st.info(f"📅 Visualizando datos financieros desde **{fecha_inicio_filtro}** hasta **{fecha_fin_filtro}**")

    # Consultar datos filtrados por período
    cur.execute("""
    SELECT COUNT(*) as num_pedidos, COALESCE(SUM(unidades), 0) as total_hogazas, COALESCE(SUM(total_cobrado), 0) as total_ventas 
    FROM pedidos 
    WHERE fecha_entrega BETWEEN ? AND ?
    """, (fecha_inicio_filtro, fecha_fin_filtro))
    v_data = cur.fetchone()

    cur.execute("""
    SELECT COALESCE(SUM(costo_total_lote), 0) as total_costo_lotes 
    FROM lotes_produccion 
    WHERE fecha_horneado BETWEEN ? AND ?
    """, (fecha_inicio_filtro, fecha_fin_filtro))
    c_data = cur.fetchone()

    cur.execute("""
    SELECT COALESCE(SUM(monto), 0) as total_gastos 
    FROM gastos_operativos 
    WHERE fecha BETWEEN ? AND ?
    """, (fecha_inicio_filtro, fecha_fin_filtro))
    g_data = cur.fetchone()

    # Historial de gastos filtrado
    cur.execute("""
    SELECT * FROM gastos_operativos 
    WHERE fecha BETWEEN ? AND ? 
    ORDER BY fecha DESC
    """, (fecha_inicio_filtro, fecha_fin_filtro))
    gastos_list = cur.fetchall()

    conn.close()

    total_ingresos = v_data["total_ventas"]
    costo_produccion = c_data["total_costo_lotes"]
    gastos_operativos = g_data["total_gastos"]
    utilidad_neta = total_ingresos - costo_produccion - gastos_operativos
    margen_neto_pct = (utilidad_neta / total_ingresos * 100) if total_ingresos > 0 else 0.0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Ingresos Ventas", baker_math.format_cop(total_ingresos), f"{v_data['total_hogazas']} hogazas")
    kpi2.metric("Costo Producción Lotes", baker_math.format_cop(costo_produccion))
    kpi3.metric("Gastos Operativos", baker_math.format_cop(gastos_operativos))
    kpi4.metric("Utilidad Neta Período", baker_math.format_cop(utilidad_neta), f"{margen_neto_pct:.1f}% margen")

    st.markdown("---")
    col_fin1, col_fin2 = st.columns(2)

    with col_fin1:
        st.markdown("### 💸 Registrar Nuevo Gasto Operativo")
        with st.form("form_gasto"):
            g_concepto = st.text_input("Concepto (ej: Pago cilindro de gas 40lb, bolsas kraft, arriendo taller):")
            g_cat = st.selectbox("Categoría:", ["Energia/Gas", "Alquiler", "Empaque", "Transporte", "Herramientas/Mantenimiento", "Otros"])
            g_monto = st.number_input("Monto en Pesos Colombianos (COP):", min_value=500.0, value=115000.0, step=5000.0)
            g_fecha = st.date_input("Fecha del Gasto:", value=date.today())

            submit_gasto = st.form_submit_button("Registrar Gasto", type="primary")
            if submit_gasto and g_concepto:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                INSERT INTO gastos_operativos (concepto, categoria, monto, fecha)
                VALUES (?, ?, ?, ?)
                """, (g_concepto, g_cat, g_monto, g_fecha.strftime("%Y-%m-%d")))
                conn.commit()
                conn.close()
                st.success("Gasto registrado exitosamente.")
                st.rerun()

    with col_fin2:
        st.markdown(f"### 📋 Historial de Gastos del Período ({len(gastos_list)} registros)")
        if gastos_list:
            df_g = pd.DataFrame([dict(g) for g in gastos_list])
            df_g["Monto Formateado"] = df_g["monto"].apply(baker_math.format_cop)
            st.dataframe(
                df_g[["fecha", "concepto", "categoria", "Monto Formateado"]].rename(
                    columns={"fecha": "Fecha", "concepto": "Concepto", "categoria": "Categoría", "Monto Formateado": "Monto en COP"}
                ),
                column_config={
                    "Fecha": st.column_config.TextColumn("Fecha"),
                    "Concepto": st.column_config.TextColumn("Concepto"),
                    "Categoría": st.column_config.TextColumn("Categoría"),
                    "Monto en COP": st.column_config.TextColumn("Monto en COP")
                },
                use_container_width=True
            )
        else:
            st.info("No hay gastos registrados en el período seleccionado.")

# ==========================================================
# MÓDULO 7: CALENDARIO DE ACTIVIDADES (VISTA GOOGLE CALENDAR)
# ==========================================================
elif menu == "📅 7. Calendario de Actividades":
    st.markdown('<div class="main-header">📅 Calendario de Actividades & Ritmo Semanal</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Vista tipo Google Calendar con actividades diferenciadas por color, vista mensual, semanal y edición diaria</div>', unsafe_allow_html=True)

    # Paleta de colores distintivos por tipo de actividad
    CAL_ESTILOS = {
        "🛒 Compra de Insumos & Harinas": {"bg": "#E8F5E9", "border": "#2E7D32", "text": "#1B5E20", "chip": "#10B981", "badge": "🛒 Compras"},
        "📢 Apertura de Preventa (WhatsApp/Redes)": {"bg": "#E3F2FD", "border": "#1976D2", "text": "#0D47A1", "chip": "#3B82F6", "badge": "📢 Preventa"},
        "🔒 Cierre de Pedidos": {"bg": "#FFEBEE", "border": "#D32F2F", "text": "#B71C1C", "chip": "#EF4444", "badge": "🔒 Cierre"},
        "🥣 Amasado, Autólisis y Formado": {"bg": "#FFF8E1", "border": "#D97706", "text": "#B45309", "chip": "#F59E0B", "badge": "🥣 Amasado"},
        "🔥 Día de Horneado & Empaque": {"bg": "#FBE9E7", "border": "#991B1B", "text": "#7F1D1D", "chip": "#991B1B", "badge": "🔥 Horneado"},
        "📦 Despacho y Entrega de Pedidos": {"bg": "#F3E5F5", "border": "#7B1FA2", "text": "#4A148C", "chip": "#8B5CF6", "badge": "📦 Entrega"},
        "🌾 Refresco de Masa Madre": {"bg": "#FEF3C7", "border": "#B45309", "text": "#78350F", "chip": "#D97706", "badge": "🌾 Masa Madre"},
        "🧹 Mantenimiento y Limpieza": {"bg": "#ECEFF1", "border": "#546E7A", "text": "#263238", "chip": "#64748B", "badge": "🧹 Limpieza"}
    }
    ESTILO_DEFAULT = {"bg": "#F1F5F9", "border": "#475569", "text": "#1E293B", "chip": "#64748B", "badge": "📌 Tarea"}

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM calendario_actividades ORDER BY fecha ASC, id ASC")
    actividades_raw = cur.fetchall()
    conn.close()

    actividades_list = [dict(a) for a in actividades_raw]

    # Agrupar actividades por fecha 'YYYY-MM-DD'
    actividades_por_fecha = {}
    for a in actividades_list:
        f = a["fecha"]
        if f not in actividades_por_fecha:
            actividades_por_fecha[f] = []
        actividades_por_fecha[f].append(a)

    # Modal interactivo tipo Google Calendar para editar o gestionar actividades del día
    @st.dialog("📅 Gestión de Actividades del Día")
    def modal_gestionar_dia(fecha_sel, lista_acts):
        dias_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        meses_es = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        f_obj = datetime.strptime(fecha_sel, "%Y-%m-%d").date()
        fecha_txt = f"{dias_es[f_obj.weekday()]}, {f_obj.day} de {meses_es[f_obj.month - 1]} de {f_obj.year}"
        st.markdown(f"### 🗓️ {fecha_txt}")
        
        tab_m_ver, tab_m_add = st.tabs([f"✏️ Actividades Registradas ({len(lista_acts)})", "➕ Añadir Nueva Tarea"])
        
        with tab_m_ver:
            if not lista_acts:
                st.info("No hay actividades registradas para esta fecha.")
            else:
                for a in lista_acts:
                    estilo = CAL_ESTILOS.get(a["tipo_actividad"], ESTILO_DEFAULT)
                    st.markdown(f"""
                    <div style="background-color:{estilo['bg']}; border-left:4px solid {estilo['chip']}; padding:6px 10px; border-radius:5px; margin-bottom:8px;">
                        <b style="color:{estilo['text']};">{estilo['badge']}</b> - <span style="font-size:0.95rem; font-weight:600;">{a['titulo']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.form(f"form_modal_ed_{a['id']}"):
                        m_f1, m_f2 = st.columns([1, 1])
                        with m_f1:
                            m_n_fecha = st.date_input("Fecha:", value=datetime.strptime(a["fecha"], "%Y-%m-%d").date(), key=f"mf_f_{a['id']}")
                        with m_f2:
                            m_n_tipo = st.selectbox(
                                "Tipo:",
                                list(CAL_ESTILOS.keys()),
                                index=list(CAL_ESTILOS.keys()).index(a["tipo_actividad"]) if a["tipo_actividad"] in CAL_ESTILOS else 0,
                                key=f"mf_t_{a['id']}"
                            )
                        m_n_tit = st.text_input("Título:", value=a["titulo"], key=f"mf_tit_{a['id']}")
                        m_n_desc = st.text_area("Detalles u observaciones:", value=a["descripcion"] or "", key=f"mf_desc_{a['id']}")
                        m_n_comp = st.checkbox("Marcar como Completada", value=bool(a["completada"]), key=f"mf_chk_{a['id']}")
                        
                        col_sav, col_del = st.columns([1, 1])
                        with col_sav:
                            if st.form_submit_button("💾 Guardar Cambios", type="primary"):
                                conn = get_connection()
                                cur = conn.cursor()
                                cur.execute("""
                                UPDATE calendario_actividades
                                SET fecha = ?, tipo_actividad = ?, titulo = ?, descripcion = ?, completada = ?
                                WHERE id = ?
                                """, (m_n_fecha.strftime("%Y-%m-%d"), m_n_tipo, m_n_tit, m_n_desc, 1 if m_n_comp else 0, a["id"]))
                                conn.commit()
                                conn.close()
                                st.success("Actividad modificada exitosamente.")
                                st.rerun()

                    if st.button(f"🗑️ Eliminar Actividad '{a['titulo']}'", key=f"del_modal_btn_{a['id']}", type="secondary"):
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM calendario_actividades WHERE id = ?", (a["id"],))
                        conn.commit()
                        conn.close()
                        st.warning("Actividad eliminada.")
                        st.rerun()
                    st.divider()

        with tab_m_add:
            st.markdown(f"**Programar nueva actividad para el {fecha_sel}:**")
            with st.form(f"form_modal_add_{fecha_sel}"):
                add_tipo = st.selectbox("Tipo de Actividad:", list(CAL_ESTILOS.keys()), key=f"madd_t_{fecha_sel}")
                add_tit = st.text_input("Título:", key=f"madd_tit_{fecha_sel}")
                add_desc = st.text_area("Detalles u observaciones:", key=f"madd_desc_{fecha_sel}")
                if st.form_submit_button("🚀 Programar Tarea", type="primary"):
                    if add_tit:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute("""
                        INSERT INTO calendario_actividades (fecha, tipo_actividad, titulo, descripcion, completada)
                        VALUES (?, ?, ?, ?, 0)
                        """, (fecha_sel, add_tipo, add_tit, add_desc))
                        conn.commit()
                        conn.close()
                        st.success("Actividad programada exitosamente.")
                        st.rerun()
                    else:
                        st.error("Por favor ingresa un título.")

    tab_mes, tab_sem, tab_agenda, tab_nueva = st.tabs([
        "📅 Vista Mensual (Google Calendar)",
        "📆 Vista Semanal",
        "📋 Agenda / Lista Cronológica",
        "➕ Agendar Nueva Actividad"
    ])

    hoy = date.today()

    # Inicializar estado del calendario si no existe
    if "cal_nav_year" not in st.session_state:
        st.session_state["cal_nav_year"] = hoy.year
    if "cal_nav_month" not in st.session_state:
        st.session_state["cal_nav_month"] = hoy.month

    # 1. VISTA MENSUAL (GOOGLE CALENDAR GRID)
    with tab_mes:
        col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1, 1, 2.5, 1.5])
        with col_nav1:
            if st.button("◀️ Mes Anterior", use_container_width=True):
                if st.session_state["cal_nav_month"] == 1:
                    st.session_state["cal_nav_month"] = 12
                    st.session_state["cal_nav_year"] -= 1
                else:
                    st.session_state["cal_nav_month"] -= 1
                st.rerun()

        with col_nav2:
            if st.button("Mes Siguiente ▶️", use_container_width=True):
                if st.session_state["cal_nav_month"] == 12:
                    st.session_state["cal_nav_month"] = 1
                    st.session_state["cal_nav_year"] += 1
                else:
                    st.session_state["cal_nav_month"] += 1
                st.rerun()

        cal_year = st.session_state["cal_nav_year"]
        cal_month = st.session_state["cal_nav_month"]
        nombres_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        with col_nav3:
            st.markdown(f"<h3 style='margin:0; padding-top:4px; text-align:center; color:#991b1b;'>📅 {nombres_meses[cal_month - 1]} {cal_year}</h3>", unsafe_allow_html=True)

        with col_nav4:
            if st.button("📍 Ir a Hoy", use_container_width=True):
                st.session_state["cal_nav_year"] = hoy.year
                st.session_state["cal_nav_month"] = hoy.month
                st.rerun()

        # Leyenda de Colores
        st.markdown("""
        <div style="display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0 10px 0; font-size: 0.82rem;">
            <span style="background-color: #E8F5E9; border-left: 3px solid #10B981; color: #1B5E20; padding: 2px 7px; border-radius: 3px; font-weight:600;">🛒 Insumos</span>
            <span style="background-color: #E3F2FD; border-left: 3px solid #3B82F6; color: #0D47A1; padding: 2px 7px; border-radius: 3px; font-weight:600;">📢 Preventa</span>
            <span style="background-color: #FFF8E1; border-left: 3px solid #F59E0B; color: #B45309; padding: 2px 7px; border-radius: 3px; font-weight:600;">🥣 Amasado</span>
            <span style="background-color: #FFEBEE; border-left: 3px solid #EF4444; color: #B71C1C; padding: 2px 7px; border-radius: 3px; font-weight:600;">🔒 Cierre Pedidos</span>
            <span style="background-color: #FBE9E7; border-left: 3px solid #991B1B; color: #7F1D1D; padding: 2px 7px; border-radius: 3px; font-weight:600;">🔥 Horneado</span>
            <span style="background-color: #F3E5F5; border-left: 3px solid #8B5CF6; color: #4A148C; padding: 2px 7px; border-radius: 3px; font-weight:600;">📦 Entrega</span>
            <span style="background-color: #FEF3C7; border-left: 3px solid #D97706; color: #78350F; padding: 2px 7px; border-radius: 3px; font-weight:600;">🌾 Masa Madre</span>
            <span style="background-color: #ECEFF1; border-left: 3px solid #64748B; color: #263238; padding: 2px 7px; border-radius: 3px; font-weight:600;">🧹 Mantenimiento</span>
        </div>
        """, unsafe_allow_html=True)

        # Generar matriz del mes
        semanas = calendar.monthcalendar(cal_year, cal_month)
        dias_encabezado = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

        # Encabezado de días de la semana
        cols_header = st.columns(7)
        for i, nom_dia in enumerate(dias_encabezado):
            cols_header[i].markdown(f"<div style='text-align:center; font-weight:700; color:#475569; font-size:0.85rem; padding: 6px 0; background-color:#F8FAFC; border-radius:4px;'>{nom_dia}</div>", unsafe_allow_html=True)

        # Celdas por semana
        for sem in semanas:
            cols_dia = st.columns(7)
            for d_idx, dia_num in enumerate(sem):
                with cols_dia[d_idx]:
                    if dia_num == 0:
                        st.markdown("<div style='height:118px; background-color:#FAFAFA; border:1px dashed #E2E8F0; border-radius:8px; opacity:0.35;'></div>", unsafe_allow_html=True)
                    else:
                        fecha_str = f"{cal_year}-{cal_month:02d}-{dia_num:02d}"
                        es_hoy = (cal_year == hoy.year and cal_month == hoy.month and dia_num == hoy.day)
                        acts_del_dia = actividades_por_fecha.get(fecha_str, [])

                        with st.container(border=True, height=118):
                            # Encabezado superior: Número de día a la izquierda y Botón de acción a la derecha
                            col_c_num, col_c_btn = st.columns([1, 1], vertical_alignment="center")
                            with col_c_num:
                                if es_hoy:
                                    st.markdown(f"<span class='cal-badge-hoy' style='background-color:#991b1b; color:#FFFFFF; padding:1px 6px; border-radius:10px; font-weight:700; font-size:0.75rem; white-space:nowrap;'>{dia_num} HOY</span>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<span style='font-weight:700; color:#334155; font-size:0.92rem; padding-left:1px;'>{dia_num}</span>", unsafe_allow_html=True)

                            with col_c_btn:
                                if acts_del_dia:
                                    if st.button("✏️ Editar", key=f"btn_dia_{fecha_str}", use_container_width=True, help=f"Editar actividades ({len(acts_del_dia)}) del {fecha_str}"):
                                        modal_gestionar_dia(fecha_str, acts_del_dia)
                                else:
                                    if st.button("➕", key=f"btn_add_{fecha_str}", use_container_width=True, help=f"Agendar actividad en {fecha_str}"):
                                        modal_gestionar_dia(fecha_str, [])

                            # Actividades / Etiquetas dentro del mismo recuadro
                            if acts_del_dia:
                                chips_html = ""
                                for a in acts_del_dia:
                                    estilo = CAL_ESTILOS.get(a["tipo_actividad"], ESTILO_DEFAULT)
                                    tachado = "text-decoration:line-through;opacity:0.6;" if a["completada"] == 1 else ""
                                    chips_html += f'<div style="background-color:{estilo["bg"]};border-left:3px solid {estilo["chip"]};color:{estilo["text"]};padding:2px 5px;border-radius:3px;font-size:0.72rem;margin-top:2px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;{tachado}" title="{a["tipo_actividad"]}: {a["titulo"]}">{a["titulo"]}</div>'
                                st.markdown(chips_html, unsafe_allow_html=True)

        st.markdown("---")
        # Gestor y editor de actividades del mes seleccionado
        st.markdown("### 🔎 Gestor y Editor de Actividades por Día")
        fechas_con_actividades = sorted(list(actividades_por_fecha.keys()), reverse=True)
        if fechas_con_actividades:
            col_sel_f, col_sel_info = st.columns([1.5, 2.5])
            with col_sel_f:
                sel_fecha_gestionar = st.selectbox("Seleccionar Fecha a Consultar o Editar:", fechas_con_actividades)
            
            with col_sel_info:
                st.write("")
                st.caption(f"Actividades agendadas para el **{sel_fecha_gestionar}**:")

            acts_de_esa_fecha = actividades_por_fecha.get(sel_fecha_gestionar, [])
            for a in acts_de_esa_fecha:
                estilo = CAL_ESTILOS.get(a["tipo_actividad"], ESTILO_DEFAULT)
                with st.expander(f"{estilo['badge']} - {a['titulo']} {'(✅ Completada)' if a['completada'] == 1 else '(⏳ Pendiente)'}"):
                    with st.form(f"form_ed_act_mes_{a['id']}"):
                        ed_f1, ed_f2 = st.columns([1, 1])
                        with ed_f1:
                            nueva_fecha = st.date_input("Fecha:", value=datetime.strptime(a["fecha"], "%Y-%m-%d").date(), key=f"f_cal_ed_{a['id']}")
                        with ed_f2:
                            nuevo_tipo = st.selectbox(
                                "Tipo de Actividad:",
                                list(CAL_ESTILOS.keys()),
                                index=list(CAL_ESTILOS.keys()).index(a["tipo_actividad"]) if a["tipo_actividad"] in CAL_ESTILOS else 0,
                                key=f"tipo_cal_ed_{a['id']}"
                            )

                        nuevo_tit = st.text_input("Título:", value=a["titulo"], key=f"tit_cal_ed_{a['id']}")
                        nueva_desc = st.text_area("Detalles:", value=a["descripcion"] or "", key=f"desc_cal_ed_{a['id']}")
                        nuevo_estado_comp = st.checkbox("Marcar como Completada", value=bool(a["completada"]), key=f"comp_cal_ed_{a['id']}")

                        col_btn1, col_btn2 = st.columns([1, 1])
                        with col_btn1:
                            if st.form_submit_button("💾 Guardar Cambios"):
                                conn = get_connection()
                                cur = conn.cursor()
                                cur.execute("""
                                UPDATE calendario_actividades
                                SET fecha = ?, tipo_actividad = ?, titulo = ?, descripcion = ?, completada = ?
                                WHERE id = ?
                                """, (nueva_fecha.strftime("%Y-%m-%d"), nuevo_tipo, nuevo_tit, nueva_desc, 1 if nuevo_estado_comp else 0, a["id"]))
                                conn.commit()
                                conn.close()
                                st.success("Actividad actualizada.")
                                st.rerun()

                    if st.button(f"🗑️ Eliminar Actividad #{a['id']}", key=f"del_btn_mes_{a['id']}", type="secondary"):
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM calendario_actividades WHERE id = ?", (a["id"],))
                        conn.commit()
                        conn.close()
                        st.warning("Actividad eliminada.")
                        st.rerun()
        else:
            st.info("No hay actividades registradas en el calendario.")

    # 2. VISTA SEMANAL
    with tab_sem:
        st.markdown("### 📆 Vista Semanal del Obrador")
        # Calcular lunes de la semana actual
        lunes_actual = hoy - timedelta(days=hoy.weekday())
        col_sem_nav1, col_sem_nav2 = st.columns([2, 1])
        with col_sem_nav1:
            offset_semanas = st.number_input("Navegar semanas (0 = Esta semana, +1 = Próxima semana, -1 = Anterior):", value=0, step=1)
        
        lunes_sel = lunes_actual + timedelta(weeks=offset_semanas)
        domingo_sel = lunes_sel + timedelta(days=6)
        
        st.markdown(f"**Semana:** Del **{lunes_sel.strftime('%d/%m/%Y')}** al **{domingo_sel.strftime('%d/%m/%Y')}**")

        dias_cols = st.columns(7)
        for i in range(7):
            d_fecha = lunes_sel + timedelta(days=i)
            d_fecha_str = d_fecha.strftime("%Y-%m-%d")
            es_dia_hoy = (d_fecha == hoy)

            with dias_cols[i]:
                header_bg = "#991b1b" if es_dia_hoy else "#475569"
                header_html = f'<div style="background-color:{header_bg};color:#FFFFFF;padding:6px;border-radius:6px;text-align:center;font-size:0.85rem;font-weight:700;margin-bottom:8px;">{dias_encabezado[i]}<br><span style="font-size:1rem;">{d_fecha.day}</span></div>'
                st.markdown(header_html, unsafe_allow_html=True)

                acts_del_dia = actividades_por_fecha.get(d_fecha_str, [])
                if not acts_del_dia:
                    st.caption("Sin tareas")
                    if st.button("➕ Agendar", key=f"sem_btn_add_{d_fecha_str}", use_container_width=True):
                        modal_gestionar_dia(d_fecha_str, [])
                else:
                    for a in acts_del_dia:
                        estilo = CAL_ESTILOS.get(a["tipo_actividad"], ESTILO_DEFAULT)
                        tachado = "line-through" if a["completada"] == 1 else "none"
                        card_html = f'<div class="cal-day-cell" style="background-color:{estilo["bg"]};border-left:4px solid {estilo["chip"]};color:{estilo["text"]};padding:6px;border-radius:4px;font-size:0.8rem;margin-bottom:6px;min-height:auto;"><b style="text-decoration:{tachado};">{a["titulo"]}</b><br><span style="font-size:0.75rem;color:{estilo["text"]};">{estilo["badge"]}</span></div>'
                        st.markdown(card_html, unsafe_allow_html=True)
                    if st.button(f"✏️ Editar ({len(acts_del_dia)})", key=f"sem_btn_ed_{d_fecha_str}", use_container_width=True):
                        modal_gestionar_dia(d_fecha_str, acts_del_dia)

    # 3. AGENDA / LISTA CRONOLÓGICA
    with tab_agenda:
        st.markdown("### 📋 Agenda Cronológica de Actividades")
        col_filtro1, col_filtro2 = st.columns([1, 1])
        with col_filtro1:
            filtro_est = st.radio("Estado de Tarea:", ["Todas", "Solo Pendientes", "Solo Completadas"], horizontal=True)
        with col_filtro2:
            filtro_tipo = st.selectbox("Filtrar por Tipo:", ["Todos los tipos"] + list(CAL_ESTILOS.keys()))

        acts_agenda = []
        for a in actividades_list:
            if filtro_est == "Solo Pendientes" and a["completada"] == 1:
                continue
            if filtro_est == "Solo Completadas" and a["completada"] == 0:
                continue
            if filtro_tipo != "Todos los tipos" and a["tipo_actividad"] != filtro_tipo:
                continue
            acts_agenda.append(a)

        if not acts_agenda:
            st.info("No se encontraron actividades con los filtros seleccionados.")
        else:
            for a in acts_agenda:
                estilo = CAL_ESTILOS.get(a["tipo_actividad"], ESTILO_DEFAULT)
                with st.container():
                    col_chk, col_info, col_act_btns = st.columns([0.4, 4.2, 1.4])
                    with col_chk:
                        is_comp = bool(a["completada"])
                        if st.checkbox("", value=is_comp, key=f"chk_ag_{a['id']}"):
                            if not is_comp:
                                conn = get_connection()
                                cur = conn.cursor()
                                cur.execute("UPDATE calendario_actividades SET completada = 1 WHERE id = ?", (a["id"],))
                                conn.commit()
                                conn.close()
                                st.rerun()
                        else:
                            if is_comp:
                                conn = get_connection()
                                cur = conn.cursor()
                                cur.execute("UPDATE calendario_actividades SET completada = 0 WHERE id = ?", (a["id"],))
                                conn.commit()
                                conn.close()
                                st.rerun()

                    with col_info:
                        tachado = "~~" if a["completada"] == 1 else ""
                        st.markdown(f"📅 **{a['fecha']}** | <span style='background-color:{estilo['bg']}; border-left:3px solid {estilo['chip']}; color:{estilo['text']}; padding:2px 6px; border-radius:3px; font-weight:600; font-size:0.8rem;'>{estilo['badge']}</span> **{tachado}{a['titulo']}{tachado}**", unsafe_allow_html=True)
                        if a["descripcion"]:
                            st.caption(f"{a['descripcion']}")

                    with col_act_btns:
                        exp_ed_ag = st.expander("✏️ Editar")
                        with exp_ed_ag:
                            with st.form(f"form_ed_ag_{a['id']}"):
                                n_f = st.date_input("Fecha:", value=datetime.strptime(a["fecha"], "%Y-%m-%d").date(), key=f"f_ag_{a['id']}")
                                n_t = st.selectbox("Tipo:", list(CAL_ESTILOS.keys()), index=list(CAL_ESTILOS.keys()).index(a["tipo_actividad"]) if a["tipo_actividad"] in CAL_ESTILOS else 0, key=f"t_ag_{a['id']}")
                                n_tit = st.text_input("Título:", value=a["titulo"], key=f"tit_ag_{a['id']}")
                                n_desc = st.text_area("Detalle:", value=a["descripcion"] or "", key=f"desc_ag_{a['id']}")
                                if st.form_submit_button("Guardar"):
                                    conn = get_connection()
                                    cur = conn.cursor()
                                    cur.execute("UPDATE calendario_actividades SET fecha = ?, tipo_actividad = ?, titulo = ?, descripcion = ? WHERE id = ?", (n_f.strftime("%Y-%m-%d"), n_t, n_tit, n_desc, a["id"]))
                                    conn.commit()
                                    conn.close()
                                    st.success("Guardado.")
                                    st.rerun()
                        
                        if st.button("🗑️", key=f"del_ag_{a['id']}", help="Eliminar tarea"):
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute("DELETE FROM calendario_actividades WHERE id = ?", (a["id"],))
                            conn.commit()
                            conn.close()
                            st.rerun()

                    st.divider()

    # 4. AGENDAR NUEVA ACTIVIDAD
    with tab_nueva:
        st.markdown("### ➕ Agendar Nueva Actividad en el Calendario")
        with st.form("form_nueva_actividad_full"):
            col_na1, col_na2 = st.columns([1, 1])
            with col_na1:
                nueva_act_fecha = st.date_input("Fecha Programada:", value=date.today())
            with col_na2:
                nueva_act_tipo = st.selectbox("Tipo de Actividad:", list(CAL_ESTILOS.keys()))

            nueva_act_tit = st.text_input("Título de la Tarea (ej: Horneado Lote Especial de Masa Madre)")
            nueva_act_desc = st.text_area("Descripción u observaciones técnicas")

            estilo_sel = CAL_ESTILOS.get(nueva_act_tipo, ESTILO_DEFAULT)
            st.markdown(f"""
            <div style="background-color:{estilo_sel['bg']}; border-left:4px solid {estilo_sel['chip']}; color:{estilo_sel['text']}; padding:8px; border-radius:5px; font-size:0.85rem; margin:10px 0;">
                💡 <b>Vista previa del color:</b> {estilo_sel['badge']} - Se notificará con aviso previo en la campana de alertas 1 día antes y el día del evento.
            </div>
            """, unsafe_allow_html=True)

            if st.form_submit_button("🚀 Programar en el Calendario", type="primary"):
                if nueva_act_tit:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("""
                    INSERT INTO calendario_actividades (fecha, tipo_actividad, titulo, descripcion, completada)
                    VALUES (?, ?, ?, ?, 0)
                    """, (nueva_act_fecha.strftime("%Y-%m-%d"), nueva_act_tipo, nueva_act_tit, nueva_act_desc))
                    conn.commit()
                    conn.close()
                    st.success(f"Actividad '{nueva_act_tit}' agendada exitosamente.")
                    st.rerun()
                else:
                    st.error("Por favor ingresa un título para la actividad.")

# ==========================================================
# MÓDULO 8: MANTENIMIENTO DE EQUIPOS (NUEVO)
# ==========================================================
elif menu == "🛠️ 8. Mantenimiento de Equipos":
    st.markdown('<div class="main-header">🛠️ Mantenimiento de Equipos & Alertas</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Prevención y alarmas de mantenimiento para hornos, amasadoras, neveras y herramientas</div>', unsafe_allow_html=True)

    tasks = baker_math.get_maintenance_tasks()

    # Métricas de estado de equipos
    total_equipos = len(tasks)
    al_dia = sum(1 for t in tasks if t["estado"] == "AL DÍA")
    proximos = sum(1 for t in tasks if t["estado"] == "PRÓXIMO")
    vencidos = sum(1 for t in tasks if t["estado"] == "VENCIDO")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Equipos Monitoreados", total_equipos)
    m2.metric("🟢 Al Día", al_dia)
    m3.metric("🟡 Próximos (≤ 7 días)", proximos)
    m4.metric("🔴 Alertas Vencidas", vencidos)

    if vencidos > 0:
        st.markdown(f'<div class="stock-alert">⚠️ <b>ALERTA DE MANTENIMIENTO:</b> Hay {vencidos} tarea(s) de mantenimiento vencidas que requieren atención urgente.</div>', unsafe_allow_html=True)

    st.markdown("### 📋 Plan de Mantenimiento Preventivo")

    if not tasks:
        st.info("No hay equipos ni rutinas de mantenimiento registradas. Puedes agregar una a continuación.")
    else:
        for t in tasks:
            badge_cls = "badge-aldia" if t["estado"] == "AL DÍA" else ("badge-proximo" if t["estado"] == "PRÓXIMO" else "badge-vencido")
            with st.container():
                col_eq_info, col_eq_btn = st.columns([3.5, 1.5])
                with col_eq_info:
                    st.markdown(f"#### ⚙️ {t['equipo']} - <span class='badge-tag {badge_cls}'>{t['estado']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Tarea:** {t['tarea']}")
                    st.markdown(f"📅 **Última fecha:** {t['ultima_fecha']} | **Próxima fecha programada:** **{t['proxima_fecha']}** (Frecuencia: cada {t['frecuencia_dias']} días)")
                    if t["dias_restantes"] < 0:
                        st.markdown(f"<span style='color: #DC2626; font-weight: 700;'>⚠️ Vencido hace {abs(t['dias_restantes'])} día(s)</span>", unsafe_allow_html=True)
                    else:
                        st.caption(f"Faltan {t['dias_restantes']} día(s) para el próximo servicio")
                    if t["notas"]:
                        st.caption(f"Nota técnica: {t['notas']}")

                with col_eq_btn:
                    st.write("")
                    if st.button("✅ Marcar Realizado", key=f"btn_maint_{t['id']}", type="primary", use_container_width=True):
                        baker_math.complete_maintenance(t["id"])
                        st.success(f"Mantenimiento registrado para {t['equipo']}. Próxima fecha calculada automáticamente.")
                        st.rerun()

                    exp_mod = st.expander("⚙️ Modificar Equipo", expanded=False)
                    with exp_mod:
                        tab_ed_eq, tab_del_eq = st.tabs(["✏️ Editar", "🗑️ Eliminar"])
                        
                        with tab_ed_eq:
                            with st.form(f"form_edit_eq_{t['id']}"):
                                ed_eq_nombre = st.text_input("Nombre del Equipo:", value=t["equipo"])
                                ed_eq_tarea = st.text_input("Tarea de Mantenimiento:", value=t["tarea"])
                                col_ed1, col_ed2 = st.columns(2)
                                with col_ed1:
                                    ed_eq_frec = st.number_input("Frecuencia (días):", min_value=1, max_value=365, value=int(t["frecuencia_dias"]), step=5)
                                with col_ed2:
                                    ult_d = datetime.strptime(t["ultima_fecha"], "%Y-%m-%d").date()
                                    ed_eq_ultima = st.date_input("Último Servicio:", value=ult_d, key=f"d_ult_{t['id']}")
                                
                                prox_d = datetime.strptime(t["proxima_fecha"], "%Y-%m-%d").date()
                                ed_eq_proxima = st.date_input("Próximo Servicio:", value=prox_d, key=f"d_prox_{t['id']}")
                                ed_eq_resp = st.text_input("Responsable:", value=t["responsable"] or "Panadero Jefe")
                                ed_eq_notas = st.text_area("Notas Técnicas:", value=t["notas"] or "")
                                
                                if st.form_submit_button("💾 Guardar Cambios"):
                                    conn = get_connection()
                                    cur = conn.cursor()
                                    cur.execute("""
                                    UPDATE mantenimiento_equipos
                                    SET equipo = ?, tarea = ?, frecuencia_dias = ?, ultima_fecha = ?, proxima_fecha = ?, responsable = ?, notas = ?
                                    WHERE id = ?
                                    """, (ed_eq_nombre, ed_eq_tarea, ed_eq_frec, ed_eq_ultima.strftime("%Y-%m-%d"), ed_eq_proxima.strftime("%Y-%m-%d"), ed_eq_resp, ed_eq_notas, t["id"]))
                                    conn.commit()
                                    conn.close()
                                    st.success(f"Equipo '{ed_eq_nombre}' actualizado.")
                                    st.rerun()

                        with tab_del_eq:
                            st.caption(f"¿Deseas eliminar definitivamente '{t['equipo']}' del sistema?")
                            if st.button("⚠️ Confirmar Borrado", key=f"btn_del_eq_{t['id']}", type="secondary", use_container_width=True):
                                conn = get_connection()
                                cur = conn.cursor()
                                cur.execute("DELETE FROM mantenimiento_equipos WHERE id = ?", (t["id"],))
                                conn.commit()
                                conn.close()
                                st.warning(f"Equipo '{t['equipo']}' eliminado.")
                                st.rerun()

                st.divider()

    with st.expander("➕ Agregar Nuevo Equipo o Rutina de Mantenimiento"):
        with st.form("form_nuevo_equipo"):
            ne_nombre = st.text_input("Nombre del Equipo (ej: Cámara de Fermentación, Balanza de Precisión)")
            ne_tarea = st.text_input("Tarea a Realizar (ej: Calibración con pesas patrón, engrase)")
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                ne_frecuencia = st.number_input("Frecuencia (cada cuántos días):", min_value=1, max_value=365, value=30, step=5)
            with col_e2:
                ne_ultima = st.date_input("Fecha del último mantenimiento realizado:", value=date.today())
            ne_resp = st.text_input("Responsable:", value="Panadero Jefe")
            ne_notas = st.text_area("Observaciones o especificaciones técnicas")

            submit_equipo = st.form_submit_button("Guardar Rutina de Mantenimiento")
            if submit_equipo and ne_nombre and ne_tarea:
                proxima = ne_ultima + timedelta(days=ne_frecuencia)
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                INSERT INTO mantenimiento_equipos (equipo, tarea, frecuencia_dias, ultima_fecha, proxima_fecha, estado, responsable, notas)
                VALUES (?, ?, ?, ?, ?, 'AL DÍA', ?, ?)
                """, (ne_nombre, ne_tarea, ne_frecuencia, ne_ultima.strftime("%Y-%m-%d"), proxima.strftime("%Y-%m-%d"), ne_resp, ne_notas))
                conn.commit()
                conn.close()
                st.success(f"Mantenimiento para '{ne_nombre}' creado.")
                st.rerun()
