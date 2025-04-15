import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Flujo de Caja – Promoción Inmobiliaria", layout="wide")
st.title("🧮 Modelo de Flujo de Caja – Promoción Inmobiliaria")

# === BLOQUE 1: DATOS GENERALES ===
st.header("📋 Datos Generales del Proyecto")

col1, col2 = st.columns(2)

with col1:
    num_viviendas = st.number_input("Nº de viviendas", min_value=1, value=20)
    st.caption(f"→ {num_viviendas:,.0f} viviendas")

    superficie_total = st.number_input("Superficie construida total (m²)", min_value=0.0, value=2000.0)
    st.caption(f"→ {superficie_total:,.0f} m² construidos")

    precio_medio_venta = st.number_input("Precio medio de venta por vivienda (€)", min_value=0.0, value=220000.0)
    st.caption(f"→ {precio_medio_venta:,.0f} € por vivienda")

with col2:
    fecha_inicio_obra = st.date_input("Fecha de inicio de obra", value=date.today())
    plazo_obra_meses = st.number_input("Plazo de ejecución (meses)", min_value=1, value=18)
    fecha_inicio_comercializacion = st.date_input("Fecha de inicio de comercialización", value=date.today())

# === BLOQUE 2: COSTES DEL PROYECTO ===
st.header("🏗️ Costes del Proyecto")

coste_suelo = st.number_input("Coste del Suelo (€)", min_value=0.0, value=300000.0)
st.caption(f"→ {coste_suelo:,.0f} €")

coste_ejecucion_m2 = st.number_input("Coste de ejecución por m²", min_value=0.0, value=750.0)
st.caption(f"→ {coste_ejecucion_m2:,.2f} €/m²")

porcentaje_honorarios = st.number_input("% Honorarios técnicos sobre ejecución", min_value=0.0, max_value=100.0, value=6.0)
porcentaje_admin = st.number_input("% Gastos administrativos sobre ejecución", min_value=0.0, max_value=100.0, value=3.0)

gastos_financieros = st.number_input("Gastos financieros por vivienda (€)", min_value=0.0, value=2000.0)
st.caption(f"→ Total: {gastos_financieros * num_viviendas:,.0f} €")

comisiones_venta = st.number_input("Comisiones (% sobre precio sin IVA)", min_value=0.0, max_value=100.0, value=4.0)

# === BLOQUE 3: INGRESOS ===
st.header("💰 Ingresos")

st.markdown("**Calendario de pagos del cliente**")

col_res, col_con, col_apl, col_esc = st.columns(4)

with col_res:
    reserva_fija = st.number_input("Reserva (€ por vivienda)", min_value=0.0, value=6000.0)
    st.caption(f"→ Total reservas: {reserva_fija * num_viviendas:,.0f} €")

with col_con:
    pct_contrato = st.number_input("Contrato (%) sobre precio con IVA", min_value=0.0, max_value=100.0, value=15.0)

with col_apl:
    pct_aplazado = st.number_input("Aplazado (%) sobre precio con IVA", min_value=0.0, max_value=100.0, value=10.0)

with col_esc:
    st.text_input("Escritura (%)", value="Resto", disabled=True)

# === BLOQUE 4: IVA y parámetros adicionales ===
st.header("📌 Parámetros Adicionales")

col_iva1, col_iva2, col_iva3 = st.columns(3)

with col_iva1:
    iva_venta = st.number_input("IVA en ventas (%)", min_value=0.0, max_value=100.0, value=10.0)
with col_iva2:
    iva_ejecucion = st.number_input("IVA en costes de ejecución (%)", min_value=0.0, max_value=100.0, value=10.0)
with col_iva3:
    iva_otros = st.number_input("IVA en otros gastos (%)", min_value=0.0, max_value=100.0, value=21.0)

# === CALENDARIO ===
fecha_fin_obra = fecha_inicio_obra + relativedelta(months=plazo_obra_meses)
fecha_entrega_viviendas = fecha_fin_obra + relativedelta(months=3)

st.subheader("📆 Calendario de proyecto")
st.caption(f"🏗️ Fin de obra estimado: **{fecha_fin_obra.strftime('%Y-%m-%d')}**")
st.caption(f"🏁 Entrega prevista: **{fecha_entrega_viviendas.strftime('%Y-%m-%d')}**")

st.header("🏘️ Planificación de Ventas por Mes")

