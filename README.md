# 🏗️ Herramienta de Flujos de Caja para Promociones Inmobiliarias

Esta aplicación permite generar flujos de caja mensuales para promociones inmobiliarias, desde la fase inicial hasta la entrega de las viviendas, integrando cronogramas de ingresos, costes (ejecución, indirectos y financieros) y necesidades de financiación. Todo se gestiona a través de una interfaz web interactiva desarrollada con Streamlit.

## 🚀 Funcionalidades principales

- Inputs generales del proyecto y parámetros económicos clave.
- Planificación de ventas mensual (manual o importada desde Excel).
- Generación automática de cronograma de ingresos por fases de pago.
- Cálculo de comisiones por ventas según fases.
- Planificación y cronograma de ejecución por capítulos con vista Gantt editable.
- Carga de costes de ejecución desde CSV o tabla predefinida.
- Cálculo automático de costes indirectos y financieros según reglas establecidas.
- Generación de tablas y gráficos acumulados.
- Análisis del saldo de la cuenta especial intervenida y necesidades de financiación.
- Exportación de resultados y visualización en pestañas.

## 🧰 Requisitos

- Python 3.10+
- Streamlit
- Pandas
- Plotly
- WeasyPrint
- openpyxl
- Otros módulos estándar incluidos en `requirements.txt`.

## 📦 Instalación

1. Clona el repositorio o descarga los archivos:
   ```bash
   git clone https://github.com/tu_usuario/nombre_proyecto.git
   cd nombre_proyecto

2.	Crea un entorno virtual e instálalo:
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    pip install -r requirements.txt

3.	Ejecuta la aplicación:
    streamlit run streamlit_app.py  

## 📂 Estructura esperada
	•	streamlit_app.py: Lógica principal de la aplicación.
	•	requirements.txt: Lista de dependencias.
	•	data/: Carpeta opcional para almacenar versiones guardadas o archivos de entrada.
	•	csv/: Archivos CSV con estructura de capítulos por defecto.

## 📥 Cómo usar la aplicación
	1.	Inputs Generales: Rellena los datos del proyecto: nombre, fechas clave, número de viviendas, m² construidos, costes unitarios y parámetros generales.
	2.	Ingresos y Comisiones: Introduce la tabla de ventas mensual o pégala desde Excel. Se generarán automáticamente los ingresos por fases de pago (reserva, contrato, aplazado y escritura).
	3.	Costes:
	•	Carga o edita los capítulos de ejecución y sus pesos.
	•	Revisa o modifica las fechas y duración por capítulo.
	•	Visualiza el cronograma Gantt.
	•	Se generarán los cronogramas económicos mensuales de ejecución, indirectos y financieros.
	4.	Flujo de Caja: Se muestra el flujo global, acumulado, saldo de la cuenta especial y necesidades de financiación mes a mes.
	5.	Resumen: Incluye:
	•	Tabla resumen del flujo de caja.
	•	Gráfico Gantt del cronograma de ejecución.
	•	Tabla de ventas mensuales.
	•	Descarga de CSV con todos los inputs para informes o presentaciones.

## 📝 Notas adicionales
	•	Todos los cálculos se adaptan automáticamente a las fechas de comercialización y obra definidas.
	•	Los ingresos siguen un calendario fijo por cliente: reserva (mes venta), contrato (+1), aplazado (+3), escritura (+3 desde fin de obra).
	•	Las comisiones se calculan por fase e incluyen IVA en los costes comerciales.
	•	La cuenta especial solo cubre costes de ejecución. El resto de costes se cubre con fondos propios o se registran como necesidades de financiación.
