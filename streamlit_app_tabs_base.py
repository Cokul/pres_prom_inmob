import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Flujo de Caja – Promoción Inmobiliaria", layout="wide")

# === Nombre del Proyecto ===
nombre_proyecto = st.text_input("🏗️ Nombre del Proyecto", value="Promoción Residencial")
st.title(f"🧮 Modelo de Flujo de Caja – {nombre_proyecto}")

tabs = st.tabs(["Inputs Generales", "Ingresos y Comisiones", "Costes", "Flujo y Resumen"])

# === Inicialización de fechas por defecto ===
if "fecha_inicio_obra" not in st.session_state:
    st.session_state["fecha_inicio_obra"] = date.today()
if "fecha_inicio_comercializacion" not in st.session_state:
    st.session_state["fecha_inicio_comercializacion"] = date.today()
if "plazo_obra_meses" not in st.session_state:
    st.session_state["plazo_obra_meses"] = 18

fecha_inicio_obra = st.session_state["fecha_inicio_obra"]
fecha_inicio_comercializacion = st.session_state["fecha_inicio_comercializacion"]
plazo_obra_meses = st.session_state["plazo_obra_meses"]

with tabs[0]:
    st.header("📋 Datos Generales del Proyecto")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        num_viviendas = st.number_input("Nº de viviendas", min_value=1, value=20)
        superficie_total = st.number_input("Superficie construida total (m²)", min_value=0.0, value=2000.0)
        precio_medio_venta = st.number_input("Precio medio de venta por vivienda (€)", min_value=0.0, value=220000.0)
    with col_b:
        coste_suelo = st.number_input("Coste del Suelo (€)", min_value=0.0, value=300000.0)
        coste_ejecucion_m2 = st.number_input("Coste ejecución por m²", min_value=0.0, value=750.0)
        comisiones_venta = st.number_input("Comisiones (% sobre precio sin IVA)", min_value=0.0, max_value=100.0, value=4.0)
    with col_c:
        porcentaje_honorarios = st.number_input("% Honorarios técnicos", min_value=0.0, max_value=100.0, value=6.0)
        porcentaje_admin = st.number_input("% Gastos administración", min_value=0.0, max_value=100.0, value=3.0)
        gastos_financieros = st.number_input("Gastos financieros por vivienda (€)", min_value=0.0, value=2000.0)

    st.header("📌 Parámetros Adicionales")
    col_iva1, col_iva2, col_iva3 = st.columns(3)
    with col_iva1:
        iva_venta = st.number_input("IVA en ventas (%)", min_value=0.0, max_value=100.0, value=10.0)
    with col_iva2:
        iva_ejecucion = st.number_input("IVA en costes de ejecución (%)", min_value=0.0, max_value=100.0, value=10.0)
    with col_iva3:
        iva_otros = st.number_input("IVA en otros gastos (%)", min_value=0.0, max_value=100.0, value=21.0)

    st.markdown("### 🗓️ Fechas del Proyecto")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        fecha_inicio_obra = st.date_input("Fecha de inicio de obra", value=fecha_inicio_obra, key="fecha_inicio_obra")
    with col_f2:
        fecha_inicio_comercializacion = st.date_input("Inicio comercialización", value=fecha_inicio_comercializacion, key="fecha_inicio_comercializacion")
    with col_f3:
        plazo_obra_meses = st.number_input("Plazo de ejecución (meses)", min_value=1, value=plazo_obra_meses, key="plazo_obra_meses")