# Generar meses hasta escritura (máximo desfase)
fecha_actual = fecha_inicio_comercializacion
fecha_ultima_escritura = fecha_fin_obra + relativedelta(months=3)
meses = []
while fecha_actual <= fecha_ultima_escritura:
    meses.append(fecha_actual.strftime("%Y-%m"))
    fecha_actual += relativedelta(months=1)

ventas_por_mes = {}
total_previsto = 0

st.markdown("### 📆 Indica cuántas viviendas vendes cada mes")
for mes in meses:
    col1, col2 = st.columns([3, 1])
    with col1:
        unidades = st.number_input(f"Ventas en {mes}", min_value=0, max_value=num_viviendas, key=f"ventas_{mes}")
        ventas_por_mes[mes] = unidades
        total_previsto += unidades

if total_previsto > num_viviendas:
    st.error(f"❌ Has asignado {total_previsto} viviendas, pero el máximo es {num_viviendas}.")
else:
    st.success(f"✅ Unidades asignadas: {total_previsto} de {num_viviendas}")

    st.header("📈 Cronograma Real de Ingresos y Comisiones")

    precio_con_iva = precio_medio_venta * (1 + iva_venta / 100)
    resto = precio_con_iva - reserva_fija
    importe_contrato = precio_con_iva * pct_contrato / 100
    importe_aplazado = precio_con_iva * pct_aplazado / 100
    importe_escritura = resto - importe_contrato - importe_aplazado

    ingresos_dict = {}
    comisiones_dict = {}
    for mes in meses:
        ingresos_dict[mes] = {
            "Reserva (€)": 0,
            "Contrato (€)": 0,
            "Aplazado (€)": 0,
            "Escritura (€)": 0,
            "Comisiones (€)": 0,
        }

    for i, mes_venta in enumerate(meses):
        unidades = ventas_por_mes[mes_venta]
        if unidades == 0:
            continue

        fecha_reserva = date.fromisoformat(mes_venta + "-01")
        fecha_contrato = fecha_reserva + relativedelta(months=1)
        fecha_aplazado = fecha_contrato + relativedelta(months=3)
        fecha_escritura = fecha_fin_obra + relativedelta(months=3)

        m_reserva = fecha_reserva.strftime("%Y-%m")
        m_contrato = fecha_contrato.strftime("%Y-%m")
        m_aplazado = fecha_aplazado.strftime("%Y-%m")
        m_escritura = fecha_escritura.strftime("%Y-%m")

        ingresos_dict[m_reserva]["Reserva (€)"] += unidades * reserva_fija
        ingresos_dict[m_contrato]["Contrato (€)"] += unidades * importe_contrato
        ingresos_dict[m_aplazado]["Aplazado (€)"] += unidades * importe_aplazado
        ingresos_dict[m_escritura]["Escritura (€)"] += unidades * importe_escritura

    for mes in meses:
        ingreso_total = sum(ingresos_dict[mes].values())
        base_comision = ingreso_total * comisiones_venta / 100
        comision_total = -base_comision * (1 + iva_otros / 100)  # ahora en negativo
        ingresos_dict[mes]["Comisiones (€)"] = comision_total

    resumen = {
        "Mes": [],
        "Reserva (€)": [],
        "Contrato (€)": [],
        "Aplazado (€)": [],
        "Escritura (€)": [],
        "Comisiones (€)": [],
        "Total ingresos (€)": [],
        "Ingresos netos (€)": []
    }

    for mes in meses:
        resumen["Mes"].append(mes)
        reserva = ingresos_dict[mes]["Reserva (€)"]
        contrato = ingresos_dict[mes]["Contrato (€)"]
        aplazado = ingresos_dict[mes]["Aplazado (€)"]
        escritura = ingresos_dict[mes]["Escritura (€)"]
        comisiones = ingresos_dict[mes]["Comisiones (€)"]
        total_ingresos = reserva + contrato + aplazado + escritura
        ingresos_netos = total_ingresos + comisiones

        resumen["Reserva (€)"].append(reserva)
        resumen["Contrato (€)"].append(contrato)
        resumen["Aplazado (€)"].append(aplazado)
        resumen["Escritura (€)"].append(escritura)
        resumen["Comisiones (€)"].append(comisiones)
        resumen["Total ingresos (€)"].append(total_ingresos)
        resumen["Ingresos netos (€)"].append(ingresos_netos)

    df = pd.DataFrame(resumen)
    df_mostrar = df.copy()
    df_mostrar["Total ingresos (€)"] = df_mostrar["Total ingresos (€)"].round(2)
    df_mostrar["Comisiones (€)"] = df_mostrar["Comisiones (€)"].round(2)
    df_mostrar["Ingresos netos (€)"] = df_mostrar["Ingresos netos (€)"].round(2)
    st.dataframe(df_mostrar, use_container_width=True)


    st.markdown("### 📊 Gráfico de Ingresos Acumulados")
    df["Acumulado"] = df["Total ingresos (€)"].cumsum()
    fig = px.line(df, x="Mes", y="Acumulado", markers=True, title="Evolución acumulada de ingresos")
    fig.update_layout(yaxis_title="€ acumulado")
    st.plotly_chart(fig, use_container_width=True)

    # === TABLA ACUMULADA DE INGRESOS Y COMISIONES ===
    st.markdown("### 📋 Tabla Acumulada de Ingresos y Comisiones")
    df_acumulado = df[["Mes", "Reserva (€)", "Contrato (€)", "Aplazado (€)", "Escritura (€)", "Comisiones (€)", "Total ingresos (€)", "Ingresos netos (€)"]].copy()
    df_acumulado["Reserva acumulado (€)"] = df_acumulado["Reserva (€)"].cumsum()
    df_acumulado["Contrato acumulado (€)"] = df_acumulado["Contrato (€)"].cumsum()
    df_acumulado["Aplazado acumulado (€)"] = df_acumulado["Aplazado (€)"].cumsum()
    df_acumulado["Escritura acumulado (€)"] = df_acumulado["Escritura (€)"].cumsum()
    df_acumulado["Comisiones acumulado (€)"] = df_acumulado["Comisiones (€)"].cumsum()
    df_acumulado["Ingresos totales acumulado (€)"] = df_acumulado["Total ingresos (€)"].cumsum()
    df_acumulado["Ingresos netos acumulado (€)"] = df_acumulado["Ingresos netos (€)"].cumsum()

    columnas_mostrar = [
        "Mes",
        "Reserva acumulado (€)",
        "Contrato acumulado (€)",
        "Aplazado acumulado (€)",
        "Escritura acumulado (€)",
        "Comisiones acumulado (€)",
        "Ingresos totales acumulado (€)",
        "Ingresos netos acumulado (€)"
    ]

    df_acumulado[columnas_mostrar[1:]] = df_acumulado[columnas_mostrar[1:]].round(2)
    st.dataframe(df_acumulado[columnas_mostrar], use_container_width=True)


