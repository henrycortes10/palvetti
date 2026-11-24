# 🥖 PALVETI - Sistema de Gestión para Panadería Artesanal de Masa Madre

Aplicación local y ligera desarrollada en **Python + Streamlit + SQLite** diseñada específicamente para la planificación, producción por porcentaje de panadero, control de fermentación, inventarios y finanzas del obrador artesanal **PALVETI**.

---

## 🚀 Inicio Rápido (En 1 Clic)

Simplemente haz doble clic sobre el archivo:
```bat
iniciar_palveti.bat
```
El sistema abrirá automáticamente la aplicación en tu navegador en: `http://localhost:8501`.

---

## 🛠️ Requisitos Previos

Si abres el proyecto por primera vez en otra máquina:
```bash
pip install streamlit pandas
```

---

## 📂 Estructura del Proyecto

- `app.py`: Interfaz visual interactiva completa con 6 módulos especializados.
- `database.py`: Esquema relacional SQLite (`palveti.db`) y precarga de insumos, recetas y clientes base.
- `baker_math.py`: Motor de cálculo de Porcentaje de Panadero, escalado dinámico de masa, costeo al gramo y descuento automático de inventario.
- `iniciar_palveti.bat`: Lanzador directo para Windows.
- `palveti.db`: Base de datos SQLite local (se genera automáticamente al primer arranque).

---

## 📋 Módulos Implementados

1. **Calculadora & Recetas (El Núcleo):**
   - Manejo de porcentajes de panadero con harina base al 100%.
   - Cálculo automático de gramos por ingrediente según la cantidad de hogazas y el peso deseado.
   - Botón directo para crear y planificar un lote de producción.
2. **Costos & Fijación de Precios:**
   - Desglose de costos de materia prima por unidad.
   - Simulador con margen porcentual sobre venta, markup sobre costo o ganancia fija en dólares por pan.
3. **Inventario & Materia Prima:**
   - Semáforo y alertas automáticas de stock mínimo.
   - Registro de entradas (compras) y nuevos insumos.
4. **Gestión de Pedidos & Lotes (Preventa):**
   - Agrupación de pedidos por fecha y lote de horneado.
   - Flujo de estados: *Registrado ➔ Pagado ➔ En Fermentación ➔ Horneado ➔ Entregado*.
   - Directorio de clientes con preferencias específicas de corteza, rebanado, etc.
   - Botón para descontar automáticamente los insumos consumidos del stock.
5. **Bitácora de Fermentación & Control de Calidad:**
   - Registro de variables ambientales y técnicas: temperatura ambiente, temperatura de la masa, tiempo de autólisis, horas de bloque, pliegues (*folds*), horas en frío y temperatura de nevera.
   - Calificación de calidad (1-5 estrellas) y observaciones sobre alveolado, greña y salto de horno.
6. **Finanzas & Reportes:**
   - Resumen en tiempo real de ingresos por ventas, costos de materia prima y gastos operativos (gas, energía, empaques).
   - Cálculo de utilidad neta y margen operativo.
