# 🌙 PALVETI - Historial de Modificaciones (Sesión Nocturna)

> **ID de Conversación:** `8238d46d-c430-466c-94e8-8a27a2ac6da7`  
> **Fecha:** 26 de Noviembre de 2026 (Horas de la noche)  
> **Repositorio GitHub:** `https://github.com/henrycortes10/palvetti.git` (rama `main`)  
> **URL Oficial en la Nube:** `https://palvetti-web.streamlit.app`  
> **URL Local:** `http://localhost:8501`

---

## 📌 ¿Cómo retomar esta sesión en Antigravity IDE?

Para continuar el desarrollo en cualquier PC o sesión futura, abre el proyecto y escribe:

```text
Por favor lee el archivo HISTORIAL_MODIFICACIONES_NOCHE.md y HISTORIAL_PROYECTO_PALVETI.md para entender todo el contexto reciente y continuemos desde aquí.
```

---

## 📝 Resumen Cronológico de Requerimientos y Modificaciones Realizadas

### 1. Despliegue en Streamlit Community Cloud
- **Problema inicial:** Al conectar con el dominio en Streamlit Cloud, el healthcheck fallaba con `dial tcp 127.0.0.1:8501: connect: connection refused` debido al prompt interactivo de bienvenida de Streamlit pidiendo email y a la falta de `requirements.txt`.
- **Acciones tomadas:**
  - Se creó [requirements.txt](file:///c:/Users/barbas/Desktop/Proyectos/palveti/requirements.txt) con `streamlit>=1.30.0` y `pandas>=2.0.0`.
  - Se configuró [.streamlit/config.toml](file:///c:/Users/barbas/Desktop/Proyectos/palveti/.streamlit/config.toml) con `headless = true` y `gatherUsageStats = false`.
  - Se sincronizó el repositorio y la app quedó desplegada y operativa al 100% en `https://palvetti-web.streamlit.app`.

### 2. Módulo Financiero de Costos y Cálculo Automático de Precios de Venta
- **Requerimiento:** Módulo de costos para gestionar la rentabilidad de cada producto de PALVETI.
- **Implementación:**
  - **Registro y Actualización de Costos de Compra:** En el Módulo 3 (*Inventario & Materia Prima*), se incorporó el actualizador rápido que permite ingresar precios por Kilo ($/kg), Bulto/Saco ($/saco) o por Unidad/Servicio (empaques, gas/energía).
  - **Cálculo Automático del Costo Unitario:** En el Módulo 2 (*Costos & Fijación de Precios*), se calcula dinámicamente el costo exacto por hogaza multiplicando los gramos/unidades por el costo unitario de cada insumo en inventario.
  - **Sugerencia de Precio de Venta:** Métodos de cálculo por Factor Multiplicador (ej: 3.0x), Margen % sobre Venta, Markup % sobre Costo y Ganancia Neta Fija.
  - **Simulador Interactivo de Precio Manual:** Permite ingresar un precio de venta fijo y arroja en tiempo real la ganancia neta en COP, margen real y semáforo visual de rentabilidad.

### 3. Módulo 1 (Calculadora & Recetas) - Constructor Dinámico y Personalizado de Ingredientes
- **Requerimientos:**
  - Poder añadir ingredientes manualmente uno a uno en la sección de *Composición de Ingredientes (% de Panadero)* sin un esquema rígido predeterminado.
  - Mantener la tabla visual de pesaje y costos establecida.
  - Disponer de una lista desplegable con insumos estándar del catálogo.
  - Adicionar en la lista desplegable la opción personalizada **"➕ [Personalizado / Añadir OTRO insumo nuevo...]"** para registrar nuevos insumos directamente sobre la marcha (nombre, categoría, unidad, costo de compra) e integrarlos a la receta de inmediato.

### 4. Corrección de Error de Importación (`create_ingredient`)
- **Error reportado:** `ImportError: cannot import name 'create_ingredient' from 'database'` en `app.py`.
- **Causa:** El proceso en ejecución de Streamlit mantenía en memoria caché una versión previa del módulo `database.py` cuando se invocaba la nueva función.
- **Solución:**
  - Se configuró en [app.py](file:///c:/Users/barbas/Desktop/Proyectos/palveti/app.py) la recarga explícita del módulo con `importlib.reload(database)`.
  - Se centralizaron todas las importaciones de base de datos a nivel superior (`init_db`, `get_connection`, `create_ingredient`, `add_ingredient_to_recipe`, `remove_ingredient_from_recipe`, `delete_recipe`, `update_ingredient_cost`).
  - Se eliminaron las sentencias de importación redundantes internas en los callbacks de botones.

### 5. Disponibilidad y Operación 24/7
- Se aclaró la diferencia entre el entorno local y la nube:
  - **Streamlit Cloud (`https://palvetti-web.streamlit.app`):** Funciona de forma continua 24/7 sin necesidad de tener el IDE abierto ni el PC encendido.
  - **Local (`localhost:8501`):** Depende del proceso de Python ejecutándose en la máquina local.

---

## 📂 Archivos del Proyecto Afectados en esta Sesión

1. [app.py](file:///c:/Users/barbas/Desktop/Proyectos/palveti/app.py): Constructor dinámico de recetas, selector con opción personalizada, integración del módulo de costos, centralización de imports.
2. [database.py](file:///c:/Users/barbas/Desktop/Proyectos/palveti/database.py): Funciones `create_ingredient`, `add_ingredient_to_recipe`, `remove_ingredient_from_recipe`, `delete_recipe`, `update_ingredient_cost` y normalización de costos iniciales en COP.
3. [baker_math.py](file:///c:/Users/barbas/Desktop/Proyectos/palveti/baker_math.py): Motor de cálculo de costos unitarios de tandas, márgenes, markups y formateo en moneda COP.
4. [.streamlit/config.toml](file:///c:/Users/barbas/Desktop/Proyectos/palveti/.streamlit/config.toml): Configuración headless para despliegue sin bloqueos en Streamlit Cloud.
5. [requirements.txt](file:///c:/Users/barbas/Desktop/Proyectos/palveti/requirements.txt): Dependencias de producción para la nube (`streamlit`, `pandas`).
6. [HISTORIAL_PROYECTO_PALVETI.md](file:///c:/Users/barbas/Desktop/Proyectos/palveti/HISTORIAL_PROYECTO_PALVETI.md): Registro global acumulado de funcionalidades del proyecto.