# === BLOQUE: Costes de ejecución por capítulo ===
st.header("🏗️ Costes de ejecución por capítulo")

# Capítulos por defecto con importe (usados internamente)
def_capitulos_pesos = [
    ("Actuaciones previas", 5.65),
    ("Demoliciones", 250.3),
    ("Acondicionamiento del terreno", 17136.22),
    ("Cimentaciones", 16649.02),
    ("Estructuras", 75002.02),
    ("Fachadas y particiones", 61416.42),
    ("Carpintería, cerrajería, vidrios y protecciones solares", 69642.26),
    ("Remates y ayudas", 7821.92),
    ("Instalaciones", 126341.23),
    ("Aislamientos e impermeabilizaciones", 9647.18),
    ("Cubiertas", 22251.31),
    ("Revestimientos y trasdosados", 139035.68),
    ("Señalización y equipamiento", 45396.32),
    ("Urbanización interior de la parcela", 104182.23),
    ("Gestión de residuos", 7314.44),
    ("Control de calidad y ensayos", 403.22),
    ("Seguridad y salud", 1860.81)
]
df_def = pd.DataFrame(def_capitulos_pesos, columns=["Capítulo", "Importe"])
df_def["Peso (%)"] = df_def["Importe"] / df_def["Importe"].sum() * 100

# Opción de carga personalizada
st.markdown("📎 Opcional: cargar CSV con capítulos y PEM")
archivo_csv = st.file_uploader("Cargar archivo CSV con capítulos", type="csv")

