import streamlit as st
import pandas as pd
from datetime import datetime, date
import sqlite3

from database import init_db, get_connection
import baker_math

# Configuración de página
st.set_page_config(
    page_title="PALVETI - Panadería Artesanal",
    page_icon="🥖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar Base de Datos con datos semilla si es primera vez
init_db()

# Estilos CSS personalizados con temática artesanal y Tailwind Red-800 (#991b1b) para Sidebar
st.markdown("""
<style>
    :root {
        --primary-color: #991b1b; /* Tailwind red-800 */
        --primary-dark: #7f1d1d;  /* Tailwind red-900 */
        --primary-light: #b91c1c; /* Tailwind red-700 */
        --bg-light: #FBF9F5;
        --accent-gold: #D4A373;
    }

    /* ======================================================== */
    /* SIDEBAR: TAILWIND RED-800 (#991b1b) & TEXTO OPTIMIZADO   */
    /* ======================================================== */
    [data-testid="stSidebar"], 
    [data-testid="stSidebar"] > div:first-child,
    section[data-testid="stSidebar"],
    [data-testid="stSidebarContent"],
    div[data-testid="stSidebarUserContent"] {
        background-color: #991b1b !important;
        color: #fef2f2 !important;
    }

    /* Títulos y textos generales del sidebar */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label {
        color: #fef2f2 !important;
    }

    /* Líneas separadoras */
    [data-testid="stSidebar"] hr {
        border-color: rgba(254, 226, 226, 0.25) !important;
        margin: 15px 0 !important;
    }

    /* Título principal de la panadería */
    .brand-title {
        font-family: 'Georgia', serif;
        font-size: 1.85rem;
        font-weight: 800;
        color: #ffffff !important;
        letter-spacing: 0.5px;
        margin-bottom: 2px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .brand-subtitle {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 0.95rem;
        color: #fecaca !important; /* Tailwind red-200 */
        font-weight: 500;
        margin-bottom: 12px;
    }

    .nav-header-text {
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #fca5a5 !important; /* Tailwind red-300 */
        margin-bottom: 8px;
    }

    /* ======================================================== */
    /* MÓDULOS DE NAVEGACIÓN (RADIO BUTTONS)                     */
    /* ======================================================== */
    [data-testid="stSidebar"] [data-testid="stRadio"] > label {
        display: none !important; /* Ocultar etiqueta por defecto */
    }

    [data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 6px !important;
    }

    /* Cada botón / módulo de navegación */
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        background-color: rgba(255, 255, 255, 0.08) !important;
        padding: 9px 12px !important;
        border-radius: 8px !important;
        margin-bottom: 4px !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.15) !important;
    }

    /* Hover sobre un módulo */
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: rgba(255, 255, 255, 0.18) !important;
        border-color: rgba(255, 255, 255, 0.35) !important;
        transform: translateX(3px);
    }

    /* Módulo seleccionado / Activo */
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"],
    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
        background-color: #7f1d1d !important; /* Tailwind red-900 para contraste */
        border: 1.5px solid #fca5a5 !important; /* Borde iluminado red-300 */
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.35) !important;
    }

    /* Texto dentro de los módulos */
    [data-testid="stSidebar"] div[role="radiogroup"] label p,
    [data-testid="stSidebar"] div[role="radiogroup"] label span {
        color: #ffffff !important;
        font-size: 0.93rem !important;
        font-weight: 600 !important;
    }

    /* Color del círculo del radio button */
    [data-testid="stSidebar"] div[role="radiogroup"] input[type="radio"] {
        accent-color: #ffffff !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] svg {
        fill: #ffffff !important;
    }

    /* Expanders y alertas en el sidebar */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background-color: rgba(0, 0, 0, 0.25) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] summary {
        color: #ffffff !important;
    }

    .sidebar-footer-text {
        font-size: 0.8rem;
        color: #fca5a5 !important; /* Tailwind red-300 */
        line-height: 1.4;
        text-align: center;
        margin-top: 10px;
    }

    /* ======================================================== */
    /* CONTENIDO PRINCIPAL                                      */
    /* ======================================================== */
    .main-header {
        font-family: 'Georgia', serif;
        font-size: 2.3rem;
        color: #991b1b; /* Tailwind red-800 para headers */
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
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #EADBCE;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .badge-hydration {
        background-color: #E8F4F8;
        color: #1976D2;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .badge-cost {
        background-color: #EBF7EE;
        color: #2E7D32;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .stock-alert {
        background-color: #FDEDEC;
        border-left: 5px solid #E74C3C;
        padding: 10px 15px;
        margin-bottom: 15px;
        border-radius: 4px;
        color: #922B21;
    }
</style>
""", unsafe_allow_html=True)

# Barra Lateral
st.sidebar.markdown("""
<div class="brand-title">🥖 PALVETI</div>
<div class="brand-subtitle">Gestión Artesanal de Masa Madre</div>
<hr>
<div class="nav-header-text">Navegación:</div>
""", unsafe_allow_html=True)

# Alerta de Stock en Barra Lateral
alertas_stock = baker_math.get_low_stock_alerts()
if alertas_stock:
    st.sidebar.markdown(f"⚠️ **Atención:** {len(alertas_stock)} insumo(s) con stock bajo.")
    with st.sidebar.expander("Ver alertas de stock"):
        for a in alertas_stock:
            st.error(f"**{a['nombre']}**: {a['stock_actual']} {a['unidad_medida']} (Mínimo: {a['stock_minimo']})")

menu = st.sidebar.radio(
    "Navegación:",
    [
        "🥖 1. Calculadora & Recetas (Núcleo)",
        "💰 2. Costos & Fijación de Precios",
        "📦 3. Inventario & Materia Prima",
        "📋 4. Pedidos & Preventa (Lotes)",
        "🌡️ 5. Bitácora de Fermentación & Calidad",
        "📊 6. Finanzas & Reportes"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("""
<hr>
<div class="sidebar-footer-text">
    <b>PALVETI v1.0</b><br>
    Base de Datos Local SQLite<br>
    Masa Madre Artesanal
</div>
""", unsafe_allow_html=True)

# ==========================================================
# MÓDULO 1: CALCULADORA DE PRODUCCIÓN Y RECETAS
# ==========================================================
if menu == "🥖 1. Calculadora & Recetas (Núcleo)":
    st.markdown('<div class="main-header">🥖 Calculadora de Producción & Recetas</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Porcentajes de panadero dinámicos y escalado exacto por hogaza</div>', unsafe_allow_html=True)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, peso_unitario_crudo FROM recetas ORDER BY nombre")
    recetas_disponibles = cursor.fetchall()
    conn.close()

    if not recetas_disponibles:
        st.warning("No hay recetas registradas. Puedes agregar una a continuación.")
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

        # Cálculo de Porcentaje de Panadero
        resultado = baker_math.calculate_production_batch(receta_id, unidades_deseadas, peso_por_hogaza)

        if resultado:
            # Métricas rápidas del cálculo
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Masa Total Requerida", f"{resultado['total_masa_requerida_g']:,.0f} g", f"{resultado['total_masa_requerida_g']/1000:.2f} kg")
            m2.metric("Harina Base Total (100%)", f"{resultado['harina_base_total_g']:,.0f} g", f"{resultado['harina_base_total_g']/1000:.2f} kg")
            m3.metric("Hidratación Estimada", f"{resultado['hidratacion_porcentaje']}%")
            m4.metric("Costo Total Materia Prima", f"${resultado['costo_total_lote']:.2f}", f"${resultado['costo_por_hogaza']:.2f} / pan")

            st.markdown("#### ⚖️ Tabla de Pesaje de Ingredientes")
            
            # Tabla de ingredientes
            df_calc = pd.DataFrame(resultado["ingredientes"])
            df_display = df_calc[["nombre", "porcentaje", "gramos_por_hogaza", "gramos_lote", "unidad", "costo_linea", "stock_actual", "stock_suficiente"]].copy()
            df_display.columns = ["Ingrediente", "% Panadero", "Por Hogaza", "Total para el Lote", "Unidad", "Costo ($)", "Stock en Bodega", "¿Hay Stock?"]
            
            st.dataframe(
                df_display.style.format({
                    "% Panadero": "{:.1f}%",
                    "Por Hogaza": "{:.1f}",
                    "Total para el Lote": "{:,.1f}",
                    "Costo ($)": "${:.2f}",
                    "Stock en Bodega": "{:,.0f}"
                }),
                use_container_width=True
            )

            # Botón directo para crear Lote de Producción
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
                        # Crear bitácora vacía para este lote
                        cur.execute("INSERT INTO bitacora_fermentacion (lote_id, temp_ambiente_amasado_c) VALUES (?, 24.0)", (nuevo_lote_id,))
                        conn.commit()
                        st.success(f"✅ ¡Lote **{codigo_nuevo_lote}** registrado con éxito! Puedes gestionarlo en el módulo de Lotes y Bitácora.")
                    except sqlite3.IntegrityError:
                        st.error(f"El código de lote {codigo_nuevo_lote} ya existe. Modifícalo antes de guardar.")
                    finally:
                        conn.close()

    # Sección para agregar nueva Receta
    with st.expander("➕ Crear Nueva Receta Estandarizada"):
        st.markdown("Define una nueva receta base con sus porcentajes de panadero.")
        with st.form("form_nueva_receta"):
            n_nombre = st.text_input("Nombre del Pan (ej: Pan Rústico de Nueces y Arándanos)")
            n_desc = st.text_area("Descripción")
            c1, c2, c3 = st.columns(3)
            with c1:
                n_peso_crudo = st.number_input("Peso por pieza en crudo (g):", value=850.0, step=50.0)
            with c2:
                n_peso_horneado = st.number_input("Peso horneado estimado (g):", value=750.0, step=50.0)
            with c3:
                n_precio_sug = st.number_input("Precio de venta estimado ($):", value=6.0, step=0.5)

            st.info("💡 Una vez creada la receta, podrás asociarle ingredientes y porcentajes en la base de datos.")
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
                st.success(f"Receta '{n_nombre}' guardada con éxito. Actualiza la página para usarla.")

# ==========================================================
# MÓDULO 2: COSTOS Y FIJACIÓN DE PRECIOS
# ==========================================================
elif menu == "💰 2. Costos & Fijación de Precios":
    st.markdown('<div class="main-header">💰 Costos de Producción y Fijación de Precios</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Cálculo de costo por unidad basado en recetas e insumos con margen comercial</div>', unsafe_allow_html=True)

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

        # Calculamos el costo base para 1 unidad
        calc_unitario = baker_math.calculate_production_batch(rec_data["id"], 1, rec_data["peso_unitario_crudo"])

        if calc_unitario:
            costo_materia_prima = calc_unitario["costo_total_lote"]

            col_costos, col_simulador = st.columns([1, 1])

            with col_costos:
                st.markdown("### 📋 Desglose de Costo Unitario")
                st.markdown(f"**Pan:** {sel_rec_nombre} ({rec_data['peso_unitario_crudo']}g en crudo)")
                
                df_ing_costos = pd.DataFrame(calc_unitario["ingredientes"])
                st.dataframe(
                    df_ing_costos[["nombre", "gramos_por_hogaza", "unidad", "costo_linea"]].rename(
                        columns={"nombre": "Insumo", "gramos_por_hogaza": "Cantidad", "unidad": "Unidad", "costo_linea": "Costo ($)"}
                    ).style.format({"Cantidad": "{:.1f}", "Costo ($)": "${:.3f}"}),
                    use_container_width=True
                )
                
                st.success(f"**Costo Total de Materia Prima por Hogaza:** ${costo_materia_prima:.3f}")

            with col_simulador:
                st.markdown("### 🧮 Simulador de Precio y Margen")
                
                tipo_margen = st.radio(
                    "Método de Fijación de Margen:",
                    ["Margen Porcentual sobre Venta (%)", "Markup Porcentual sobre Costo (%)", "Ganancia Fija Deseada ($/pan)"]
                )

                if "sobre Venta" in tipo_margen:
                    valor_m = st.slider("Margen de Ganancia deseado (%):", min_value=10, max_value=85, value=65, step=5)
                    tipo_calc = "porcentual_margen"
                elif "sobre Costo" in tipo_margen:
                    valor_m = st.slider("Markup sobre costo (%):", min_value=50, max_value=400, value=200, step=10)
                    tipo_calc = "porcentual_markup"
                else:
                    valor_m = st.number_input("Ganancia fija por hogaza ($):", min_value=0.5, max_value=50.0, value=4.0, step=0.5)
                    tipo_calc = "monto_fijo"

                res_precio = baker_math.calculate_pricing(costo_materia_prima, tipo_calc, valor_m)

                st.markdown("---")
                col_p1, col_p2, col_p3 = st.columns(3)
                col_p1.metric("Precio Venta Sugerido", f"${res_precio['precio_venta']:.2f}")
                col_p2.metric("Ganancia por Pan", f"${res_precio['ganancia_por_unidad']:.2f}")
                col_p3.metric("Margen Real Bruto", f"{res_precio['margen_real_pct']:.1f}%")

                if st.button("💾 Actualizar Precio Sugerido en la Receta"):
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("UPDATE recetas SET precio_venta_sugerido = ? WHERE id = ?", (res_precio["precio_venta"], rec_data["id"]))
                    conn.commit()
                    conn.close()
                    st.success(f"Precio sugerido de ${res_precio['precio_venta']:.2f} guardado para {sel_rec_nombre}.")

# ==========================================================
# MÓDULO 3: INVENTARIO Y MATERIA PRIMA
# ==========================================================
elif menu == "📦 3. Inventario & Materia Prima":
    st.markdown('<div class="main-header">📦 Inventario & Materia Prima</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Control de existencias, alerta de mínimos y descuento por lotes</div>', unsafe_allow_html=True)

    # Alertas visibles
    alertas = baker_math.get_low_stock_alerts()
    if alertas:
        st.markdown(f'<div class="stock-alert">⚠️ <b>ALERTA DE REABASTECIMIENTO:</b> Hay {len(alertas)} insumo(s) por debajo o igual al stock mínimo de seguridad.</div>', unsafe_allow_html=True)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ingredientes ORDER BY categoria, nombre")
    ingredientes = cur.fetchall()
    conn.close()

    df_stock = pd.DataFrame([dict(i) for i in ingredientes])
    
    # Agregar columna de estado
    def calcular_estado(row):
        if row["stock_actual"] <= 0:
            return "🔴 Agotado"
        elif row["stock_actual"] <= row["stock_minimo"]:
            return "🟡 Stock Bajo"
        return "🟢 Normal"

    df_stock["Estado"] = df_stock.apply(calcular_estado, axis=1)

    st.dataframe(
        df_stock[["id", "nombre", "categoria", "stock_actual", "stock_minimo", "unidad_medida", "costo_unitario", "Estado"]].rename(
            columns={
                "id": "ID", "nombre": "Insumo", "categoria": "Categoría",
                "stock_actual": "Stock Actual", "stock_minimo": "Stock Mínimo",
                "unidad_medida": "Unidad", "costo_unitario": "Costo/Unidad ($)"
            }
        ).style.format({
            "Stock Actual": "{:,.1f}",
            "Stock Mínimo": "{:,.1f}",
            "Costo/Unidad ($)": "${:.4f}"
        }),
        use_container_width=True
    )

    col_inv1, col_inv2 = st.columns(2)

    with col_inv1:
        st.markdown("### 📥 Entrada de Insumos (Compra/Reabastecimiento)")
        with st.form("form_entrada_stock"):
            ing_map_nombres = {i["nombre"]: i["id"] for i in ingredientes}
            sel_ing_compra = st.selectbox("Insumo:", list(ing_map_nombres.keys()))
            cant_ing_compra = st.number_input("Cantidad a sumar al stock:", min_value=0.1, value=5000.0, step=500.0)
            nuevo_costo = st.number_input("Actualizar costo unitario si cambió ($):", min_value=0.0, value=0.0, step=0.0001, format="%.4f")
            referencia_compra = st.text_input("Nota o N° Factura Proveedor:", value="Compra semanal molino")

            submit_compra = st.form_submit_button("Registrar Entrada de Stock")
            if submit_compra:
                ing_id = ing_map_nombres[sel_ing_compra]
                conn = get_connection()
                cur = conn.cursor()
                if nuevo_costo > 0:
                    cur.execute("UPDATE ingredientes SET stock_actual = stock_actual + ?, costo_unitario = ? WHERE id = ?", (cant_ing_compra, nuevo_costo, ing_id))
                else:
                    cur.execute("UPDATE ingredientes SET stock_actual = stock_actual + ? WHERE id = ?", (cant_ing_compra, ing_id))
                
                cur.execute("""
                INSERT INTO movimientos_inventario (ingrediente_id, tipo_movimiento, cantidad, referencia)
                VALUES (?, 'ENTRADA_COMPRA', ?, ?)
                """, (ing_id, cant_ing_compra, referencia_compra))
                conn.commit()
                conn.close()
                st.success(f"Se agregaron {cant_ing_compra} al inventario de {sel_ing_compra}.")
                st.rerun()

    with col_inv2:
        st.markdown("### ➕ Registrar Nuevo Insumo")
        with st.form("form_nuevo_insumo"):
            n_insumo_nombre = st.text_input("Nombre del Insumo (ej: Harina Integral Trigo Sarraceno)")
            n_cat = st.selectbox("Categoría:", ["harina", "liquido", "fermento", "aditivo", "empaque"])
            n_unidad = st.selectbox("Unidad de Medida:", ["g", "kg", "unidad", "ml"])
            c_s1, c_s2 = st.columns(2)
            with c_s1:
                n_stock_ini = st.number_input("Stock Inicial:", min_value=0.0, value=10000.0, step=1000.0)
            with c_s2:
                n_stock_min = st.number_input("Stock Mínimo Alerta:", min_value=0.0, value=3000.0, step=500.0)
            n_costo_u = st.number_input("Costo por gramo/unidad ($):", min_value=0.0, value=0.002, format="%.4f", step=0.0005)

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
                st.success(f"Insumo {n_insumo_nombre} creado correctamente.")
                st.rerun()

# ==========================================================
# MÓDULO 4: GESTIÓN DE PEDIDOS Y LOTES (PREVENTA)
# ==========================================================
elif menu == "📋 4. Pedidos & Preventa (Lotes)":
    st.markdown('<div class="main-header">📋 Pedidos & Preventa de Lotes</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Organización por fecha de horneado, estados del pedido y cartera de clientes</div>', unsafe_allow_html=True)

    tab_lotes, tab_pedidos, tab_clientes = st.tabs(["🔥 Lotes de Producción", "📦 Pedidos de Clientes", "👥 Directorio de Clientes"])

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
                    c1.write(f"**Programado:** {lote['unidades_programadas']} hogazas ({lote['peso_hogaza_g']}g)")
                    c2.write(f"**Reservado en preventa:** {lote['unidades_reservadas']} hogazas")
                    c3.write(f"**Costo Estimado Lote:** ${lote['costo_total_lote']:.2f}")
                    c4.write(f"**Inventario Descontado:** {'✅ Sí' if lote['inventario_descontado'] == 1 else '❌ Pendiente'}")

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
                            st.write("**Descuento Automático:**")
                            if st.button("📉 Descontar Ingredientes de Bodega", type="secondary", key=f"desc_inv_{lote['id']}"):
                                ok, msg = baker_math.discount_inventory_for_batch(lote["id"])
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                        else:
                            st.info("Los insumos de este lote ya fueron descontados del inventario.")

    with tab_pedidos:
        st.markdown("### 🛒 Registro y Estado de Pedidos")
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
        SELECT p.*, c.nombre as cliente_nombre, c.telefono as cliente_telefono, r.nombre as pan_nombre, l.codigo_lote
        FROM pedidos p
        JOIN clientes c ON p.cliente_id = c.id
        JOIN recetas r ON p.receta_id = r.id
        LEFT JOIN lotes_produccion l ON p.lote_id = l.id
        ORDER BY p.fecha_entrega DESC, p.id DESC
        """)
        pedidos = cur.fetchall()
        conn.close()

        if pedidos:
            for p in pedidos:
                with st.container():
                    col_pinfo, col_pestado = st.columns([3, 1])
                    with col_pinfo:
                        st.markdown(f"**Pedido #{p['id']} - {p['cliente_nombre']}** ({p['cliente_telefono']})")
                        st.markdown(f"🥖 **{p['unidades']}x {p['pan_nombre']}** | 📅 Entrega: **{p['fecha_entrega']}** | Lote: `{p['codigo_lote'] or 'Sin asignar'}` | Total: **${p['total_cobrado']:.2f}** ({p['metodo_pago']})")
                        if p["notas"]:
                            st.caption(f"Nota: {p['notas']}")
                    with col_pestado:
                        estados_pedido = ["REGISTRADO", "PAGADO", "EN_FERMENTACION", "HORNEADO", "ENTREGADO"]
                        idx_est = estados_pedido.index(p["estado"]) if p["estado"] in estados_pedido else 0
                        sel_est = st.selectbox("Estado:", estados_pedido, index=idx_est, key=f"ped_est_{p['id']}")
                        if sel_est != p["estado"]:
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute("UPDATE pedidos SET estado = ? WHERE id = ?", (sel_est, p["id"]))
                            conn.commit()
                            conn.close()
                            st.success(f"Pedido #{p['id']} -> {sel_est}")
                            st.rerun()
                    st.divider()

        # Formulario para Nuevo Pedido
        with st.expander("➕ Registrar Nuevo Pedido"):
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, nombre FROM clientes ORDER BY nombre")
            clientes_db = cur.fetchall()
            cur.execute("SELECT id, nombre, precio_venta_sugerido FROM recetas ORDER BY nombre")
            recetas_db = cur.fetchall()
            cur.execute("SELECT id, codigo_lote FROM lotes_produccion WHERE estado != 'FINALIZADO' ORDER BY id DESC")
            lotes_db = cur.fetchall()
            conn.close()

            with st.form("form_nuevo_pedido"):
                c_map = {c["nombre"]: c["id"] for c in clientes_db}
                r_map = {r["nombre"]: (r["id"], r["precio_venta_sugerido"]) for r in recetas_db}
                l_map = {l["codigo_lote"]: l["id"] for l in lotes_db}
                l_map["(Sin lote asignado)"] = None

                np_cliente = st.selectbox("Cliente:", list(c_map.keys()))
                np_pan = st.selectbox("Pan Solicitado:", list(r_map.keys()))
                np_lote = st.selectbox("Asignar a Lote de Horneado:", list(l_map.keys()))
                
                cp1, cp2, cp3 = st.columns(3)
                with cp1:
                    np_cant = st.number_input("Unidades:", min_value=1, value=1, step=1)
                with cp2:
                    precio_sug = r_map[np_pan][1]
                    np_total = st.number_input("Total a Cobrar ($):", min_value=0.0, value=float(precio_sug * np_cant), step=0.5)
                with cp3:
                    np_pago = st.selectbox("Método de Pago:", ["Transferencia", "Efectivo", "Tarjeta"])

                np_fecha = st.date_input("Fecha de Entrega:", value=date.today())
                np_notas = st.text_input("Notas de entrega (ej: rebanado, recoger en taller)")

                submit_pedido = st.form_submit_button("Guardar Pedido")
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

    with tab_clientes:
        st.markdown("### 👥 Directorio de Clientes")
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM clientes ORDER BY nombre")
        clientes = cur.fetchall()
        conn.close()

        df_cli = pd.DataFrame([dict(c) for c in clientes])
        st.dataframe(df_cli[["id", "nombre", "telefono", "direccion", "preferencias"]].rename(
            columns={"id": "ID", "nombre": "Nombre", "telefono": "Teléfono", "direccion": "Dirección", "preferencias": "Preferencias de Pan"}
        ), use_container_width=True)

        with st.expander("➕ Añadir Nuevo Cliente"):
            with st.form("form_nuevo_cliente"):
                nc_nom = st.text_input("Nombre Completo:")
                nc_tel = st.text_input("Teléfono / WhatsApp:")
                nc_dir = st.text_input("Dirección de Entrega:")
                nc_pref = st.text_area("Preferencias (ej: hogazas bien tostadas, semillas, sin rebanar)")

                submit_cliente = st.form_submit_button("Guardar Cliente")
                if submit_cliente and nc_nom:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("""
                    INSERT INTO clientes (nombre, telefono, direccion, preferencias)
                    VALUES (?, ?, ?, ?)
                    """, (nc_nom, nc_tel, nc_dir, nc_pref))
                    conn.commit()
                    conn.close()
                    st.success(f"Cliente {nc_nom} agregado.")
                    st.rerun()

# ==========================================================
# MÓDULO 5: BITÁCORA DE FERMENTACIÓN Y CALIDAD
# ==========================================================
elif menu == "🌡️ 5. Bitácora de Fermentación & Calidad":
    st.markdown('<div class="main-header">🌡️ Bitácora de Fermentación & Control de Calidad</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Registro técnico de temperatura, tiempos y calidad organoléptica por lote</div>', unsafe_allow_html=True)

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
            with col_temp1:
                t_amb = st.number_input("Temperatura Ambiente Amasado (°C):", value=float(reg["temp_ambiente_amasado_c"] or 24.0), step=0.5)
            with col_temp2:
                t_masa = st.number_input("Temperatura Final de la Masa (°C):", value=float(reg["temp_final_masa_c"] or 25.0), step=0.5)
            with col_temp3:
                t_nevera = st.number_input("Temperatura Nevera Retardo (°C):", value=float(reg["temp_nevera_c"] or 4.0), step=0.5)

            st.markdown("#### ⏱️ Tiempos de Fermentación")
            col_t1, col_t2, col_t3, col_t4 = st.columns(4)
            with col_t1:
                autolisis = st.number_input("Autólisis (minutos):", value=int(reg["duracion_autolisis_min"] or 30), step=10)
            with col_t2:
                bloque_hrs = st.number_input("Fermentación en Bloque (horas):", value=float(reg["tiempo_bloque_horas"] or 4.0), step=0.5)
            with col_t3:
                pliegues = st.number_input("Pliegues / Folds realizados:", value=int(reg["pliegues_realizados"] or 3), step=1)
            with col_t4:
                frio_hrs = st.number_input("Retardo en Frío (horas):", value=float(reg["tiempo_retardo_frio_horas"] or 16.0), step=1.0)

            st.markdown("#### ⭐ Evaluación Organoléptica de Calidad")
            col_q1, col_q2 = st.columns([1, 2])
            with col_q1:
                estrellas = st.slider("Calificación Global (1 a 5 estrellas):", min_value=1, max_value=5, value=int(reg["evaluacion_calidad"] or 5))
            with col_q2:
                obs = st.text_area("Observaciones (greña, alveolado, acidez, salto de horno, corteza):", value=reg["observaciones_calidad"] or "")

            submit_bitacora = st.form_submit_button("💾 Guardar Datos en Bitácora")
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

        # Histórico comparativo
        st.markdown("---")
        st.markdown("### 📊 Histórico de Fermentaciones para Estandarización")
        df_hist = pd.DataFrame([dict(r) for r in registros if r["evaluacion_calidad"] is not None])
        if not df_hist.empty:
            st.dataframe(
                df_hist[["codigo_lote", "receta_nombre", "temp_ambiente_amasado_c", "temp_final_masa_c", "tiempo_bloque_horas", "tiempo_retardo_frio_horas", "evaluacion_calidad", "observaciones_calidad"]].rename(
                    columns={
                        "codigo_lote": "Lote", "receta_nombre": "Pan",
                        "temp_ambiente_amasado_c": "T. Amb (°C)", "temp_final_masa_c": "T. Masa (°C)",
                        "tiempo_bloque_horas": "Bloque (h)", "tiempo_retardo_frio_horas": "Frío (h)",
                        "evaluacion_calidad": "Estrellas (1-5)", "observaciones_calidad": "Observaciones"
                    }
                ),
                use_container_width=True
            )

# ==========================================================
# MÓDULO 6: FINANZAS Y REPORTES
# ==========================================================
elif menu == "📊 6. Finanzas & Reportes":
    st.markdown('<div class="main-header">📊 Finanzas & Reportes Operativos</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Métricas de ingresos, costos de producción, gastos y rentabilidad neta</div>', unsafe_allow_html=True)

    conn = get_connection()
    cur = conn.cursor()

    # Ventas totales
    cur.execute("SELECT COUNT(*) as num_pedidos, COALESCE(SUM(unidades), 0) as total_hogazas, COALESCE(SUM(total_cobrado), 0) as total_ventas FROM pedidos")
    v_data = cur.fetchone()

    # Costos de lotes producidos
    cur.execute("SELECT COALESCE(SUM(costo_total_lote), 0) as total_costo_lotes FROM lotes_produccion")
    c_data = cur.fetchone()

    # Gastos operativos
    cur.execute("SELECT COALESCE(SUM(monto), 0) as total_gastos FROM gastos_operativos")
    g_data = cur.fetchone()

    cur.execute("SELECT * FROM gastos_operativos ORDER BY fecha DESC")
    gastos_list = cur.fetchall()

    conn.close()

    total_ingresos = v_data["total_ventas"]
    costo_produccion = c_data["total_costo_lotes"]
    gastos_operativos = g_data["total_gastos"]
    utilidad_bruta = total_ingresos - costo_produccion
    utilidad_neta = total_ingresos - costo_produccion - gastos_operativos
    margen_neto_pct = (utilidad_neta / total_ingresos * 100) if total_ingresos > 0 else 0.0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Ingresos Ventas", f"${total_ingresos:,.2f}", f"{v_data['total_hogazas']} hogazas")
    kpi2.metric("Costo Producción (Materia Prima)", f"${costo_produccion:,.2f}")
    kpi3.metric("Gastos Operativos (Gas, Alquiler)", f"${gastos_operativos:,.2f}")
    kpi4.metric("Utilidad Neta Estimada", f"${utilidad_neta:,.2f}", f"{margen_neto_pct:.1f}% margen neto")

    st.markdown("---")
    col_fin1, col_fin2 = st.columns(2)

    with col_fin1:
        st.markdown("### 💸 Registrar Gasto Operativo")
        with st.form("form_gasto"):
            g_concepto = st.text_input("Concepto (ej: Pago de luz, cilindro de gas, empaques extra):")
            g_cat = st.selectbox("Categoría:", ["Energia/Gas", "Alquiler", "Empaque", "Transporte", "Herramientas/Mantenimiento", "Otros"])
            g_monto = st.number_input("Monto ($):", min_value=0.5, value=25.0, step=5.0)
            g_fecha = st.date_input("Fecha:", value=date.today())

            submit_gasto = st.form_submit_button("Registrar Gasto")
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
        st.markdown("### 📋 Historial de Gastos Operativos")
        if gastos_list:
            df_g = pd.DataFrame([dict(g) for g in gastos_list])
            st.dataframe(df_g[["fecha", "concepto", "categoria", "monto"]].rename(
                columns={"fecha": "Fecha", "concepto": "Concepto", "categoria": "Categoría", "monto": "Monto ($)"}
            ).style.format({"Monto ($)": "${:.2f}"}), use_container_width=True)
        else:
            st.info("No hay gastos operativos registrados.")
