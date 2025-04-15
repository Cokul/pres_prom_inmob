import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Flujo de Caja – Promoción Inmobiliaria", layout="wide")

# === Nombre del Proyecto ===
nombre_proyecto = st.text_input("🏗️ Nombre del Proyecto", value="Promoción Residencial")
st.title(f"🧮 Modelo de Flujo de Caja – {nombre_proyecto}")

tabs = st.tabs(["Inputs Generales", "Ingresos y Comisiones", "Costes", "Flujo de Caja", "Resumen"])

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
                reserva = ingresos_dict[mes]["Reserva (€)"]
                contrato = ingresos_dict[mes]["Contrato (€)"]
                aplazado = ingresos_dict[mes]["Aplazado (€)"]
                escritura = ingresos_dict[mes]["Escritura (€)"]

                # Comisión sobre importe sin IVA de venta, con IVA de gasto
                comision_reserva = reserva / (1 + iva_venta / 100) * (comisiones_venta / 100) * (1 + iva_otros / 100)
                comision_contrato = contrato / (1 + iva_venta / 100) * (comisiones_venta / 100) * (1 + iva_otros / 100)
                comision_aplazado = aplazado / (1 + iva_venta / 100) * (comisiones_venta / 100) * (1 + iva_otros / 100)
                comision_escritura = escritura / (1 + iva_venta / 100) * (comisiones_venta / 100) * (1 + iva_otros / 100)

                comision_total = -(comision_reserva + comision_contrato + comision_aplazado + comision_escritura)
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
    st.header("🏗️ Costes de ejecución por capítulo")

    coste_total_ejecucion = superficie_total * coste_ejecucion_m2

    # === BLOQUE 1: Pesos por defecto establecidos ===
    pesos_defecto = {
        'Actuaciones previas': 0.0008,
        'Demoliciones': 0.03554,
        'Acondicionamiento del terreno': 2.43289,
        'Cimentaciones': 2.36372,
        'Estructuras': 10.64831,
        'Fachadas y particiones': 8.71951,
        'Carpintería, cerrajería, vidrios y protecciones solares': 9.88736,
        'Remates y ayudas': 1.11051,
        'Instalaciones': 17.93712,
        'Aislamientos e impermeabilizaciones': 1.36965,
        'Cubiertas': 3.1591,
        'Revestimientos y trasdosados': 19.7394,
        'Señalización y equipamiento': 6.44508,
        'Urbanización interior de la parcela': 14.79113,
        'Gestión de residuos': 1.03846,
        'Control de calidad y ensayos': 0.05725,
        'Seguridad y salud': 0.26417
    }

    df_capitulos = pd.DataFrame({
        "Capítulo": list(pesos_defecto.keys()),
        "Peso (%)": list(pesos_defecto.values())
    })
    df_capitulos["Coste ejecución ajustado (€)"] = -round(df_capitulos["Peso (%)"] * coste_total_ejecucion / 100, 2)

    # === BLOQUE 2: Carga opcional de CSV
    st.markdown("### 📂 Cargar capítulos y valores (opcional)")
    st.caption("Sube un CSV con columnas 'Capítulo' y el **importe** del capítulo (no el porcentaje)")
    archivo_csv = st.file_uploader("Arrastra y suelta el archivo aquí", type=["csv"])

    if archivo_csv:
        try:
            df_csv = pd.read_csv(archivo_csv, sep=None, engine="python", decimal=",")
            columna_importe = df_csv.columns[1]
            df_csv[columna_importe] = df_csv[columna_importe].astype(str).str.replace(",", ".").astype(float)
            df_csv = df_csv.rename(columns={columna_importe: "Importe"})
            df_csv["Peso (%)"] = df_csv["Importe"] / df_csv["Importe"].sum() * 100
            df_csv["Coste ejecución ajustado (€)"] = -round(df_csv["Peso (%)"] * coste_total_ejecucion / 100, 2)
            df_capitulos = df_csv[["Capítulo", "Peso (%)", "Coste ejecución ajustado (€)"]]
            st.success("✅ Archivo cargado correctamente")
        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {e}")

    st.markdown(f"### 📊 Capítulos y pesos aplicados (Coste total ejecución: {coste_total_ejecucion:,.2f} €)")
    st.dataframe(df_capitulos[["Capítulo", "Peso (%)", "Coste ejecución ajustado (€)"]], use_container_width=True)

    # === BLOQUE 3: Planificación por defecto basada en cronograma.csv
    fechas_inicio_relativas = {
        'Actuaciones previas': 0,
        'Demoliciones': 0,
        'Acondicionamiento del terreno': 0,
        'Cimentaciones': 2,
        'Estructuras': 4,
        'Fachadas y particiones': 8,
        'Carpintería, cerrajería, vidrios y protecciones solares': 10,
        'Remates y ayudas': 12,
        'Instalaciones': 10,
        'Aislamientos e impermeabilizaciones': 4,
        'Cubiertas': 6,
        'Revestimientos y trasdosados': 12,
        'Señalización y equipamiento': 15,
        'Urbanización interior de la parcela': 13,
        'Gestión de residuos': 0,
        'Control de calidad y ensayos': 14,
        'Seguridad y salud': 0
    }

    duraciones_defecto = {
        'Actuaciones previas': 3,
        'Demoliciones': 3,
        'Acondicionamiento del terreno': 3,
        'Cimentaciones': 4,
        'Estructuras': 4,
        'Fachadas y particiones': 4,
        'Carpintería, cerrajería, vidrios y protecciones solares': 5,
        'Remates y ayudas': 6,
        'Instalaciones': 6,
        'Aislamientos e impermeabilizaciones': 3,
        'Cubiertas': 2,
        'Revestimientos y trasdosados': 5,
        'Señalización y equipamiento': 2,
        'Urbanización interior de la parcela': 4,
        'Gestión de residuos': 17,
        'Control de calidad y ensayos': 5,
        'Seguridad y salud': 17
    }

    planificacion = []
    for i, row in df_capitulos.iterrows():
        capitulo = row["Capítulo"]
        offset_meses = fechas_inicio_relativas.get(capitulo, i)
        inicio = fecha_inicio_obra + relativedelta(months=offset_meses)
        duracion = duraciones_defecto.get(capitulo, 6)
        planificacion.append({
            "Capítulo": capitulo,
            "Inicio": inicio,
            "Duración (meses)": duracion
        })

    df_planificacion = pd.DataFrame(planificacion)

    # === BLOQUE 4: Tabla editable
    st.markdown("### 🗂️ Revisión y ajustes de planificación por capítulo")
    df_editable = st.data_editor(df_planificacion, num_rows="dynamic", use_container_width=True)

    # === BLOQUE 5: Gantt
    st.markdown("### 📆 Gráfico de Gantt")
    df_editable["Fin"] = pd.to_datetime(df_editable["Inicio"]) + df_editable["Duración (meses)"].apply(lambda m: relativedelta(months=int(m)))
    fig = px.timeline(
        df_editable,
        x_start="Inicio",
        x_end="Fin",
        y="Capítulo",
        color="Capítulo",
        title="Planificación de ejecución por capítulo"
    )
    fig.update_yaxes(autorange="reversed", categoryorder="array", categoryarray=list(df_capitulos["Capítulo"]))
    st.plotly_chart(fig, use_container_width=True)
        # === BLOQUE 6: Cronograma económico mensual ===
    st.markdown("### 📆 Cronograma económico mensual")

    # Coste total de ejecución ya calculado
    total_coste = superficie_total * coste_ejecucion_m2

    # Unimos planificación con pesos para obtener el % de cada capítulo
    df_merge = pd.merge(df_editable, df_capitulos[["Capítulo", "Peso (%)"]], on="Capítulo", how="left")
    df_merge["Coste total capítulo (€)"] = -round(df_merge["Peso (%)"] / 100 * total_coste, 2)

    # Generamos una lista de meses desde inicio de obra hasta último fin de capítulo
    fecha_inicio_global = df_merge["Inicio"].min()
    fecha_fin_global = df_merge.apply(lambda row: row["Inicio"] + relativedelta(months=int(row["Duración (meses)"])), axis=1).max()

    meses_totales = []
    fecha_cursor = fecha_inicio_global
    while fecha_cursor <= fecha_fin_global:
        meses_totales.append(fecha_cursor.strftime("%Y-%m"))
        fecha_cursor += relativedelta(months=1)

    # Inicializamos diccionario para el cronograma económico
    cronograma = {mes: {} for mes in meses_totales}

    for _, row in df_merge.iterrows():
        capitulo = row["Capítulo"]
        inicio = row["Inicio"]
        duracion = int(row["Duración (meses)"])
        coste_total = row["Coste total capítulo (€)"]
        coste_mensual = round(coste_total / duracion, 2)

        for i in range(duracion):
            fecha_mes = inicio + relativedelta(months=i)
            clave_mes = fecha_mes.strftime("%Y-%m")
            if capitulo not in cronograma[clave_mes]:
                cronograma[clave_mes][capitulo] = 0
            cronograma[clave_mes][capitulo] += coste_mensual

    # Convertimos en DataFrame
    df_cronograma = pd.DataFrame.from_dict(cronograma, orient="index").fillna(0)
    df_cronograma.index.name = "Mes"
    df_cronograma["Total mensual (€)"] = df_cronograma.sum(axis=1)

    st.dataframe(df_cronograma.round(2), use_container_width=True)

    # Gráfico de evolución de costes
    st.markdown("### 📉 Evolución mensual del coste de ejecución")
    fig_coste = px.bar(df_cronograma.reset_index(), x="Mes", y="Total mensual (€)", title="Coste mensual de ejecución")
    fig_coste.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_coste, use_container_width=True)

    # === BLOQUE 7: Coste del suelo ===
    df_suelo = pd.DataFrame(columns=["Mes", "Coste suelo (€)"])
    mes_inicio_comercial = fecha_inicio_comercializacion.strftime("%Y-%m")
    df_suelo = pd.DataFrame({
        "Mes": [mes_inicio_comercial],
        "Coste suelo (€)": [-coste_suelo]
    })

    # === BLOQUE 8: Honorarios técnicos ===
    importe_total_honorarios = -(porcentaje_honorarios / 100 * coste_total_ejecucion)
    mes_inicio_obra = fecha_inicio_obra.strftime("%Y-%m")
    mes_fin_obra = (fecha_inicio_obra + relativedelta(months=plazo_obra_meses)).strftime("%Y-%m")

    # 50% inicio, 20% repartido durante obra, 30% al final
    mensual_durante_obra = (importe_total_honorarios * 0.20) / plazo_obra_meses
    df_honorarios = []
    for i in range(plazo_obra_meses):
        fecha = fecha_inicio_obra + relativedelta(months=i)
        mes = fecha.strftime("%Y-%m")
        df_honorarios.append({
            "Mes": mes,
            "Honorarios técnicos (€)": mensual_durante_obra
        })
    df_honorarios.append({"Mes": mes_inicio_obra, "Honorarios técnicos (€)": importe_total_honorarios * 0.50})
    df_honorarios.append({"Mes": mes_fin_obra, "Honorarios técnicos (€)": importe_total_honorarios * 0.30})
    df_honorarios = pd.DataFrame(df_honorarios).groupby("Mes").sum().reset_index()

    # === BLOQUE 9: Gastos de administración ===
    total_admin = -(porcentaje_admin / 100 * coste_total_ejecucion)
    mes_entrega = (fecha_inicio_obra + relativedelta(months=plazo_obra_meses + 3)).strftime("%Y-%m")
    df_admin = pd.DataFrame({
        "Mes": [mes_inicio_obra, mes_entrega],
        "Gastos administración (€)": [total_admin * 0.5, total_admin * 0.5]
    })

    # === BLOQUE 10: Costes financieros ===
    if ventas_por_mes:
        lista_financieros = []
        for mes, unidades in ventas_por_mes.items():
            if unidades > 0:
                fecha = date.fromisoformat(mes + "-01") + relativedelta(months=1)
                mes_contrato = fecha.strftime("%Y-%m")
                lista_financieros.append({
                    "Mes": mes_contrato,
                    "Costes financieros (€)": -gastos_financieros * unidades
                })
        if lista_financieros:
            df_financieros = pd.DataFrame(lista_financieros)
            if "Mes" in df_financieros.columns:
                df_financieros = df_financieros.groupby("Mes", as_index=False).sum()
            else:
                df_financieros = pd.DataFrame(columns=["Mes", "Costes financieros (€)"])
        else:
            df_financieros = pd.DataFrame(columns=["Mes", "Costes financieros (€)"])
    else:
        df_financieros = pd.DataFrame(columns=["Mes", "Costes financieros (€)"])

    
    # === BLOQUE 11: Consolidación de todos los costes adicionales ===
    st.markdown("### 🧾 Consolidado de costes no ejecutivos")
    df_total_costes = pd.merge(df_suelo, df_honorarios, on="Mes", how="outer")
    df_total_costes = pd.merge(df_total_costes, df_admin, on="Mes", how="outer")
    df_total_costes = pd.merge(df_total_costes, df_financieros, on="Mes", how="outer")
    df_total_costes = df_total_costes.fillna(0)
    df_total_costes["Total otros costes (€)"] = df_total_costes.drop(columns=["Mes"]).sum(axis=1)
    st.dataframe(df_total_costes.round(2), use_container_width=True)

    # Mostrar solo las tablas auxiliares que contengan datos
    with st.expander("🔍 Desglose mensual por tipo de coste", expanded=False):
        if not df_suelo.empty:
            st.markdown("**📌 Coste del Suelo**")
            st.dataframe(df_suelo.round(2), use_container_width=True)

        if not df_honorarios.empty:
            st.markdown("**📐 Honorarios técnicos**")
            st.dataframe(df_honorarios.round(2), use_container_width=True)

        if not df_admin.empty:
            st.markdown("**🏛️ Gastos de administración**")
            st.dataframe(df_admin.round(2), use_container_width=True)

        if not df_financieros.empty:
            st.markdown("**💸 Costes financieros**")
            st.dataframe(df_financieros.round(2), use_container_width=True)

    # === BLOQUE 12: Gráfico de otros costes ===
    st.markdown("### 📊 Gráfico de otros costes por mes")
    fig_otros = px.bar(df_total_costes, x="Mes", y="Total otros costes (€)", title="Evolución mensual de otros costes")
    fig_otros.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_otros, use_container_width=True, key="gantt_costes")
    st.session_state["df_gantt"] = fig

    # Guardamos en sesión por si se usa en resumen
    st.session_state["df_costes_otros"] = df_total_costes