if archivo_csv is not None:
    try:
        df_custom = pd.read_csv(archivo_csv, encoding="utf-8", sep=";", decimal=",", header=0, usecols=[0, 1], on_bad_lines='skip')
    except UnicodeDecodeError:
        df_custom = pd.read_csv(archivo_csv, encoding="latin1", sep=";", decimal=",", header=0, usecols=[0, 1], on_bad_lines='skip')
    df_custom.columns = ["Capítulo", "Importe"]
    df_custom["Importe"] = pd.to_numeric(df_custom["Importe"], errors="coerce")
    df_custom = df_custom.dropna(subset=["Importe"])
    df_custom["Peso (%)"] = df_custom["Importe"] / df_custom["Importe"].sum() * 100
    df_base = df_custom.copy()
else:
    df_base = df_def.copy()

# Calcular importe ajustado al coste total de ejecución
coste_total_ejecucion = superficie_total * coste_ejecucion_m2
df_base["Coste ejecución ajustado (€)"] = -round(df_base["Peso (%)"] * coste_total_ejecucion / 100, 2)

# Mostrar solo columnas relevantes
st.markdown(f"### 📊 Capítulos y pesos aplicados (Coste total ejecución: {coste_total_ejecucion:,.2f} €)")
st.dataframe(df_base[["Capítulo", "Peso (%)", "Coste ejecución ajustado (€)"]], use_container_width=True)

# === Fechas por defecto por capítulo ===
plantilla_fechas = {
    "Actuaciones previas": (0, 3),
    "Demoliciones": (1, 3),
    "Acondicionamiento del terreno": (2, 3),
    "Cimentaciones": (2, 4),
    "Estructuras": (3, 4),
    "Fachadas y particiones": (5, 4),
    "Carpintería, cerrajería, vidrios y protecciones solares": (7, 5),
    "Remates y ayudas": (11, 6),
    "Instalaciones": (11, 6),
    "Aislamientos e impermeabilizaciones": (11, 3),
    "Cubiertas": (13, 2),
    "Revestimientos y trasdosados": (14, 5),
    "Señalización y equipamiento": (16, 2),
    "Urbanización interior de la parcela": (16, 4),
    "Gestión de residuos": (0, 17),
    "Control de calidad y ensayos": (9, 5),
    "Seguridad y salud": (0, 17)
}

planificacion = []
for _, row in df_base.iterrows():
    capitulo = row["Capítulo"]
    offset, duracion = plantilla_fechas.get(capitulo, (0, 6))
    inicio = fecha_inicio_obra + relativedelta(months=offset)
    planificacion.append({"Capítulo": capitulo, "Inicio": inicio, "Duración (meses)": duracion})

df_planificacion = pd.DataFrame(planificacion)

st.markdown("### 🗂️ Revisión y ajustes de planificación por capítulo")
df_editable = st.data_editor(df_planificacion, num_rows="dynamic", use_container_width=True)

# === Gantt ===
st.markdown("### 📆 Gráfico de Gantt generado")
df_editable["Fin"] = pd.to_datetime(df_editable["Inicio"]) + df_editable["Duración (meses)"].apply(lambda m: relativedelta(months=int(m)))
fig = px.timeline(
    df_editable,
    x_start="Inicio",
    x_end="Fin",
    y="Capítulo",
    color="Capítulo",
    title="Gantt de ejecución por capítulo"
)
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)

# === Cronograma económico mensual ===
st.markdown("### 📅 Cronograma económico mensual")

fecha_min = df_editable["Inicio"].min()
fecha_max = df_editable["Fin"].max()
meses = pd.date_range(start=fecha_min, end=fecha_max, freq="MS")
meses_str = [m.strftime("%Y-%m") for m in meses]
cronograma = pd.DataFrame({"Mes": meses_str})

costes = dict(zip(df_base["Capítulo"], df_base["Coste ejecución ajustado (€)"]))

for _, row in df_editable.iterrows():
    capitulo = row["Capítulo"]
    inicio = row["Inicio"]
    duracion = int(row["Duración (meses)"])
    fechas = [(inicio + relativedelta(months=i)).strftime("%Y-%m") for i in range(duracion)]
    mensualidad = round(costes.get(capitulo, 0) / duracion, 2)
    cronograma[capitulo] = [mensualidad if m in fechas else 0 for m in meses_str]

cronograma["Total mensual (€)"] = cronograma.drop(columns=["Mes"]).sum(axis=1)
st.dataframe(cronograma, use_container_width=True)

# === BLOQUE: Costes Indirectos (Honorarios y Administración) ===
st.header("💼 Costes Indirectos")

# Cálculo de fechas clave
fecha_fin_obra = fecha_inicio_obra + relativedelta(months=plazo_obra_meses)
fecha_escritura = fecha_fin_obra + relativedelta(months=3)

