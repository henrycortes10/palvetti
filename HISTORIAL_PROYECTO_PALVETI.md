# 🥖 PALVETI - Historial Completo del Proyecto y Conversación

> **ID de Conversación Original:** `3cb8bb60-8d4b-45af-8251-e79ea248637d`  
> **Fecha de guardado:** 26 de Noviembre de 2026  
> **Repositorio GitHub:** `https://github.com/henrycortes10/palvetti.git`  
> **Ubicación Local:** `c:\Users\USER\Desktop\palvetti`

---

## 📌 ¿Cómo retomar esta conversación en Antigravity IDE en otro PC?

Cuando abras este proyecto en el nuevo PC con **Antigravity IDE**, simplemente escribe en el chat el siguiente mensaje:

```text
Por favor lee el archivo HISTORIAL_PROYECTO_PALVETI.md para entender todo el contexto, requerimientos y estado del proyecto, y continuemos desde aquí.
```

El asistente leerá todo este archivo y sabrá exactamente qué se ha hecho, qué errores se corrigieron y qué falta por hacer.

---

## 🧭 ¿Dónde guarda Antigravity el historial de conversaciones en tu PC?

1. **En la interfaz gráfica de Antigravity IDE:**
   - En la esquina superior del panel de chat, busca el ícono de **Historial / Reloj** o el desplegable de conversaciones.
   - También puedes presionar `Ctrl + Shift + P`, escribir `Antigravity` y seleccionar **"Antigravity: List Conversations"** o abrir el panel de chats anteriores.
2. **En el disco duro de Windows:**
   - Las conversaciones se guardan en la ruta:
     `C:\Users\<TU_USUARIO>\.gemini\antigravity\brain\`
   - La carpeta específica de esta conversación es:
     `C:\Users\<TU_USUARIO>\.gemini\antigravity\brain\3cb8bb60-8d4b-45af-8251-e79ea248637d\`
   - Dentro encontrarás los archivos `transcript.jsonl` y `transcript_full.jsonl` que contienen cada mensaje intercambiado. Si copias esa carpeta a la misma ruta en tu otro PC, Antigravity la reconocerá en su historial.

---

## 📋 Resumen Ejecutivo del Proyecto PALVETI

**PALVETI** es una aplicación de escritorio/web local desarrollada en **Python + Streamlit + SQLite** diseñada específicamente para la gestión operativa y artesanal de una panadería de masa madre.

### Módulos Desarrollados y Estado Actual:

1. **🥖 1. Calculadora & Recetas (Núcleo):**
   - Porcentajes panaderos con Harina al 100%.
   - Escalado dinámico por número de piezas y peso por pieza.
   - Inclusión automática de prefermento / masa madre y cálculo exacto de hidratación total.
2. **💰 2. Costos & Fijación de Precios:**
   - Precios y costos configurados en **Pesos Colombianos (COP)** (sin decimales innecesarios, ej: `$3.500 COP`).
   - Cálculo de costo por gramo y margen de ganancia.
3. **📦 3. Inventario & Materia Prima:**
   - Descuento automático de inventario al registrar una producción de lote.
   - Registro de entradas de insumos con notificación visual inmediata.
   - Alerta visual de stock mínimo.
4. **📋 4. Pedidos & Preventa (Lotes):**
   - Directorio de clientes dividido en dos pestañas: **Clientes Minoristas / Retail** y **Clientes Mayoristas (B2B)**.
   - Opciones completas para **Editar** y **Eliminar** pedidos.
   - Formateo limpio de teléfonos sin decimales flotantes (`3003545` en lugar de `3003545,0000`).
5. **🍇 5. Bitácora de Fermentación & Calidad:**
   - Control de tiempos y temperaturas (bloque, retardo en frío, horneado).
   - Formato numérico limpio en temperaturas sin ceros sobrantes.
6. **📊 6. Finanzas & Reportes:**
   - Historial de gastos con filtro mensual y selector de rango de fechas.
   - Métricas de ingresos, egresos y balance general en COP.
7. **📅 7. Calendario de Actividades (Estilo Google Calendar):**
   - Matriz mensual y vista semanal del obrador.
   - Chips codificados por color (Insumos, Amasado, Horneado, Cierre de Pedidos, Entrega, Masa Madre, Mantenimiento).
   - **Efecto Hover Zoom:** Al pasar el mouse sobre cualquier celda, se anima con un zoom leve y sombra elegante.
   - **Botón `➕` o `✏️ Editar`:** Integrado en la esquina superior derecha dentro de la misma celda de fecha.
   - **Modal de edición directa:** Al hacer clic, abre una ventana flotante (`@st.dialog`) para editar, completar o eliminar actividades, o agendar nuevas tareas para ese día.
8. **🛠️ 8. Mantenimiento de Equipos & Alarmas:**
   - Monitoreo de hornos, amasadoras, neveras y fermentadoras con semáforo de estado (Al Día, Próximo a vencer, Vencido).
   - Opciones para registrar, **Editar**, **Eliminar** equipos y marcar mantenimientos como realizados.
9. **🔔 Campana de Notificaciones Global (Esquina Superior Derecha):**
   - Visible en cualquier módulo del sistema.
   - Despliega alertas en tiempo real: alarmas de mantenimiento vencido o próximo, insumos bajo el stock mínimo, pedidos pendientes y eventos del calendario (con aviso de 1 día de anticipación y del día actual).

---

## 🛠️ Estructura de Archivos del Proyecto

- `app.py`: Aplicación principal de interfaz Streamlit con estilos modernos (Tailwind `red-800` `#991b1b`).
- `baker_math.py`: Funciones matemáticas del panadero, alertas de notificación y formateo de moneda COP.
- `database.py`: Esquema y migraciones automáticas de SQLite (`palveti.db`).
- `iniciar_palveti.bat`: Script de inicio rápido con doble clic para Windows con detección automática de Python y apertura en el navegador.
- `requirements.txt`: Dependencias del proyecto (`streamlit`, `pandas`).
- `palveti.db`: Base de datos SQLite local con todas las tablas y datos del obrador.

---

## 🚀 Despliegue en la Nube (Streamlit Community Cloud)

- **URL de Producción:** `https://palvetti-web.streamlit.app`
- **Repositorio Conectado:** `https://github.com/henrycortes10/palvetti.git` (rama `main`)
- **Configuración de Despliegue:**
  - `requirements.txt`: Contiene `streamlit>=1.30.0` y `pandas>=2.0.0`.
  - `.streamlit/config.toml`: Configurado con `headless = true` y `gatherUsageStats = false` para omitir el prompt interactivo de terminal y permitir que el healthcheck de Streamlit Cloud responda inmediatamente.

---

## 🚀 Cómo Iniciar la Aplicación en Cualquier PC (Modo Local)

1. Asegúrate de tener instalado Python 3.10 o superior.
2. Instala las dependencias:
   ```cmd
   pip install -r requirements.txt
   ```
3. Ejecuta con doble clic el archivo `iniciar_palveti.bat` o desde la consola con:
   ```cmd
   python -m streamlit run app.py
   ```
4. Se abrirá automáticamente en tu navegador en `http://localhost:8501`.
