import sqlite3
import os
from datetime import datetime, date, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "palveti.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Ingredientes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ingredientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        categoria TEXT NOT NULL,
        unidad_medida TEXT NOT NULL,
        stock_actual REAL NOT NULL DEFAULT 0,
        stock_minimo REAL NOT NULL DEFAULT 0,
        costo_unitario REAL NOT NULL DEFAULT 0 -- Costo en COP por gramo o por unidad
    )
    """)

    # 2. Movimientos de inventario
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimientos_inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ingrediente_id INTEGER NOT NULL,
        tipo_movimiento TEXT NOT NULL,
        cantidad REAL NOT NULL,
        referencia TEXT,
        fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ingrediente_id) REFERENCES ingredientes(id)
    )
    """)

    # 3. Recetas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recetas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        peso_unitario_crudo REAL NOT NULL DEFAULT 850,
        peso_unitario_horneado REAL NOT NULL DEFAULT 750,
        precio_venta_sugerido REAL NOT NULL DEFAULT 0, -- en COP
        tiempo_horneado_minutos INTEGER DEFAULT 35,
        temperatura_horno_c INTEGER DEFAULT 230
    )
    """)

    # 4. Detalle de ingredientes de recetas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receta_ingredientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receta_id INTEGER NOT NULL,
        ingrediente_id INTEGER NOT NULL,
        es_harina_base INTEGER NOT NULL DEFAULT 0,
        porcentaje_panadero REAL NOT NULL,
        cantidad_fija_por_unidad REAL DEFAULT 0,
        FOREIGN KEY (receta_id) REFERENCES recetas(id),
        FOREIGN KEY (ingrediente_id) REFERENCES ingredientes(id)
    )
    """)

    # 5. Lotes de producción
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lotes_produccion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_lote TEXT NOT NULL UNIQUE,
        receta_id INTEGER NOT NULL,
        unidades_programadas INTEGER NOT NULL,
        peso_hogaza_g REAL NOT NULL,
        unidades_reales INTEGER DEFAULT 0,
        fecha_amasado DATE NOT NULL,
        fecha_horneado DATE NOT NULL,
        estado TEXT NOT NULL DEFAULT 'PLANIFICADO',
        inventario_descontado INTEGER NOT NULL DEFAULT 0,
        costo_total_lote REAL DEFAULT 0,
        FOREIGN KEY (receta_id) REFERENCES recetas(id)
    )
    """)

    # 6. Bitácora de fermentación y calidad
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bitacora_fermentacion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lote_id INTEGER NOT NULL UNIQUE,
        temp_ambiente_amasado_c REAL,
        temp_final_masa_c REAL,
        duracion_autolisis_min INTEGER DEFAULT 0,
        tiempo_bloque_horas REAL,
        pliegues_realizados INTEGER DEFAULT 3,
        tiempo_retardo_frio_horas REAL,
        temp_nevera_c REAL DEFAULT 4.0,
        evaluacion_calidad INTEGER DEFAULT 5,
        observaciones_calidad TEXT,
        FOREIGN KEY (lote_id) REFERENCES lotes_produccion(id)
    )
    """)

    # 7. Clientes (con tipo_cliente: Minorista / Mayorista)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT,
        direccion TEXT,
        preferencias TEXT,
        tipo_cliente TEXT NOT NULL DEFAULT 'Minorista'
    )
    """)

    # 8. Pedidos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        lote_id INTEGER,
        receta_id INTEGER NOT NULL,
        unidades INTEGER NOT NULL DEFAULT 1,
        fecha_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
        fecha_entrega DATE NOT NULL,
        estado TEXT NOT NULL DEFAULT 'REGISTRADO',
        total_cobrado REAL NOT NULL, -- en COP
        metodo_pago TEXT DEFAULT 'Efectivo',
        notas TEXT,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
        FOREIGN KEY (lote_id) REFERENCES lotes_produccion(id),
        FOREIGN KEY (receta_id) REFERENCES recetas(id)
    )
    """)

    # 9. Gastos operativos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gastos_operativos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        concepto TEXT NOT NULL,
        categoria TEXT NOT NULL,
        monto REAL NOT NULL, -- en COP
        fecha DATE NOT NULL
    )
    """)

    # 10. Mantenimiento de Equipos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mantenimiento_equipos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipo TEXT NOT NULL,
        tarea TEXT NOT NULL,
        frecuencia_dias INTEGER NOT NULL DEFAULT 30,
        ultima_fecha DATE NOT NULL,
        proxima_fecha DATE NOT NULL,
        estado TEXT NOT NULL DEFAULT 'AL DÍA', -- AL DÍA, PRÓXIMO, VENCIDO
        responsable TEXT DEFAULT 'Panadero Jefe',
        notas TEXT
    )
    """)

    # 11. Calendario de Actividades Operativas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS calendario_actividades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha DATE NOT NULL,
        tipo_actividad TEXT NOT NULL, -- Compra de Insumos, Apertura Preventa, Cierre Pedidos, Amasado, Horneado, Mantenimiento, Entrega
        titulo TEXT NOT NULL,
        descripcion TEXT,
        completada INTEGER NOT NULL DEFAULT 0
    )
    """)

    conn.commit()

    # Migrar base de datos si ya existe para asegurar compatibilidad y COP
    migrate_to_cop(conn)
    seed_initial_data(conn)
    conn.close()

def migrate_to_cop(conn):
    """
    Asegura que la columna tipo_cliente exista y convierte precios antiguos a COP.
    """
    cursor = conn.cursor()

    # Verificar si existe columna tipo_cliente en clientes
    cursor.execute("PRAGMA table_info(clientes)")
    columnas_clientes = [col[1] for col in cursor.fetchall()]
    if "tipo_cliente" not in columnas_clientes:
        cursor.execute("ALTER TABLE clientes ADD COLUMN tipo_cliente TEXT NOT NULL DEFAULT 'Minorista'")

    # Verificar si los precios de insumos están en dólares (< 100) y migrarlos a COP
    cursor.execute("SELECT MAX(costo_unitario) FROM ingredientes")
    row = cursor.fetchone()
    max_costo = row[0] if row and row[0] is not None else 0

    if max_costo > 0 and max_costo < 50:
        # Migrar Insumos a COP realistas
        costos_cop = {
            "Harina de Fuerza 13% Proteína": 4.5, # $4.500 / kg -> $4.5 por gramo
            "Harina Integral de Centeno": 7.2,    # $7.200 / kg -> $7.2 por gramo
            "Agua Filtrada": 0.05,
            "Masa Madre Activa 100% Hidratación": 5.0, # $5.000 / kg -> $5.0 por gramo
            "Sal Marina Fina": 2.5,               # $2.500 / kg -> $2.5 por gramo
            "Semillas Mixtas (Sésamo, Chía, Girasol)": 22.0, # $22.000 / kg -> $22.0 por gramo
            "Aceite de Oliva Extra Virgen": 45.0, # $45.000 / litro -> $45.0 por gramo
            "Bolsa de Papel Kraft PALVETI": 1200.0 # $1.200 por unidad
        }
        for nombre, costo in costos_cop.items():
            cursor.execute("UPDATE ingredientes SET costo_unitario = ? WHERE nombre = ?", (costo, nombre))

        # Migrar Recetas a precios COP
        cursor.execute("UPDATE recetas SET precio_venta_sugerido = 22000 WHERE id = 1")
        cursor.execute("UPDATE recetas SET precio_venta_sugerido = 26000 WHERE id = 2")
        cursor.execute("UPDATE recetas SET precio_venta_sugerido = 28000 WHERE id = 3")

        # Migrar Pedidos existentes a COP
        cursor.execute("UPDATE pedidos SET total_cobrado = total_cobrado * 4000 WHERE total_cobrado < 500")

        # Migrar Gastos existentes a COP
        cursor.execute("UPDATE gastos_operativos SET monto = monto * 3000 WHERE monto < 500")

        # Migrar Lotes a COP
        cursor.execute("UPDATE lotes_produccion SET costo_total_lote = costo_total_lote * 4000 WHERE costo_total_lote < 500")

        # Actualizar clientes existentes
        cursor.execute("UPDATE clientes SET tipo_cliente = 'Mayorista' WHERE nombre LIKE '%Bistro%' OR nombre LIKE '%Café%'")

    # Normalizar costos de materias primas a COP realistas si están desfasados o en bulto entero
    costos_estandar = {
        "Harina de Fuerza 13% Proteína": 4.5,     # $4.500 / kg -> $4.5 por gramo
        "Harina Integral de Centeno": 7.2,        # $7.200 / kg -> $7.2 por gramo
        "Agua Filtrada": 0.05,                   # $0.05 por gramo ($50 por litro)
        "Masa Madre Activa 100% Hidratación": 5.0,# $5.000 / kg -> $5.0 por gramo
        "Sal Marina Fina": 2.5,                   # $2.500 / kg -> $2.5 por gramo
        "Semillas Mixtas (Sésamo, Chía, Girasol)": 22.0, # $22.000 / kg -> $22.0 por gramo
        "Aceite de Oliva Extra Virgen": 45.0,     # $45.000 / litro -> $45.0 por gramo
        "Bolsa de Papel Kraft PALVETI": 1200.0,   # $1.200 por unidad
        " dátiles": 25.0,                        # $25.000 / kg -> $25.0 por gramo
        "Dátiles": 25.0
    }
    for nombre_insumo, c_est in costos_estandar.items():
        cursor.execute("""
        UPDATE ingredientes 
        SET costo_unitario = ? 
        WHERE (nombre = ? OR nombre LIKE ?) AND (costo_unitario < 0.1 OR costo_unitario > 500 OR costo_unitario = 0.28)
        """, (c_est, nombre_insumo, f"%{nombre_insumo.strip()}%"))

    # Garantizar insumos de empaque y energéticos adicionales
    cursor.execute("SELECT id FROM ingredientes WHERE nombre LIKE '%Etiqueta%'")
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO ingredientes (nombre, categoria, unidad_medida, stock_actual, stock_minimo, costo_unitario)
        VALUES ('Etiqueta Adhesiva PALVETI', 'empaque', 'unidad', 500, 100, 350.0)
        """)

    cursor.execute("SELECT id FROM ingredientes WHERE nombre LIKE '%Gas%' OR nombre LIKE '%Energía%'")
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO ingredientes (nombre, categoria, unidad_medida, stock_actual, stock_minimo, costo_unitario)
        VALUES ('Gas / Energía Proporcional (por hogaza)', 'servicio', 'unidad', 9999, 50, 1500.0)
        """)

    # Vincular ingredientes a Receta 3 (Focaccia) si no los tiene
    cursor.execute("SELECT count(*) FROM receta_ingredientes WHERE receta_id = 3")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT id, nombre FROM ingredientes")
        ing_dict = {r["nombre"]: r["id"] for r in cursor.fetchall()}
        focaccia_ings = [
            (3, ing_dict.get("Harina de Fuerza 13% Proteína", 1), 1, 100.0, 0),
            (3, ing_dict.get("Agua Filtrada", 3), 0, 80.0, 0),
            (3, ing_dict.get("Masa Madre Activa 100% Hidratación", 4), 0, 20.0, 0),
            (3, ing_dict.get("Sal Marina Fina", 5), 0, 2.5, 0),
            (3, ing_dict.get("Aceite de Oliva Extra Virgen", 7), 0, 8.0, 0),
            (3, ing_dict.get("Bolsa de Papel Kraft PALVETI", 8), 0, 0, 1.0)
        ]
        cursor.executemany("""
        INSERT INTO receta_ingredientes (receta_id, ingrediente_id, es_harina_base, porcentaje_panadero, cantidad_fija_por_unidad)
        VALUES (?, ?, ?, ?, ?)
        """, focaccia_ings)

    conn.commit()

def update_ingredient_cost(ingrediente_id, nuevo_costo_unitario):
    """Actualiza el costo unitario de compra de un ingrediente en la base de datos."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE ingredientes SET costo_unitario = ? WHERE id = ?", (float(nuevo_costo_unitario), int(ingrediente_id)))
    conn.commit()
    conn.close()
    return True