# Cálculo de importes con IVA (en negativo porque son gastos)
honorarios_base = coste_total_ejecucion * porcentaje_honorarios / 100
honorarios_total = -honorarios_base * (1 + iva_otros / 100)

admin_base = coste_total_ejecucion * porcentaje_admin / 100
admin_total = -admin_base * (1 + iva_otros / 100)

# Distribución de honorarios técnicos
honorarios_inicio = honorarios_total * 0.50
honorarios_final = honorarios_total * 0.30
honorarios_lineal_total = honorarios_total * 0.20
honorarios_lineal_mensual = honorarios_lineal_total / plazo_obra_meses

# Distribución de gastos administrativos
admin_inicio = admin_total * 0.50
admin_entrega = admin_total * 0.50

# Crear cronograma mensual desde inicio de obra hasta mes de escritura
fechas = pd.date_range(start=fecha_inicio_obra, end=fecha_escritura, freq="MS")
cronograma_indirectos = pd.DataFrame({"Mes": fechas.strftime("%Y-%m")})
cronograma_indirectos["Honorarios Técnicos (€)"] = 0.0
cronograma_indirectos["Gastos Administración (€)"] = 0.0

for i, fila in cronograma_indirectos.iterrows():
    mes = pd.to_datetime(fila["Mes"])
    if mes.date() == fecha_inicio_obra.replace(day=1):
        cronograma_indirectos.at[i, "Honorarios Técnicos (€)"] += honorarios_inicio
        cronograma_indirectos.at[i, "Gastos Administración (€)"] += admin_inicio
    if fecha_inicio_obra <= mes.date() < fecha_fin_obra:
        cronograma_indirectos.at[i, "Honorarios Técnicos (€)"] += honorarios_lineal_mensual
    if mes.date() == fecha_fin_obra.replace(day=1):
        cronograma_indirectos.at[i, "Honorarios Técnicos (€)"] += honorarios_final
    if mes.date() == fecha_escritura.replace(day=1):
        cronograma_indirectos.at[i, "Gastos Administración (€)"] += admin_entrega

st.markdown("### 📋 Cronograma mensual de costes indirectos")
st.dataframe(cronograma_indirectos, use_container_width=True)

# === BLOQUE: Costes Financieros ===
st.header("🏦 Costes Financieros")

# Crear diccionario para cronograma financiero por mes
cronograma_financieros = {}

# Imputar coste financiero (en negativo) en el mes del contrato (1 mes después de reserva)
for mes_venta, unidades in ventas_por_mes.items():
    if unidades == 0:
        continue
    fecha_reserva = date.fromisoformat(mes_venta + "-01")
    fecha_contrato = fecha_reserva + relativedelta(months=1)
    mes_contrato = fecha_contrato.strftime("%Y-%m")
    if mes_contrato not in cronograma_financieros:
        cronograma_financieros[mes_contrato] = 0.0
    cronograma_financieros[mes_contrato] += -unidades * gastos_financieros  # Importe en negativo

# Convertir a DataFrame
df_financieros = pd.DataFrame(sorted(cronograma_financieros.items()), columns=["Mes", "Coste Financiero (€)"])

st.markdown("### 📋 Cronograma mensual de costes financieros")
st.dataframe(df_financieros, use_container_width=True)

# === BLOQUE FINAL: Flujo de Caja General de la Promoción ===
st.header("📊 Flujo de Caja General de la Promoción")

# Unir todas las tablas por columna "Mes"
df_flujo = cronograma[["Mes", "Total mensual (€)"]].rename(columns={"Total mensual (€)": "Coste ejecución (€)"})
df_flujo = df_flujo.merge(cronograma_indirectos, on="Mes", how="outer")
df_flujo = df_flujo.merge(df_financieros, on="Mes", how="outer")
df_flujo = df_flujo.merge(df[["Mes", "Ingresos netos (€)"]], on="Mes", how="outer")

# Añadir columna de coste del suelo (solo en el primer mes del cronograma)
df_flujo["Coste del suelo (€)"] = 0.0
if not df_flujo.empty:
    df_flujo.loc[df_flujo.index[0], "Coste del suelo (€)"] = -coste_suelo

# Rellenar vacíos con 0
df_flujo = df_flujo.fillna(0)

