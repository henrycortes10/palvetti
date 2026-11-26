from datetime import datetime, date, timedelta
from database import get_connection

def format_cop(valor):
    """Formatea un número a Pesos Colombianos, ej: $ 25.000 COP"""
    if valor is None:
        return "$ 0 COP"
    try:
        val_int = int(round(float(valor)))
        return f"$ {val_int:,}".replace(",", ".") + " COP"
    except (ValueError, TypeError):
        return f"$ {valor} COP"

def get_recipe_details(receta_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.*, 
               ri.ingrediente_id, ri.es_harina_base, ri.porcentaje_panadero, ri.cantidad_fija_por_unidad,
               i.nombre as ingrediente_nombre, i.categoria, i.unidad_medida, i.costo_unitario, i.stock_actual, i.stock_minimo
        FROM recetas r
        JOIN receta_ingredientes ri ON r.id = ri.receta_id
        JOIN ingredientes i ON ri.ingrediente_id = i.id
        WHERE r.id = ?
        ORDER BY ri.es_harina_base DESC, ri.porcentaje_panadero DESC
    """, (receta_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def calculate_production_batch(receta_id, unidades, peso_por_hogaza_g):
    """
    Calcula los gramos exactos de cada ingrediente para N hogazas usando Porcentaje de Panadero.
    También computa el costo exacto de producción por lote y por hogaza en COP.
    """
    rows = get_recipe_details(receta_id)
    if not rows:
        return None

    total_masa_requerida_g = unidades * peso_por_hogaza_g

    # 1. Suma de porcentajes de panadero de la masa (excluyendo empaques o no-masa)
    suma_porcentajes_masa = 0.0
    harina_base_porcentaje_total = 0.0

    for r in rows:
        if r["porcentaje_panadero"] > 0:
            suma_porcentajes_masa += r["porcentaje_panadero"]
        if r["es_harina_base"] == 1:
            harina_base_porcentaje_total += r["porcentaje_panadero"]

    if harina_base_porcentaje_total == 0:
        harina_base_porcentaje_total = 100.0

    # 2. Harina total base en gramos requerida
    harina_base_total_g = (total_masa_requerida_g / (suma_porcentajes_masa / 100.0))

    ingredientes_calculados = []
    costo_total_lote = 0.0
    agua_g = 0.0
    harina_g = 0.0

    for r in rows:
        if r["porcentaje_panadero"] > 0:
            # Ingrediente de masa
            gramos_totales = harina_base_total_g * (r["porcentaje_panadero"] / 100.0)
            costo_linea = gramos_totales * r["costo_unitario"]
            costo_total_lote += costo_linea
            
            if r["es_harina_base"] == 1:
                harina_g += gramos_totales
            if r["categoria"] == "liquido" and "agua" in r["ingrediente_nombre"].lower():
                agua_g += gramos_totales

            ingredientes_calculados.append({
                "ingrediente_id": r["ingrediente_id"],
                "nombre": r["ingrediente_nombre"],
                "categoria": r["categoria"],
                "unidad": "g",
                "es_harina_base": bool(r["es_harina_base"]),
                "porcentaje": r["porcentaje_panadero"],
                "gramos_por_hogaza": round(gramos_totales / unidades, 1),
                "gramos_lote": round(gramos_totales, 1),
                "costo_linea": round(costo_linea, 0),
                "stock_actual": r["stock_actual"],
                "stock_suficiente": r["stock_actual"] >= gramos_totales
            })
        elif r["cantidad_fija_por_unidad"] > 0:
            # Empaques o artículos unitarios
            cant_total = unidades * r["cantidad_fija_por_unidad"]
            costo_linea = cant_total * r["costo_unitario"]
            costo_total_lote += costo_linea

            ingredientes_calculados.append({
                "ingrediente_id": r["ingrediente_id"],
                "nombre": r["ingrediente_nombre"],
                "categoria": r["categoria"],
                "unidad": r["unidad_medida"],
                "es_harina_base": False,
                "porcentaje": 0.0,
                "gramos_por_hogaza": r["cantidad_fija_por_unidad"],
                "gramos_lote": cant_total,
                "costo_linea": round(costo_linea, 0),
                "stock_actual": r["stock_actual"],
                "stock_suficiente": r["stock_actual"] >= cant_total
            })

    costo_por_hogaza = costo_total_lote / unidades if unidades > 0 else 0
    hidratacion_calculada = (agua_g / harina_g * 100.0) if harina_g > 0 else 0.0

    return {
        "unidades": unidades,
        "peso_por_hogaza_g": peso_por_hogaza_g,
        "total_masa_requerida_g": round(total_masa_requerida_g, 1),
        "harina_base_total_g": round(harina_base_total_g, 1),
        "hidratacion_porcentaje": round(hidratacion_calculada, 1),
        "costo_total_lote": round(costo_total_lote, 0),
        "costo_por_hogaza": round(costo_por_hogaza, 0),
        "ingredientes": ingredientes_calculados
    }

def calculate_pricing(costo_unitario, tipo_margen, valor_margen):
    """
    Calcula el precio de venta sugerido y la ganancia por unidad en COP.
    """
    if costo_unitario <= 0:
        return {"precio_venta": 0.0, "ganancia": 0.0, "margen_real_pct": 0.0}

    if tipo_margen == "porcentual_margen":
        margen_frac = valor_margen / 100.0
        if margen_frac >= 1.0:
            margen_frac = 0.99
        precio = costo_unitario / (1.0 - margen_frac)
    elif tipo_margen == "porcentual_markup":
        precio = costo_unitario * (1.0 + (valor_margen / 100.0))
    else: # monto_fijo
        precio = costo_unitario + valor_margen

    ganancia = precio - costo_unitario
    margen_real_pct = (ganancia / precio * 100.0) if precio > 0 else 0.0

    return {
        "precio_venta": round(precio, -2), # Redondear a centenas de COP
        "ganancia_por_unidad": round(ganancia, -2),
        "margen_real_pct": round(margen_real_pct, 1)
    }

def discount_inventory_for_batch(lote_id):
    """
    Descuenta del inventario los insumos utilizados para un lote específico.
    Registra cada movimiento de salida en movimientos_inventario.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM lotes_produccion WHERE id = ?", (lote_id,))
    lote = cursor.fetchone()
    if not lote:
        conn.close()
        return False, "Lote no encontrado."

    if lote["inventario_descontado"] == 1:
        conn.close()
        return False, "El inventario de este lote ya fue descontado previamente."

    calc = calculate_production_batch(lote["receta_id"], lote["unidades_programadas"], lote["peso_hogaza_g"])
    if not calc:
        conn.close()
        return False, "No se pudieron calcular los ingredientes."

    for item in calc["ingredientes"]:
        cantidad_usada = item["gramos_lote"]
        cursor.execute("""
            UPDATE ingredientes 
            SET stock_actual = stock_actual - ?
            WHERE id = ?
        """, (cantidad_usada, item["ingrediente_id"]))

        cursor.execute("""
            INSERT INTO movimientos_inventario (ingrediente_id, tipo_movimiento, cantidad, referencia)
            VALUES (?, 'SALIDA_PRODUCCION', ?, ?)
        """, (item["ingrediente_id"], cantidad_usada, f"Lote #{lote['codigo_lote']} ({lote['unidades_programadas']} unidades)"))

    cursor.execute("""
        UPDATE lotes_produccion
        SET inventario_descontado = 1, costo_total_lote = ?
        WHERE id = ?
    """, (calc["costo_total_lote"], lote_id))

    conn.commit()
    conn.close()
    return True, f"Inventario descontado exitosamente para el lote {lote['codigo_lote']}."

def get_low_stock_alerts():
    """
    Retorna los ingredientes cuyo stock está en o por debajo del mínimo.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM ingredientes
        WHERE stock_actual <= stock_minimo
        ORDER BY (stock_actual / CASE WHEN stock_minimo = 0 THEN 1 ELSE stock_minimo END) ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_maintenance_tasks():
    """
    Retorna la lista de mantenimientos actualizando automáticamente el estado según la fecha.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mantenimiento_equipos ORDER BY proxima_fecha ASC")
    tasks = cursor.fetchall()
    
    hoy = date.today()
    updated_tasks = []
    
    for t in tasks:
        prox = datetime.strptime(t["proxima_fecha"], "%Y-%m-%d").date()
        dias_restantes = (prox - hoy).days
        
        nuevo_estado = "AL DÍA"
        if dias_restantes < 0:
            nuevo_estado = "VENCIDO"
        elif dias_restantes <= 7:
            nuevo_estado = "PRÓXIMO"
            
        if nuevo_estado != t["estado"]:
            cursor.execute("UPDATE mantenimiento_equipos SET estado = ? WHERE id = ?", (nuevo_estado, t["id"]))
            
        t_dict = dict(t)
        t_dict["estado"] = nuevo_estado
        t_dict["dias_restantes"] = dias_restantes
        updated_tasks.append(t_dict)
        
    conn.commit()
    conn.close()
    return updated_tasks

def complete_maintenance(task_id):
    """
    Marca un mantenimiento como realizado hoy y calcula la siguiente fecha según su frecuencia.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mantenimiento_equipos WHERE id = ?", (task_id,))
    t = cursor.fetchone()
    if not t:
        conn.close()
        return False
        
    hoy = date.today()
    prox = hoy + timedelta(days=t["frecuencia_dias"])
    
    cursor.execute("""
    UPDATE mantenimiento_equipos 
    SET ultima_fecha = ?, proxima_fecha = ?, estado = 'AL DÍA'
    WHERE id = ?
    """, (hoy.strftime("%Y-%m-%d"), prox.strftime("%Y-%m-%d"), task_id))
    
    conn.commit()
    conn.close()
    return True