with tabs[1]:
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

    st.subheader("📆 Calendario de proyecto")
    fecha_fin_obra = fecha_inicio_obra + relativedelta(months=plazo_obra_meses)
    fecha_entrega_viviendas = fecha_fin_obra + relativedelta(months=3)
    st.caption(f"🏗️ Fin de obra estimado: **{fecha_fin_obra.strftime('%Y-%m-%d')}**")
    st.caption(f"🏁 Entrega prevista: **{fecha_entrega_viviendas.strftime('%Y-%m-%d')}**")

    st.header("🏘️ Planificación de Ventas por Mes")
    fecha_actual = fecha_inicio_comercializacion
    fecha_ultima = fecha_entrega_viviendas
    meses = []
    while fecha_actual <= fecha_ultima:
        meses.append(fecha_actual.strftime("%Y-%m"))
        fecha_actual += relativedelta(months=1)

    ventas_por_mes = {}
    total_previsto = 0
    st.markdown("### 📆 Indica cuántas viviendas vendes cada mes")

    cols = st.columns(4)
    for i, mes in enumerate(meses):
        with cols[i // 6 % 4]:
            unidades = st.number_input(f"{mes}", min_value=0, max_value=num_viviendas, key=f"ventas_{mes}")
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
        # Asegurar que todos los meses posibles estén creados
        fecha_min = fecha_inicio_comercializacion
        fecha_max = fecha_entrega_viviendas + relativedelta(months=6)
        while fecha_min <= fecha_max:
            key = fecha_min.strftime("%Y-%m")
            ingresos_dict[key] = {
                "Reserva (€)": 0,
                "Contrato (€)": 0,
                "Aplazado (€)": 0,
                "Escritura (€)": 0,
                "Comisiones (€)": 0,
            }
            fecha_min += relativedelta(months=1)

        for mes_venta in ventas_por_mes:
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

        for mes in ingresos_dict:
            ingreso_total = sum([
                ingresos_dict[mes]["Reserva (€)"],
                ingresos_dict[mes]["Contrato (€)"],
                ingresos_dict[mes]["Aplazado (€)"],
                ingresos_dict[mes]["Escritura (€)"]
            ])
            base_comision = ingreso_total * comisiones_venta / 100
            comision_total = -base_comision * (1 + iva_otros / 100)
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

        for mes in sorted(ingresos_dict):
            reserva = ingresos_dict[mes]["Reserva (€)"]
            contrato = ingresos_dict[mes]["Contrato (€)"]
            aplazado = ingresos_dict[mes]["Aplazado (€)"]
            escritura = ingresos_dict[mes]["Escritura (€)"]
            comisiones = ingresos_dict[mes]["Comisiones (€)"]
            total_ingresos = reserva + contrato + aplazado + escritura
            ingresos_netos = total_ingresos + comisiones

            resumen["Mes"].append(mes)
            resumen["Reserva (€)"].append(reserva)
            resumen["Contrato (€)"].append(contrato)
            resumen["Aplazado (€)"].append(aplazado)
            resumen["Escritura (€)"].append(escritura)
            resumen["Comisiones (€)"].append(comisiones)
            resumen["Total ingresos (€)"].append(total_ingresos)
            resumen["Ingresos netos (€)"].append(ingresos_netos)

        df = pd.DataFrame(resumen)
        df["Acumulado"] = df["Total ingresos (€)"].cumsum()

        st.subheader("📋 Tabla mensual de ingresos y comisiones")
        st.dataframe(df.round(2), use_container_width=True)

        st.subheader("📊 Gráfico de Ingresos Acumulados")
        fig = px.line(df, x="Mes", y="Acumulado", markers=True, title="Evolución acumulada de ingresos")
        fig.update_layout(yaxis_title="€ acumulado")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Tabla acumulada por conceptos")
        df_acumulado = df.copy()
        for col in ["Reserva (€)", "Contrato (€)", "Aplazado (€)", "Escritura (€)", "Comisiones (€)", "Total ingresos (€)", "Ingresos netos (€)"]:
            df_acumulado[f"{col[:-4]} acumulado (€)"] = df_acumulado[col].cumsum()
        columnas = ["Mes"] + [c for c in df_acumulado.columns if "acumulado" in c]
        st.dataframe(df_acumulado[columnas].round(2), use_container_width=True)

with tabs[2]:
    st.write("🚧 Costes... (pendiente)")

with tabs[3]:
    st.write("🚧 Flujo y resumen... (pendiente)")