def seed_initial_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ingredientes")
    if cursor.fetchone()[0] == 0:
        # Insumos en Pesos Colombianos (COP)
        # Gramos: costo_unitario = precio por gramo
        # Unidades: costo_unitario = precio por unidad
        ingredientes = [
            ("Harina de Fuerza 13% Proteína", "harina", "g", 50000, 15000, 4.5), # $4.500 COP/kg
            ("Harina Integral de Centeno", "harina", "g", 20000, 5000, 7.2),    # $7.200 COP/kg
            ("Agua Filtrada", "liquido", "g", 100000, 10000, 0.05),             # $50 COP/litro
            ("Masa Madre Activa 100% Hidratación", "fermento", "g", 12000, 3000, 5.0), # $5.000 COP/kg
            ("Sal Marina Fina", "aditivo", "g", 10000, 2000, 2.5),              # $2.500 COP/kg
            ("Semillas Mixtas (Sésamo, Chía, Girasol)", "aditivo", "g", 6000, 2000, 22.0), # $22.000 COP/kg
            ("Aceite de Oliva Extra Virgen", "liquido", "g", 4000, 1000, 45.0), # $45.000 COP/litro
            ("Bolsa de Papel Kraft PALVETI", "empaque", "unidad", 150, 40, 1200.0) # $1.200 COP c/u
        ]
        cursor.executemany("""
        INSERT INTO ingredientes (nombre, categoria, unidad_medida, stock_actual, stock_minimo, costo_unitario)
        VALUES (?, ?, ?, ?, ?, ?)
        """, ingredientes)

        # Recetas estándar en COP
        cursor.execute("""
        INSERT INTO recetas (nombre, descripcion, peso_unitario_crudo, peso_unitario_horneado, precio_venta_sugerido, tiempo_horneado_minutos, temperatura_horno_c)
        VALUES 
        ('Hogaza Campesina Clásica', 'Pan de masa madre tradicional con 75% de hidratación y corteza crujiente.', 850, 750, 22000, 38, 230),
        ('Hogaza Multicereales & Centeno', 'Hogaza rústica con 20% centeno integral y mezcla de semillas tostadas.', 900, 800, 26000, 40, 225),
        ('Focaccia Artesanal al Romero', 'Focaccia esponjosa de alta hidratación con aceite de oliva extra virgen y romero.', 950, 880, 28000, 28, 220)
        """)

        cursor.execute("SELECT id, nombre FROM ingredientes")
        ing_map = {row["nombre"]: row["id"] for row in cursor.fetchall()}

        # Receta 1
        cursor.executemany("""
        INSERT INTO receta_ingredientes (receta_id, ingrediente_id, es_harina_base, porcentaje_panadero, cantidad_fija_por_unidad)
        VALUES (?, ?, ?, ?, ?)
        """, [
            (1, ing_map["Harina de Fuerza 13% Proteína"], 1, 100.0, 0),
            (1, ing_map["Agua Filtrada"], 0, 75.0, 0),
            (1, ing_map["Masa Madre Activa 100% Hidratación"], 0, 20.0, 0),
            (1, ing_map["Sal Marina Fina"], 0, 2.0, 0),
            (1, ing_map["Bolsa de Papel Kraft PALVETI"], 0, 0, 1.0)
        ])

        # Receta 2
        cursor.executemany("""
        INSERT INTO receta_ingredientes (receta_id, ingrediente_id, es_harina_base, porcentaje_panadero, cantidad_fija_por_unidad)
        VALUES (?, ?, ?, ?, ?)
        """, [
            (2, ing_map["Harina de Fuerza 13% Proteína"], 1, 80.0, 0),
            (2, ing_map["Harina Integral de Centeno"], 1, 20.0, 0),
            (2, ing_map["Agua Filtrada"], 0, 78.0, 0),
            (2, ing_map["Masa Madre Activa 100% Hidratación"], 0, 20.0, 0),
            (2, ing_map["Sal Marina Fina"], 0, 2.1, 0),
            (2, ing_map["Semillas Mixtas (Sésamo, Chía, Girasol)"], 0, 15.0, 0),
            (2, ing_map["Bolsa de Papel Kraft PALVETI"], 0, 0, 1.0)
        ])

        # Clientes
        cursor.executemany("""
        INSERT INTO clientes (nombre, telefono, direccion, preferencias, tipo_cliente)
        VALUES (?, ?, ?, ?, ?)
        """, [
            ("Sofía Mendoza", "+57 300 123 4567", "Calle 10 # 43-22", "Corteza bien dorada, entrega en la mañana", "Minorista"),
            ("Carlos Restrepo", "+57 311 987 6543", "Carrera 25 # 12-40", "Fanático del pan con semillas, pide cada semana", "Minorista"),
            ("Café & Arte Bistro", "+57 320 555 8899", "Avenida Jardín # 8-15", "Hogazas rebanadas para tostadas artesanales (15 unidades/semana)", "Mayorista"),
            ("Restaurante La Cava Rústica", "+57 315 444 1122", "Zona Rosa Cl 8 # 32-10", "Focaccias y hogazas rústicas para servicio de mesa", "Mayorista")
        ])

        # Lote de producción
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
        INSERT INTO lotes_produccion (codigo_lote, receta_id, unidades_programadas, peso_hogaza_g, unidades_reales, fecha_amasado, fecha_horneado, estado, inventario_descontado, costo_total_lote)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (f"LOTE-{today}-VIE-01", 1, 16, 850, 16, today, today, "EN_FERMENTACION", 1, 72000.0))
        lote_id = cursor.lastrowid

        # Bitácora
        cursor.execute("""
        INSERT INTO bitacora_fermentacion (lote_id, temp_ambiente_amasado_c, temp_final_masa_c, duracion_autolisis_min, tiempo_bloque_horas, pliegues_realizados, tiempo_retardo_frio_horas, temp_nevera_c, evaluacion_calidad, observaciones_calidad)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (lote_id, 23.5, 25.0, 45, 4.5, 4, 16.0, 4.0, 5, "Excelente desarrollo de gluten. Salto de horno previsto alto."))

        # Pedidos
        cursor.executemany("""
        INSERT INTO pedidos (cliente_id, lote_id, receta_id, unidades, fecha_entrega, estado, total_cobrado, metodo_pago, notas)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            (1, lote_id, 1, 2, today, "EN_FERMENTACION", 44000.0, "Transferencia", "Entregar antes de las 11 AM"),
            (2, lote_id, 1, 1, today, "PAGADO", 22000.0, "Efectivo", "Pasa a recoger al taller"),
            (3, lote_id, 1, 6, today, "REGISTRADO", 120000.0, "Transferencia", "Pedido mayorista bistró semanal")
        ])

        # Gastos operativos
        cursor.executemany("""
        INSERT INTO gastos_operativos (concepto, categoria, monto, fecha)
        VALUES (?, ?, ?, ?)
        """, [
            ("Cilindro de Gas para Horno", "Energia/Gas", 115000.0, today),
            ("Papel sulfurizado para bandejas (pack)", "Empaque", 38000.0, today)
        ])

    # Verificar si tabla de mantenimiento está vacía y sembrar datos de ejemplo
    cursor.execute("SELECT COUNT(*) FROM mantenimiento_equipos")
    if cursor.fetchone()[0] == 0:
        hoy = date.today()
        equipos_base = [
            ("Horno de Solera Refractario", "Limpieza de piedras refractarias y revisión de termocupla", 15, (hoy - timedelta(days=10)).strftime("%Y-%m-%d"), (hoy + timedelta(days=5)).strftime("%Y-%m-%d"), "AL DÍA", "Panadero Jefe", "No usar agua sobre la piedra caliente"),
            ("Amasadora de Espiral", "Lubricación de cadena motriz y revisión de correa", 30, (hoy - timedelta(days=28)).strftime("%Y-%m-%d"), (hoy + timedelta(days=2)).strftime("%Y-%m-%d"), "PRÓXIMO", "Técnico Mantenimiento", "Revisar tensión de correa"),
            ("Nevera de Fermentación / Retardo", "Limpieza de condensador, filtro y calibración de termostato", 30, (hoy - timedelta(days=35)).strftime("%Y-%m-%d"), (hoy - timedelta(days=5)).strftime("%Y-%m-%d"), "VENCIDO", "Panadero Jefe", "Temperatura objetivo: 4°C estables"),
            ("Bannetons de Caña y Telas de Lino", "Secado al horno suave y cepillado profundo de exceso de harina", 7, (hoy - timedelta(days=4)).strftime("%Y-%m-%d"), (hoy + timedelta(days=3)).strftime("%Y-%m-%d"), "AL DÍA", "Equipo Obrador", "Evitar humedad para prevenir hongos"),
            ("Filtro de Agua de 3 Etapas", "Cambio de cartucho de sedimentos y carbón activado", 90, (hoy - timedelta(days=70)).strftime("%Y-%m-%d"), (hoy + timedelta(days=20)).strftime("%Y-%m-%d"), "AL DÍA", "Proveedor Purificadores", "Esencial para el cloro en masa madre")
        ]
        cursor.executemany("""
        INSERT INTO mantenimiento_equipos (equipo, tarea, frecuencia_dias, ultima_fecha, proxima_fecha, estado, responsable, notas)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, equipos_base)

    # Verificar si tabla de actividades está vacía y sembrar datos de ejemplo
    cursor.execute("SELECT COUNT(*) FROM calendario_actividades")
    if cursor.fetchone()[0] == 0:
        hoy = date.today()
        # Generar ciclo semanal típico de panadería artesanal
        lunes = hoy - timedelta(days=hoy.weekday())
        actividades_base = [
            ((lunes).strftime("%Y-%m-%d"), "🛒 Compra de Insumos", "Comprar Harinas y Semillas en Molino", "Abastecer harina de fuerza, centeno y papel kraft para la semana", 1),
            ((lunes + timedelta(days=1)).strftime("%Y-%m-%d"), "📢 Apertura de Preventa", "Abrir Catálogo y Pedidos por WhatsApp/Instagram", "Publicar menú de horneado para el viernes y sábado", 1),
            ((lunes + timedelta(days=2)).strftime("%Y-%m-%d"), "🌾 Refresco de Masa Madre Madre", "Alimentar fermentos para producción masiva", "Pase de masa madre 1:2:2 para arrancar prefermento", 0),
            ((lunes + timedelta(days=3)).strftime("%Y-%m-%d"), "🔒 Cierre de Pedidos", "Cierre de Preventa a las 8:00 PM", "Consolidar lista de producción y pesaje de harina", 0),
            ((lunes + timedelta(days=3)).strftime("%Y-%m-%d"), "🥣 Amasado y Formado", "Amasado, Autólisis, Bloque y Formado a Banneton", "Pasar hogazas formadas a retardo en frío 16 horas", 0),
            ((lunes + timedelta(days=4)).strftime("%Y-%m-%d"), "🔥 Día de Horneado", "Horneado Lote Viernes desde las 5:00 AM", "Calentar horno a 240°C, greñado con navaja y vapor inicial", 0),
            ((lunes + timedelta(days=4)).strftime("%Y-%m-%d"), "📦 Entrega de Pedidos", "Despacho y Entrega de Hogazas", "Reparto a restaurantes y entregas a clientes particulares", 0),
            ((lunes + timedelta(days=5)).strftime("%Y-%m-%d"), "🧹 Mantenimiento y Limpieza", "Limpieza profunda de obrador y mantenimiento", "Limpieza de mesas de acero, bannetons y hornos", 0)
        ]
        cursor.executemany("""
        INSERT INTO calendario_actividades (fecha, tipo_actividad, titulo, descripcion, completada)
        VALUES (?, ?, ?, ?, ?)
        """, actividades_base)

    conn.commit()

if __name__ == "__main__":
    init_db()
    print("Base de datos PALVETI configurada y migrada en Pesos Colombianos (COP).")
