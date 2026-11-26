import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
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

        if resultado:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Masa Total Requerida", f"{resultado['total_masa_requerida_g']:,.0f} g", f"{resultado['total_masa_requerida_g']/1000:.2f} kg")
            m2.metric("Harina Base Total (100%)", f"{resultado['harina_base_total_g']:,.0f} g", f"{resultado['harina_base_total_g']/1000:.2f} kg")
            m3.metric("Hidratación Estimada", f"{resultado['hidratacion_porcentaje']}%")
            m4.metric("Costo Total Materia Prima", baker_math.format_cop(resultado['costo_total_lote']), f"{baker_math.format_cop(resultado['costo_por_hogaza'])} / pan")

            st.markdown("#### ⚖️ Tabla de Pesaje de Ingredientes")
            
            df_calc = pd.DataFrame(resultado["ingredientes"])
            df_display = df_calc[["nombre", "porcentaje", "gramos_por_hogaza", "gramos_lote", "unidad", "costo_linea", "stock_actual", "stock_suficiente"]].copy()
            df_display.columns = ["Ingrediente", "% Panadero", "Por Hogaza", "Total para el Lote", "Unidad", "Costo (COP)", "Stock en Bodega", "¿Hay Stock?"]
            
            # Formatear costo en COP
            df_display["Costo (COP)"] = df_display["Costo (COP)"].apply(baker_math.format_cop)
            df_display["¿Hay Stock?"] = df_display["¿Hay Stock?"].apply(lambda x: "✅ Sí" if x else "❌ Insuficiente")

            st.dataframe(
                df_display.style.format({
                    "% Panadero": "{:.1f}%",
                    "Por Hogaza": "{:.1f}",
                    "Total para el Lote": "{:,.1f}",
                    "Stock en Bodega": "{:,.0f}"
                }),
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

    with st.expander("➕ Crear Nueva Receta Estandarizada"):
        with st.form("form_nueva_receta"):
            n_nombre = st.text_input("Nombre del Pan (ej: Pan Rústico de Nueces y Arándanos)")
            n_desc = st.text_area("Descripción")
            c1, c2, c3 = st.columns(3)
            with c1:
                n_peso_crudo = st.number_input("Peso por pieza en crudo (g):", value=850.0, step=50.0)
            with c2:
                n_peso_horneado = st.number_input("Peso horneado estimado (g):", value=750.0, step=50.0)
            with c3:
                n_precio_sug = st.number_input("Precio de venta en COP ($):", value=22000, step=1000)

            submit_receta = st.form_submit_button("Guardar Nueva Receta")
            if submit_receta and n_nombre:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                INSERT INTO recetas (nombre, descripcion, peso_unitario_crudo, peso_unitario_horneado, precio_venta_sugerido)
                VALUES (?, ?, ?, ?, ?)
                """, (n_nombre, n_desc, n_peso_crudo, n_peso_horneado, n_precio_sug))
                conn.commit()
                conn.close()
                st.success(f"Receta '{n_nombre}' guardada con éxito.")
                st.rerun()

# ==========================================================
# MÓDULO 2: COSTOS Y FIJACIÓN DE PRECIOS
# ==========================================================
elif menu == "💰 2. Costos & Fijación de Precios":
    st.markdown('<div class="main-header">💰 Costos de Producción y Fijación de Precios</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Cálculo en Pesos Colombianos (COP) por unidad con margen porcentual o fijo</div>', unsafe_allow_html=True)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, peso_unitario_crudo, precio_venta_sugerido FROM recetas")
    recetas = cur.fetchall()
    conn.close()

    if not recetas:
        st.warning("No hay recetas disponibles.")
    else:
        rec_map = {r["nombre"]: r for r in recetas}
        sel_rec_nombre = st.selectbox("Seleccionar Pan para análisis de costos:", list(rec_map.keys()))
        rec_data = rec_map[sel_rec_nombre]

        calc_unitario = baker_math.calculate_production_batch(rec_data["id"], 1, rec_data["peso_unitario_crudo"])

        if calc_unitario:
            costo_materia_prima = calc_unitario["costo_total_lote"]

            col_costos, col_simulador = st.columns([1, 1])

            with col_costos:
                st.markdown("### 📋 Desglose de Costo Unitario")
                st.markdown(f"**Pan:** {sel_rec_nombre} ({rec_data['peso_unitario_crudo']}g en crudo)")
                
                df_ing_costos = pd.DataFrame(calc_unitario["ingredientes"])
                df_ing_costos["costo_cop"] = df_ing_costos["costo_linea"].apply(baker_math.format_cop)
                st.dataframe(
                    df_ing_costos[["nombre", "gramos_por_hogaza", "unidad", "costo_cop"]].rename(
                        columns={"nombre": "Insumo", "gramos_por_hogaza": "Cantidad", "unidad": "Unidad", "costo_cop": "Costo en COP"}
                    ).style.format({"Cantidad": "{:.1f}"}),
                    use_container_width=True
                )
                
                st.success(f"**Costo Total de Materia Prima por Hogaza:** {baker_math.format_cop(costo_materia_prima)}")

            with col_simulador:
                st.markdown("### 🧮 Simulador de Precio y Margen (COP)")
                
                tipo_margen = st.radio(
                    "Método de Fijación de Margen:",
                    ["Margen Porcentual sobre Venta (%)", "Markup Porcentual sobre Costo (%)", "Ganancia Fija Deseada ($ COP / pan)"]
                )

                if "sobre Venta" in tipo_margen:
                    valor_m = st.slider("Margen de Ganancia deseado (%):", min_value=10, max_value=85, value=65, step=5)
                    tipo_calc = "porcentual_margen"
                elif "sobre Costo" in tipo_margen:
                    valor_m = st.slider("Markup sobre costo (%):", min_value=50, max_value=400, value=200, step=10)
                    tipo_calc = "porcentual_markup"
                else:
                    valor_m = st.number_input("Ganancia fija deseada por pan ($ COP):", min_value=1000, max_value=100000, value=15000, step=1000)
                    tipo_calc = "monto_fijo"

                res_precio = baker_math.calculate_pricing(costo_materia_prima, tipo_calc, valor_m)

                st.markdown("---")
                col_p1, col_p2, col_p3 = st.columns(3)
                col_p1.metric("Precio Venta Sugerido", baker_math.format_cop(res_precio['precio_venta']))
                col_p2.metric("Ganancia Neta por Pan", baker_math.format_cop(res_precio['ganancia_por_unidad']))
                col_p3.metric("Margen Real Bruto", f"{res_precio['margen_real_pct']:.1f}%")

                if st.button("💾 Actualizar Precio Sugerido en la Receta"):
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("UPDATE recetas SET precio_venta_sugerido = ? WHERE id = ?", (res_precio["precio_venta"], rec_data["id"]))
                    conn.commit()
                    conn.close()
                    st.success(f"Precio de {baker_math.format_cop(res_precio['precio_venta'])} guardado para {sel_rec_nombre}.")

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

    st.markdown("### 📋 Existencias Actuales en Bodega")
    st.dataframe(
        df_stock[["id", "nombre", "categoria", "stock_actual", "stock_minimo", "unidad_medida", "Costo COP", "Estado"]].rename(
            columns={
                "id": "ID", "nombre": "Insumo", "categoria": "Categoría",
                "stock_actual": "Stock Actual", "stock_minimo": "Stock Mínimo",
                "unidad_medida": "Unidad", "Costo COP": "Costo Unitario (COP)"
            }
        ).style.format({
            "Stock Actual": "{:,.1f}",
            "Stock Mínimo": "{:,.1f}"
        }),
        use_container_width=True
    )

    col_inv1, col_inv2 = st.columns(2)

    with col_inv1:
        st.markdown("### 📥 Entrada de Insumos (Registrar Compra)")
        with st.form("form_entrada_stock"):
            ing_map_nombres = {i["nombre"]: i for i in ingredientes}
            sel_ing_compra = st.selectbox("Seleccionar Insumo:", list(ing_map_nombres.keys()))
            insumo_obj = ing_map_nombres[sel_ing_compra]
            
            cant_ing_compra = st.number_input(f"Cantidad a sumar ({insumo_obj['unidad_medida']}):", min_value=0.1, value=10000.0, step=1000.0)
            nuevo_costo = st.number_input(f"Costo por {insumo_obj['unidad_medida']} en COP (actualizar si cambió):", min_value=0.0, value=float(insumo_obj["costo_unitario"]), step=0.5)
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

                # Guardar en session_state para mostrar notificación visual evidente
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
        st.markdown("### ➕ Registrar Nuevo Insumo al Catálogo")
        with st.form("form_nuevo_insumo"):
            n_insumo_nombre = st.text_input("Nombre del Insumo (ej: Harina Integral Orgánica)")
            n_cat = st.selectbox("Categoría:", ["harina", "liquido", "fermento", "aditivo", "empaque"])
            n_unidad = st.selectbox("Unidad de Medida:", ["g", "kg", "unidad", "ml"])
            c_s1, c_s2 = st.columns(2)
            with c_s1:
                n_stock_ini = st.number_input("Stock Inicial:", min_value=0.0, value=25000.0, step=1000.0)
            with c_s2:
                n_stock_min = st.number_input("Stock Mínimo Alerta:", min_value=0.0, value=5000.0, step=1000.0)
            n_costo_u = st.number_input("Costo por gramo/unidad en COP ($):", min_value=0.0, value=5.0, step=0.5)

            submit_insumo = st.form_submit_button("Crear Insumo")
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
        st.dataframe(
            df_ue.rename(columns={"fecha": "Fecha y Hora", "insumo": "Insumo", "cantidad": "Cantidad Ingresada", "unidad_medida": "Unidad", "referencia": "Referencia"}).style.format({"Cantidad Ingresada": "+{:,.1f}"}),
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
                    c1.write(f"**Programado:** {lote['unidades_programadas']} hogazas ({lote['peso_hogaza_g']:g}g)")
                    c2.write(f"**Reservado en preventa:** {lote['unidades_reservadas']} hogazas")
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
                        st.markdown(f"**Pedido #{p['id']} - {p['cliente_nombre']}** <span class='badge-tag {badge_tipo}'>{p['tipo_cliente']}</span>", unsafe_allow_html=True)
                        st.markdown(f"🥖 **{p['unidades']}x {p['pan_nombre']}** | 📅 Entrega: **{p['fecha_entrega']}** | Lote: `{p['codigo_lote'] or 'Sin asignar'}`")
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
                st.dataframe(df_min[["nombre", "telefono", "direccion", "preferencias"]].rename(
                    columns={"nombre": "Nombre", "telefono": "Teléfono / WhatsApp", "direccion": "Dirección", "preferencias": "Preferencias de Pan"}
                ), use_container_width=True)
            else:
                st.info("No hay clientes minoristas registrados.")

        with subtab_may:
            st.markdown("#### Clientes al Por Mayor (Cafeterías, Bistrós, Restaurantes, Hoteles)")
            if clientes_may:
                df_may = pd.DataFrame(clientes_may)
                st.dataframe(df_may[["nombre", "telefono", "direccion", "preferencias"]].rename(
                    columns={"nombre": "Razón Social / Nombre", "telefono": "Contacto / WhatsApp", "direccion": "Dirección de Entrega", "preferencias": "Condiciones / Preferencias Comerciales"}
                ), use_container_width=True)
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
                use_container_width=True
            )
        else:
            st.info("No hay gastos registrados en el período seleccionado.")

# ==========================================================
# MÓDULO 7: CALENDARIO DE ACTIVIDADES (NUEVO)
# ==========================================================
elif menu == "📅 7. Calendario de Actividades":
    st.markdown('<div class="main-header">📅 Calendario de Actividades & Ritmo Semanal</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Planificación operativa del obrador: compra de insumos, apertura/cierre de preventa y días de horneado</div>', unsafe_allow_html=True)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM calendario_actividades ORDER BY fecha ASC, id ASC")
    actividades = cur.fetchall()
    conn.close()

    col_cal_top1, col_cal_top2 = st.columns([2, 1])

    with col_cal_top1:
        st.markdown("### 🗓️ Agenda de Operaciones")
        filtro_estado_cal = st.radio("Mostrar:", ["Todas las Actividades", "Solo Pendientes", "Solo Completadas"], horizontal=True)

    with col_cal_top2:
        st.write("")
        st.caption("Organiza tus días de compra, refrescos de masa madre, apertura de preventa, amasado y entrega.")

    # Filtrar
    actividades_filtradas = []
    for a in actividades:
        if filtro_estado_cal == "Solo Pendientes" and a["completada"] == 1:
            continue
        if filtro_estado_cal == "Solo Completadas" and a["completada"] == 0:
            continue
        actividades_filtradas.append(a)

    if not actividades_filtradas:
        st.info("No hay actividades registradas en esta vista.")
    else:
        for a in actividades_filtradas:
            with st.container():
                c_chk, c_act_info, c_del = st.columns([0.5, 5, 0.8])
                with c_chk:
                    chk_val = bool(a["completada"])
                    if st.checkbox("", value=chk_val, key=f"chk_act_{a['id']}"):
                        if not chk_val:
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute("UPDATE calendario_actividades SET completada = 1 WHERE id = ?", (a["id"],))
                            conn.commit()
                            conn.close()
                            st.rerun()
                    else:
                        if chk_val:
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute("UPDATE calendario_actividades SET completada = 0 WHERE id = ?", (a["id"],))
                            conn.commit()
                            conn.close()
                            st.rerun()

                with c_act_info:
                    tachado = "~~" if a["completada"] == 1 else ""
                    st.markdown(f"**{tachado}{a['fecha']} | {a['tipo_actividad']}: {a['titulo']}{tachado}**")
                    if a["descripcion"]:
                        st.caption(f"{a['descripcion']}")

                with c_del:
                    if st.button("🗑️", key=f"del_act_{a['id']}", help="Eliminar actividad"):
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM calendario_actividades WHERE id = ?", (a["id"],))
                        conn.commit()
                        conn.close()
                        st.rerun()

                st.divider()

    # Formulario para agendar nueva actividad
    with st.expander("➕ Agendar Nueva Actividad Operativa"):
        with st.form("form_nueva_actividad"):
            c_f1, c_f2 = st.columns([1, 1])
            with c_f1:
                act_fecha = st.date_input("Fecha Programada:", value=date.today())
            with c_f2:
                act_tipo = st.selectbox(
                    "Tipo de Actividad:",
                    [
                        "🛒 Compra de Insumos & Harinas",
                        "📢 Apertura de Preventa (WhatsApp/Redes)",
                        "🔒 Cierre de Pedidos",
                        "🥣 Amasado, Autólisis y Formado",
                        "🔥 Día de Horneado & Empaque",
                        "📦 Despacho y Entrega de Pedidos",
                        "🌾 Refresco de Masa Madre",
                        "🧹 Mantenimiento y Limpieza"
                    ]
                )

            act_titulo = st.text_input("Título de la Tarea (ej: Comprar 2 bultos de harina de fuerza en molino)")
            act_desc = st.text_area("Detalles u observaciones")

            submit_act = st.form_submit_button("Guardar en Calendario", type="primary")
            if submit_act and act_titulo:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                INSERT INTO calendario_actividades (fecha, tipo_actividad, titulo, descripcion, completada)
                VALUES (?, ?, ?, ?, 0)
                """, (act_fecha.strftime("%Y-%m-%d"), act_tipo, act_titulo, act_desc))
                conn.commit()
                conn.close()
                st.success(f"Actividad '{act_titulo}' agendada.")
                st.rerun()

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
                st.write("")
                if st.button("✅ Marcar Realizado Hoy", key=f"btn_maint_{t['id']}", type="primary"):
                    baker_math.complete_maintenance(t["id"])
                    st.success(f"Mantenimiento registrado para {t['equipo']}. Próxima fecha calculada automáticamente.")
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