with tabs[3]:
    st.header("📊 Resumen General y Flujo de Caja")

    # Recuperar ingresos y costes desde sesión
    df_ingresos = df.copy()
    df_costes_ejec = df_cronograma.copy()
    df_otros_costes = st.session_state.get("df_costes_otros", pd.DataFrame(columns=["Mes"]))

    # Unificar las tablas por Mes
    df_merge = pd.merge(df_ingresos, df_costes_ejec[["Total mensual (€)"]], on="Mes", how="outer")
    df_merge = df_merge.rename(columns={"Total mensual (€)": "Coste ejecución (€)"})
    df_merge = pd.merge(df_merge, df_otros_costes, on="Mes", how="outer")
    df_merge = df_merge.fillna(0)

    # Calcular flujo de caja mensual total y acumulado
    df_merge["Flujo mensual total (€)"] = df_merge["Ingresos netos (€)"] + df_merge["Coste ejecución (€)"] + df_merge["Total otros costes (€)"]
    df_merge["Flujo acumulado (€)"] = df_merge["Flujo mensual total (€)"].cumsum()

    # Calcular flujo de cuenta especial intervenida
    df_merge["Ingreso cuenta especial (€)"] = (
        df_merge["Reserva (€)"] +
        df_merge["Contrato (€)"] +
        df_merge["Aplazado (€)"] 
    )
    df_merge["Gasto cuenta especial (€)"] = df_merge["Coste ejecución (€)"]
    df_merge["Flujo cuenta especial (€)"] = df_merge["Ingreso cuenta especial (€)"] + df_merge["Gasto cuenta especial (€)"]
    df_merge["Acumulado cuenta especial (€)"] = df_merge["Flujo cuenta especial (€)"].cumsum()

    st.subheader("📋 Tabla resumen mensual de flujo de caja")
    columnas_resumen = [
        "Mes",
        "Ingresos netos (€)",
        "Coste ejecución (€)",
        "Total otros costes (€)",
        "Flujo mensual total (€)",
        "Flujo acumulado (€)",
        "Ingreso cuenta especial (€)",
        "Gasto cuenta especial (€)",
        "Flujo cuenta especial (€)",
        "Acumulado cuenta especial (€)"
    ]
    df_resumen = df_merge[columnas_resumen].copy()

    # Aplicar formato condicional si acumulado cuenta especial es negativo
    def highlight_negativos(val):
        return "background-color: #fdd;" if val < 0 else ""

    # Detectar columnas numéricas
    columnas_numericas = df_resumen.select_dtypes(include=["number"]).columns

    # Mostrar tabla con estilo condicional solo en la columna del acumulado
    st.dataframe(
        df_resumen.style
            .applymap(highlight_negativos, subset=["Acumulado cuenta especial (€)"])
            .format({col: "{:,.2f}" for col in columnas_numericas}),
        use_container_width=True
)

    st.subheader("📈 Gráfico de flujo acumulado total")
    fig_flujo = px.line(df_merge, x="Mes", y="Flujo acumulado (€)", markers=True)
    fig_flujo.update_layout(title="Evolución acumulada del flujo de caja", yaxis_title="€ acumulado")
    st.plotly_chart(fig_flujo, use_container_width=True)

    st.subheader("🏦 Gráfico de cuenta especial intervenida")
    fig_cuenta = px.line(df_merge, x="Mes", y="Acumulado cuenta especial (€)", markers=True)
    fig_cuenta.update_layout(title="Evolución acumulada de la cuenta especial", yaxis_title="€ acumulado")
    st.plotly_chart(fig_cuenta, use_container_width=True)

    # Guardar tabla resumen en sesión para mostrarla en la pestaña de resumen
    st.session_state["df_flujo_final"] = df_resumen

