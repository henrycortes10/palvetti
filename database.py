import sqlite3
import os
from datetime import datetime

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
        categoria TEXT NOT NULL, -- harina, liquido, fermento, aditivo, empaque
        unidad_medida TEXT NOT NULL, -- g, kg, unidad, ml
        stock_actual REAL NOT NULL DEFAULT 0,
        stock_minimo REAL NOT NULL DEFAULT 0,
        costo_unitario REAL NOT NULL DEFAULT 0 -- costo por gramo o por unidad
    )
    """)

    # 2. Movimientos de inventario
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimientos_inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ingrediente_id INTEGER NOT NULL,
        tipo_movimiento TEXT NOT NULL, -- ENTRADA_COMPRA, SALIDA_PRODUCCION, AJUSTE_MERMA
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
        peso_unitario_crudo REAL NOT NULL DEFAULT 850, -- gramos
        peso_unitario_horneado REAL NOT NULL DEFAULT 750, -- gramos
        precio_venta_sugerido REAL NOT NULL DEFAULT 0,
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
        es_harina_base INTEGER NOT NULL DEFAULT 0, -- 1 si forma parte del 100% de harina
        porcentaje_panadero REAL NOT NULL, -- % respecto a harina base total
        cantidad_fija_por_unidad REAL DEFAULT 0, -- para empaques u otros por hogaza
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
        estado TEXT NOT NULL DEFAULT 'PLANIFICADO', -- PLANIFICADO, EN_FERMENTACION, HORNEADO, FINALIZADO
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
        evaluacion_calidad INTEGER DEFAULT 5, -- 1 a 5 estrellas
        observaciones_calidad TEXT,
        FOREIGN KEY (lote_id) REFERENCES lotes_produccion(id)
    )
    """)

    # 7. Clientes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT,
        direccion TEXT,
        preferencias TEXT
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
        estado TEXT NOT NULL DEFAULT 'REGISTRADO', -- REGISTRADO, PAGADO, EN_FERMENTACION, HORNEADO, ENTREGADO
        total_cobrado REAL NOT NULL,
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
        categoria TEXT NOT NULL, -- Energia/Gas, Alquiler, Empaque, Transporte, Otros
        monto REAL NOT NULL,
        fecha DATE NOT NULL
    )
    """)

    conn.commit()
    seed_initial_data(conn)
    conn.close()

def seed_initial_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ingredientes")
    if cursor.fetchone()[0] > 0:
        return # Ya contiene datos iniciales

    # Insertar Insumos con costos aproximados (costo_unitario por gramo o por unidad)
    ingredientes = [
        ("Harina de Fuerza 13% Proteína", "harina", "g", 40000, 15000, 0.0013), # $1.30/kg
        ("Harina Integral de Centeno", "harina", "g", 15000, 5000, 0.0019),    # $1.90/kg
        ("Agua Filtrada", "liquido", "g", 100000, 10000, 0.0001),              # Casi despreciable
        ("Masa Madre Activa 100% Hidratación", "fermento", "g", 10000, 3000, 0.0015), # $1.50/kg
        ("Sal Marina Fina", "aditivo", "g", 8000, 2000, 0.0009),               # $0.90/kg
        ("Semillas Mixtas (Sésamo, Chía, Girasol)", "aditivo", "g", 4500, 2000, 0.0055), # $5.50/kg
        ("Aceite de Oliva Extra Virgen", "liquido", "g", 3000, 1000, 0.0090),  # $9.00/kg
        ("Bolsa de Papel Kraft PALVETI", "empaque", "unidad", 120, 40, 0.28)   # $0.28 c/u
    ]
    cursor.executemany("""
    INSERT INTO ingredientes (nombre, categoria, unidad_medida, stock_actual, stock_minimo, costo_unitario)
    VALUES (?, ?, ?, ?, ?, ?)
    """, ingredientes)

    # Insertar Recetas
    cursor.execute("""
    INSERT INTO recetas (nombre, descripcion, peso_unitario_crudo, peso_unitario_horneado, precio_venta_sugerido, tiempo_horneado_minutos, temperatura_horno_c)
    VALUES 
    ('Hogaza Campesina Clásica', 'Pan de masa madre tradicional con 75% de hidratación y corteza crujiente.', 850, 750, 5.50, 38, 230),
    ('Hogaza Multicereales & Centeno', 'Hogaza rústica con 20% centeno integral y mezcla de semillas tostadas.', 900, 800, 6.50, 40, 225),
    ('Focaccia Artesanal al Romero', 'Focaccia esponjosa de alta hidratación con aceite de oliva extra virgen y romero.', 950, 880, 7.00, 28, 220)
    """)

    # Obtener IDs de ingredientes
    cursor.execute("SELECT id, nombre FROM ingredientes")
    ing_map = {row["nombre"]: row["id"] for row in cursor.fetchall()}

    # Receta 1: Hogaza Campesina Clásica (Total Harina = 100%, Agua=75%, MM=20%, Sal=2%)
    receta1_id = 1
    cursor.executemany("""
    INSERT INTO receta_ingredientes (receta_id, ingrediente_id, es_harina_base, porcentaje_panadero, cantidad_fija_por_unidad)
    VALUES (?, ?, ?, ?, ?)
    """, [
        (receta1_id, ing_map["Harina de Fuerza 13% Proteína"], 1, 100.0, 0),
        (receta1_id, ing_map["Agua Filtrada"], 0, 75.0, 0),
        (receta1_id, ing_map["Masa Madre Activa 100% Hidratación"], 0, 20.0, 0),
        (receta1_id, ing_map["Sal Marina Fina"], 0, 2.0, 0),
        (receta1_id, ing_map["Bolsa de Papel Kraft PALVETI"], 0, 0, 1.0)
    ])

    # Receta 2: Hogaza Multicereales & Centeno (Fuerza 80%, Centeno 20% = 100% harina base; Agua 78%, MM 20%, Sal 2.1%, Semillas 15%)
    receta2_id = 2
    cursor.executemany("""
    INSERT INTO receta_ingredientes (receta_id, ingrediente_id, es_harina_base, porcentaje_panadero, cantidad_fija_por_unidad)
    VALUES (?, ?, ?, ?, ?)
    """, [
        (receta2_id, ing_map["Harina de Fuerza 13% Proteína"], 1, 80.0, 0),
        (receta2_id, ing_map["Harina Integral de Centeno"], 1, 20.0, 0),
        (receta2_id, ing_map["Agua Filtrada"], 0, 78.0, 0),
        (receta2_id, ing_map["Masa Madre Activa 100% Hidratación"], 0, 20.0, 0),
        (receta2_id, ing_map["Sal Marina Fina"], 0, 2.1, 0),
        (receta2_id, ing_map["Semillas Mixtas (Sésamo, Chía, Girasol)"], 0, 15.0, 0),
        (receta2_id, ing_map["Bolsa de Papel Kraft PALVETI"], 0, 0, 1.0)
    ])

    # Clientes de ejemplo
    cursor.executemany("""
    INSERT INTO clientes (nombre, telefono, direccion, preferencias)
    VALUES (?, ?, ?, ?)
    """, [
        ("Sofía Mendoza", "+57 300 123 4567", "Calle 10 # 43-22", "Corteza bien dorada, entrega en la mañana"),
        ("Carlos Restrepo", "+57 311 987 6543", "Carrera 25 # 12-40", "Fanático del pan con semillas, pide 2 hogazas cada viernes"),
        ("Café & Arte Bistro", "+57 320 555 8899", "Avenida Jardín # 8-15", "Hogazas rebanadas para tostadas artesanales")
    ])

    # Lote de producción inicial
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
    INSERT INTO lotes_produccion (codigo_lote, receta_id, unidades_programadas, peso_hogaza_g, unidades_reales, fecha_amasado, fecha_horneado, estado, inventario_descontado, costo_total_lote)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (f"LOTE-{today}-VIE-01", 1, 16, 850, 16, today, today, "EN_FERMENTACION", 1, 18.24))
    lote_id = cursor.lastrowid

    # Bitácora de fermentación inicial
    cursor.execute("""
    INSERT INTO bitacora_fermentacion (lote_id, temp_ambiente_amasado_c, temp_final_masa_c, duracion_autolisis_min, tiempo_bloque_horas, pliegues_realizados, tiempo_retardo_frio_horas, temp_nevera_c, evaluacion_calidad, observaciones_calidad)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (lote_id, 23.5, 25.2, 45, 4.5, 4, 16.0, 4.0, 5, "Excelente desarrollo de gluten. Salto de horno previsto alto."))

    # Pedidos de ejemplo
    cursor.executemany("""
    INSERT INTO pedidos (cliente_id, lote_id, receta_id, unidades, fecha_entrega, estado, total_cobrado, metodo_pago, notas)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        (1, lote_id, 1, 2, today, "EN_FERMENTACION", 11.00, "Transferencia", "Entregar antes de las 11 AM"),
        (2, lote_id, 1, 1, today, "PAGADO", 5.50, "Efectivo", "Pasa a recoger al taller"),
        (3, lote_id, 1, 6, today, "REGISTRADO", 33.00, "Transferencia", "Pedido regular bistró")
    ])

    # Gastos operativos iniciales
    cursor.executemany("""
    INSERT INTO gastos_operativos (concepto, categoria, monto, fecha)
    VALUES (?, ?, ?, ?)
    """, [
        ("Cilindro de Gas para Horno", "Energia/Gas", 45.00, today),
        ("Papel sulfurizado para bandejas (pack)", "Empaque", 12.50, today)
    ])

    conn.commit()

if __name__ == "__main__":
    init_db()
    print("Base de datos inicializada correctamente.")