# Calcular total mensual y saldo acumulado
df_flujo["Total mensual (€)"] = df_flujo[
    ["Ingresos netos (€)", "Coste del suelo (€)", "Coste ejecución (€)", "Honorarios Técnicos (€)",
     "Gastos Administración (€)", "Coste Financiero (€)"]
].sum(axis=1)

df_flujo["Saldo acumulado (€)"] = df_flujo["Total mensual (€)"].cumsum()

# === CÁLCULO DE CUENTA ESPECIAL ===
df_cuenta_esp = pd.merge(
    df[["Mes", "Ingresos netos (€)"]],
    cronograma[["Mes", "Total mensual (€)"]].rename(columns={"Total mensual (€)": "Coste ejecución (€)"}),
    on="Mes", how="outer"
).fillna(0)

df_cuenta_esp["Movimiento cuenta especial (€)"] = df_cuenta_esp["Ingresos netos (€)"] + df_cuenta_esp["Coste ejecución (€)"]
df_cuenta_esp["Saldo cuenta especial (€)"] = df_cuenta_esp["Movimiento cuenta especial (€)"].cumsum()

# Añadir columnas de cuenta especial al flujo general
df_flujo = df_flujo.merge(
    df_cuenta_esp[["Mes", "Movimiento cuenta especial (€)", "Saldo cuenta especial (€)"]],
    on="Mes", how="left"
)

# Reordenar columnas
columnas_ordenadas = [
    "Mes",
    "Ingresos netos (€)",
    "Coste del suelo (€)",
    "Coste ejecución (€)",
    "Honorarios Técnicos (€)",
    "Gastos Administración (€)",
    "Coste Financiero (€)",
    "Total mensual (€)",
    "Saldo acumulado (€)",
    "Movimiento cuenta especial (€)",
    "Saldo cuenta especial (€)"
]
df_flujo = df_flujo[columnas_ordenadas]

# === VISUALIZACIÓN FINAL CON FORMATO DECIMAL ===
st.markdown("### 📋 Tabla consolidada de flujos de caja")

def resaltar_saldo_negativo(val):
    if isinstance(val, (int, float)) and val < 0:
        return "background-color: #ffd6d6"  # Rojo claro
    return ""

# Aplicar formato numérico y estilo condicional
df_estilado = df_flujo.style \
    .applymap(resaltar_saldo_negativo, subset=["Saldo cuenta especial (€)"]) \
    .format("{:,.2f}", subset=[col for col in df_flujo.columns if col != "Mes"])

st.dataframe(df_estilado, use_container_width=True)

# === ALERTA VISUAL SI EL SALDO DE LA CUENTA ESPECIAL ES NEGATIVO ===
if (df_flujo["Saldo cuenta especial (€)"] < 0).any():
    st.error("⚠️ El saldo de la cuenta especial es NEGATIVO en algunos meses. Será necesario cubrir el déficit con fondos propios.")
else:
    st.success("✅ El saldo de la cuenta especial se mantiene siempre positivo.")

# === BLOQUE: Movimiento de la Cuenta Especial ===
st.header("🏦 Cuenta Especial Intervenida")

df_cuenta_especial = df_flujo[["Mes", "Ingresos netos (€)", "Coste ejecución (€)"]].copy()
df_cuenta_especial.rename(columns={
    "Ingresos netos (€)": "Ingresos en cuenta especial (€)",
    "Coste ejecución (€)": "Pagos desde cuenta especial (€)"
}, inplace=True)

df_cuenta_especial["Movimiento mensual (€)"] = df_cuenta_especial["Ingresos en cuenta especial (€)"] + df_cuenta_especial["Pagos desde cuenta especial (€)"]
df_cuenta_especial["Saldo cuenta especial (€)"] = df_cuenta_especial["Movimiento mensual (€)"].cumsum()

# Alerta si hay saldo negativo
if (df_cuenta_especial["Saldo cuenta especial (€)"] < 0).any():
    st.warning("⚠️ El saldo de la cuenta especial es NEGATIVO en algunos meses. Será necesario cubrir el déficit con fondos propios.")

# Mostrar tabla con celdas rojas si hay saldo negativo
def resaltar_negativos(val):
    return 'background-color: #f8d7da;' if val < 0 else ''

st.markdown("### 📋 Movimiento mensual de la cuenta especial")
st.dataframe(
    df_cuenta_especial.style.applymap(resaltar_negativos, subset=["Saldo cuenta especial (€)"]),
    use_container_width=True
)