with tabs[4]:
    st.header("📄 Resumen del Proyecto")

    # === BLOQUE 1: Mostrar todos los inputs generales
    st.markdown("### 📌 Inputs Generales")

    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown(f"**Nombre del proyecto:** {nombre_proyecto}")
        st.markdown(f"**Nº viviendas:** {num_viviendas}")
        st.markdown(f"**Superficie construida total:** {superficie_total:,.1f} m²")
        st.markdown(f"**Precio medio de venta:** {precio_medio_venta:,.2f} €")
        st.markdown(f"**Inicio obra:** {fecha_inicio_obra}")
        st.markdown(f"**Inicio comercialización:** {fecha_inicio_comercializacion}")
        st.markdown(f"**Plazo de obra (meses):** {plazo_obra_meses}")
    with col_der:
        st.markdown(f"**Coste suelo:** {coste_suelo:,.2f} €")
        st.markdown(f"**Coste ejecución por m²:** {coste_ejecucion_m2:,.2f} €")
        st.markdown(f"**% Comisiones venta:** {comisiones_venta:.2f} %")
        st.markdown(f"**% Honorarios técnicos:** {porcentaje_honorarios:.2f} %")
        st.markdown(f"**% Gastos administración:** {porcentaje_admin:.2f} %")
        st.markdown(f"**Gastos financieros por vivienda:** {gastos_financieros:,.2f} €")

    # === BLOQUE 2: Mostrar ventas por mes
    st.markdown("### 🏘️ Ventas por Mes")
    ventas_filtradas = {k: v for k, v in ventas_por_mes.items() if v > 0}
    df_ventas_resumen = pd.DataFrame(list(ventas_filtradas.items()), columns=["Mes", "Viviendas vendidas"])
    st.dataframe(df_ventas_resumen, use_container_width=True)

    # === BLOQUE 3: Botón de descarga CSV de inputs
    st.markdown("### 📥 Descargar todos los Inputs en CSV")
    import io

    buffer = io.StringIO()
    df_inputs_export = pd.DataFrame([
        ["Nombre del proyecto", nombre_proyecto],
        ["Nº viviendas", num_viviendas],
        ["Superficie construida total", superficie_total],
        ["Precio medio de venta", precio_medio_venta],
        ["Inicio obra", fecha_inicio_obra],
        ["Inicio comercialización", fecha_inicio_comercializacion],
        ["Plazo obra (meses)", plazo_obra_meses],
        ["Coste suelo", coste_suelo],
        ["Coste ejecución por m²", coste_ejecucion_m2],
        ["% Comisiones venta", comisiones_venta],
        ["% Honorarios técnicos", porcentaje_honorarios],
        ["% Gastos administración", porcentaje_admin],
        ["Gastos financieros por vivienda", gastos_financieros],
    ], columns=["Concepto", "Valor"])

    df_ventas_mes = pd.DataFrame.from_dict(ventas_filtradas, orient="index", columns=["Viviendas vendidas"])
    df_ventas_mes.index.name = "Mes"
    df_ventas_mes = df_ventas_mes.reset_index()

    df_final_csv = pd.concat([df_inputs_export, pd.DataFrame([["", ""]], columns=["Concepto", "Valor"]), df_ventas_mes.rename(columns={"Mes": "Concepto", "Viviendas vendidas": "Valor"})])

    df_final_csv.to_csv(buffer, index=False)
    st.download_button(
        label="📥 Descargar CSV de Inputs y Ventas",
        data=buffer.getvalue(),
        file_name="inputs_ventas.csv",
        mime="text/csv"
    )

    # === BLOQUE 4: Mostrar resumen del flujo de caja si está disponible
    st.markdown("### 📊 Tabla resumen del flujo de caja")

    if "df_flujo_final" in st.session_state:
        def highlight_negativos(val):
            return "background-color: #fdd;" if isinstance(val, (int, float)) and val < 0 else ""

        columnas_numericas = st.session_state["df_flujo_final"].select_dtypes(include=["number"]).columns

        st.dataframe(
            st.session_state["df_flujo_final"].style
                .applymap(highlight_negativos, subset=["Acumulado cuenta especial (€)"])
                .format({col: "{:,.2f}" for col in columnas_numericas}),
            use_container_width=True
        )
    else:
        st.warning("⚠️ Aún no se ha generado el flujo de caja final.")
    
    # === BLOQUE 5: Gráfico de Gantt desde la pestaña de Costes ===
    st.markdown("### 📆 Cronograma de ejecución por capítulo")

    if "df_gantt" in st.session_state:
        fig_gantt = st.session_state["df_gantt"]
        st.plotly_chart(fig_gantt, use_container_width=True, key="gantt_resumen")
    else:
        st.info("ℹ️ El cronograma de ejecución todavía no se ha generado.")