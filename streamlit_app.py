import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd
import plotly.express as px
import time
import plotly.graph_objects as go
import streamlit as st
from versionado import guardar_version, cargar_version, listar_versiones

# Pantalla de bienvenida con logotipo
if "pantalla_carga" not in st.session_state:
    st.session_state.pantalla_carga = True

if st.session_state.pantalla_carga:
    st.image("img/icono_automator.png", width=200)
    st.markdown("<h1 style='text-align: center;'>Promoción Inmobiliaria</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Cargando aplicación... por favor espera</p>", unsafe_allow_html=True)
    with st.spinner("Inicializando módulos..."):
        time.sleep(2.5)
    if st.button("Entrar"):
        st.session_state.pantalla_carga = False
        st.rerun()
    st.stop()

st.set_page_config(page_title="Flujo de Caja – Promoción Inmobiliaria", layout="wide")

# === Nombre del Proyecto ===
nombre_proyecto = st.text_input("🏗️ Nombre del Proyecto", value="Promoción Residencial")
st.title(f"🧮 Modelo de Flujo de Caja – {nombre_proyecto}")

# === Panel lateral auxiliar para guardar/cargar versión ===
with st.expander("⚙️ Guardar / Cargar versión", expanded=False):
    nombre_nueva_version = st.text_input("📝 Nombre para nueva versión", key="nombre_nueva_version")

    if st.button("💾 Guardar versión actual"):
        try:
            guardar_version(nombre_nueva_version)
            st.success(f"✅ Versión '{nombre_nueva_version}' guardada correctamente.")
        except Exception as e:
            st.error(f"❌ Error al guardar la versión: {e}")

    versiones_disponibles = listar_versiones()
    seleccion = st.selectbox("📂 Versión guardada:", [""] + versiones_disponibles, key="seleccion_version")

    if seleccion and st.button("🔄 Cargar versión seleccionada"):
        try:
            cargar_version(seleccion)
            st.success(f"✅ Versión '{seleccion}' cargada correctamente.")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error al cargar la versión: {e}")

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

    st.markdown("### 📋 Cargar viviendas desde tabla Excel")
    fecha_fin_obra = fecha_inicio_obra + relativedelta(months=plazo_obra_meses)
    fecha_entrega_viviendas = fecha_fin_obra + relativedelta(months=3)
    
    with st.expander("📥 Pegar tabla de viviendas desde Excel (Código, Precio, Fecha venta, Fecha escrituración)", expanded=False):
        texto_pegado = st.text_area("📋 Copia y pega aquí la tabla desde Excel (incluyendo cabecera)", height=200)

        if texto_pegado.strip():
            try:
                from io import StringIO

                # Convertimos el texto pegado en un DataFrame
                data = StringIO(texto_pegado)
                df_viviendas = pd.read_csv(data, sep="\t")

                # Normalizar nombres de columnas (por si llevan espacios)
                df_viviendas.columns = [c.strip().lower() for c in df_viviendas.columns]

                # Detectar columnas esperadas (flexible a variaciones)
                col_codigo = next((c for c in df_viviendas.columns if "código" in c or "codigo" in c or "id" == c), None)
                col_precio = next((c for c in df_viviendas.columns if "precio" in c), None)
                col_venta = next((c for c in df_viviendas.columns if "venta" in c), None)
                col_escritura = next((c for c in df_viviendas.columns if "escritu" in c), None)

                if not col_codigo or not col_precio or not col_venta:
                    st.error("❌ La tabla debe tener al menos las columnas: Código, Precio y Fecha venta.")
                else:
                    # Renombrar para trabajar cómodamente
                    df_viviendas = df_viviendas.rename(columns={
                        col_codigo: "Código",
                        col_precio: "Precio",
                        col_venta: "Fecha venta",
                        col_escritura: "Fecha escrituración" if col_escritura else None
                    })

                    # Conversión robusta de fechas (soporta strings y datetime.date)
                    for col in ["Fecha venta", "Fecha escrituración"]:
                        if col in df_viviendas.columns:
                            df_viviendas[col] = df_viviendas[col].apply(lambda x: pd.to_datetime(str(x), dayfirst=True, errors='coerce') if pd.notna(x) else pd.NaT)
                        else:
                            df_viviendas[col] = pd.NaT

                    # Asignar fecha por defecto si no hay escrituración
                    df_viviendas["Fecha escrituración"] = df_viviendas["Fecha escrituración"].fillna(fecha_entrega_viviendas)

                    # Mostrar resumen
                    st.success(f"✅ {len(df_viviendas)} viviendas cargadas correctamente")
                    st.dataframe(df_viviendas, use_container_width=True)

                    # Guardar para siguientes pestañas
                    st.session_state["df_viviendas"] = df_viviendas

                    # Actualizar inputs calculados
                    st.session_state["num_viviendas"] = len(df_viviendas)
                    st.session_state["precio_medio_venta"] = df_viviendas["Precio"].mean()

            except Exception as e:
                st.error(f"❌ Error al procesar la tabla: {e}")

    # Inputs principales con valores que pueden ser sobreescritos desde la tabla pegada
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        num_viviendas = st.number_input(
            "Nº de viviendas",
            min_value=1,
            value=st.session_state.get("num_viviendas", 20),
            key="num_viviendas"
        )
        superficie_total = st.number_input("Superficie construida total (m²)", min_value=0.0, value=2000.0)
        precio_medio_venta = st.number_input(
            "Precio medio de venta por vivienda (€)",
            min_value=0.0,
            value=st.session_state.get("precio_medio_venta", 350000.0),
            key="precio_medio_venta"
        )

    with col_b:
        coste_suelo = st.number_input("Coste del Suelo (€)", min_value=0.0, value=300000.0)
        coste_ejecucion_m2 = st.number_input("Coste ejecución por m²", min_value=0.0, value=1600.0)
        comisiones_venta = st.number_input("Comisiones (% sobre precio sin IVA)", min_value=0.0, max_value=100.0, value=15.0)

    with col_c:
        porcentaje_honorarios = st.number_input("% Honorarios técnicos", min_value=0.0, max_value=100.0, value=5.0)
        porcentaje_admin = st.number_input("% Gastos administración", min_value=0.0, max_value=100.0, value=4.0)
        gastos_financieros = st.number_input("Gastos financieros por vivienda (€)", min_value=0.0, value=5000.0)

    st.header("📌 Parámetros Adicionales")
    col_iva1, col_iva2, col_iva3 = st.columns(3)
    with col_iva1:
        iva_venta = st.number_input("IVA en ventas (%)", min_value=0.0, max_value=100.0, value=10.0)
    with col_iva2:
        iva_ejecucion = st.number_input("IVA en costes de ejecución (%)", min_value=0.0, max_value=100.0, value=0.0)
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
        reserva_fija = st.number_input("Reserva (€ por vivienda)", min_value=0.0, value=10000.0)
    with col_con:
        pct_contrato = st.number_input("Contrato (%) sobre precio con IVA", min_value=0.0, max_value=100.0, value=25.0)
    with col_apl:
        pct_aplazado = st.number_input("Aplazado (%) sobre precio con IVA", min_value=0.0, max_value=100.0, value=25.0)
    with col_esc:
        st.text_input("Escritura (%)", value="Resto", disabled=True)

    st.subheader("📆 Calendario de proyecto")
    fecha_fin_obra = fecha_inicio_obra + relativedelta(months=plazo_obra_meses)
    fecha_entrega_viviendas = fecha_fin_obra + relativedelta(months=3)
    st.caption(f"🏗️ Fin de obra estimado: **{fecha_fin_obra.strftime('%Y-%m-%d')}**")
    st.caption(f"🏁 Entrega prevista: **{fecha_entrega_viviendas.strftime('%Y-%m-%d')}**")

    st.header("🏘️ Cronograma Real de Ingresos y Comisiones")
    df_viviendas = st.session_state.get("df_viviendas")

    if df_viviendas is not None:
        df_viviendas["Fecha venta"] = pd.to_datetime(df_viviendas["Fecha venta"], dayfirst=True, errors="coerce")
        df_viviendas["Fecha escrituración"] = pd.to_datetime(df_viviendas["Fecha escrituración"], dayfirst=True, errors="coerce")

        ingresos_dict = {}

        fecha_min = df_viviendas["Fecha venta"].min().date()
        fecha_max = df_viviendas["Fecha escrituración"].fillna(pd.Timestamp(fecha_entrega_viviendas)).dt.date.max() + relativedelta(months=3)

        fecha_iter = fecha_min
        while fecha_iter <= fecha_max:
            key = fecha_iter.strftime("%Y-%m")
            ingresos_dict[key] = {
                "Reserva (€)": 0,
                "Contrato (€)": 0,
                "Aplazado (€)": 0,
                "Escritura (€)": 0,
                "Comisiones (€)": 0,
            }
            fecha_iter += relativedelta(months=1)

        for _, row in df_viviendas.iterrows():
            precio = row["Precio"]
            precio_con_iva = precio * (1 + iva_venta / 100)
            fecha_venta = row["Fecha venta"].date()
            fecha_escritura = row["Fecha escrituración"].date() if pd.notnull(row["Fecha escrituración"]) else None
            terminada = fecha_venta >= fecha_entrega_viviendas

            restante = precio_con_iva - reserva_fija
            importe_contrato = precio_con_iva * pct_contrato / 100
            importe_aplazado = precio_con_iva * pct_aplazado / 100
            importe_escritura = restante - importe_contrato - importe_aplazado

            f_reserva = fecha_venta
            f_contrato = f_reserva + relativedelta(months=1)
            f_aplazado = f_contrato + relativedelta(months=3)

            if fecha_escritura:
                if not terminada:
                    f_escritura = fecha_escritura
                else:
                    f_escritura = max(fecha_entrega_viviendas, fecha_venta + relativedelta(months=1))
            else:
                if not terminada:
                    f_escritura = fecha_entrega_viviendas
                else:
                    f_escritura = max(fecha_entrega_viviendas, fecha_venta + relativedelta(months=1))

            ingresos_dict[f_reserva.strftime("%Y-%m")]["Reserva (€)"] += reserva_fija
            ingresos_dict[f_contrato.strftime("%Y-%m")]["Contrato (€)"] += importe_contrato
            ingresos_dict[f_aplazado.strftime("%Y-%m")]["Aplazado (€)"] += importe_aplazado
            ingresos_dict[f_escritura.strftime("%Y-%m")]["Escritura (€)"] += importe_escritura

        for mes in ingresos_dict:
            total_con_iva = sum([
                ingresos_dict[mes]["Reserva (€)"],
                ingresos_dict[mes]["Contrato (€)"],
                ingresos_dict[mes]["Aplazado (€)"],
                ingresos_dict[mes]["Escritura (€)"],
            ])
            total_sin_iva = total_con_iva / (1 + iva_venta / 100)
            comision = total_sin_iva * (comisiones_venta / 100) * (1 + iva_otros / 100)
            ingresos_dict[mes]["Comisiones (€)"] = -comision

        resumen = {
            "Mes": [],
            "Reserva (€)": [],
            "Contrato (€)": [],
            "Aplazado (€)": [],
            "Escritura (€)": [],
            "Comisiones (€)": [],
            "Total ingresos (€)": [],
            "Ingresos netos (€)": [],
        }

        for mes in sorted(ingresos_dict):
            reserva = ingresos_dict[mes]["Reserva (€)"]
            contrato = ingresos_dict[mes]["Contrato (€)"]
            aplazado = ingresos_dict[mes]["Aplazado (€)"]
            escritura = ingresos_dict[mes]["Escritura (€)"]
            comisiones = ingresos_dict[mes]["Comisiones (€)"]
            total = reserva + contrato + aplazado + escritura
            neto = total + comisiones

            resumen["Mes"].append(mes)
            resumen["Reserva (€)"].append(reserva)
            resumen["Contrato (€)"].append(contrato)
            resumen["Aplazado (€)"].append(aplazado)
            resumen["Escritura (€)"].append(escritura)
            resumen["Comisiones (€)"].append(comisiones)
            resumen["Total ingresos (€)"].append(total)
            resumen["Ingresos netos (€)"].append(neto)

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

        st.session_state["df"] = df

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

    # 🔄 Guardar para la pestaña de resumen
    st.session_state["fig_gantt"] = fig
    
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

    # Gráfico de evolución acumulada del coste de ejecución (sin picos)
    st.markdown("### 📉 Evolución acumulada del coste de ejecución")

    # Crear columna acumulada
    df_cronograma_acumulado = df_cronograma.copy()
    df_cronograma_acumulado["Total acumulado (€)"] = df_cronograma_acumulado["Total mensual (€)"].cumsum()

    # Crear gráfico simple
    fig_coste = px.line(
        df_cronograma_acumulado.reset_index(),
        x="Mes",
        y="Total acumulado (€)",
        title="Coste acumulado de ejecución"
    )
    fig_coste.update_layout(xaxis_tickangle=-45)

    # Mostrar
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
    df_viviendas = st.session_state.get("df_viviendas")
    if df_viviendas is not None:
        lista_financieros = []
        for _, row in df_viviendas.iterrows():
            fecha_venta = row["Fecha venta"]
            if pd.notnull(fecha_venta):
                mes_contrato = (fecha_venta + relativedelta(months=1)).strftime("%Y-%m")
                lista_financieros.append({
                    "Mes": mes_contrato,
                    "Costes financieros (€)": -gastos_financieros
                })
        if lista_financieros:
            df_financieros = pd.DataFrame(lista_financieros)
            df_financieros = df_financieros.groupby("Mes", as_index=False).sum()
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

    # === BLOQUE 12: Gráfico de otros costes acumulados + barra mensual ===
    st.markdown("### 📊 Evolución de otros costes")

    # Crear columna acumulada
    df_total_costes["Total otros costes acumulado (€)"] = df_total_costes["Total otros costes (€)"].cumsum()

    # Crear figura combinada: barra mensual + línea acumulada
    fig_otros = go.Figure()

    # Barra: costes mensuales
    fig_otros.add_bar(
        x=df_total_costes["Mes"],
        y=df_total_costes["Total otros costes (€)"],
        name="Coste mensual",
        marker_color="steelblue"
    )

    # Línea: costes acumulados
    fig_otros.add_trace(
        go.Scatter(
            x=df_total_costes["Mes"],
            y=df_total_costes["Total otros costes acumulado (€)"],
            name="Acumulado",
            mode="lines+markers",
            line=dict(color="firebrick", width=3)
        )
    )

    # Ajustes estéticos
    fig_otros.update_layout(
        title="Otros costes: mensual y acumulado",
        xaxis_title="Mes",
        yaxis_title="€",
        xaxis_tickangle=-45,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Mostrar
    st.plotly_chart(fig_otros, use_container_width=True, key="gantt_costes")

    # Guardamos en sesión por si se usa en resumen
    st.session_state["df_costes_otros"] = df_total_costes


with tabs[3]:
    st.header("📊 Resumen General y Flujo de Caja")

    # Recuperar ingresos y costes desde sesión
    if "df" in st.session_state:
        df_ingresos = st.session_state["df"].copy()
    else:
        st.warning("⚠️ Aún no se han definido los ingresos. Por favor, ve primero a la pestaña 'Ingresos y Comisiones'.")
        st.stop()
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

    # Calcular acumulado y déficit mensual de cuenta especial
    acumulado = []
    saldo = 0
    deficits = []

    for flujo in df_merge["Flujo cuenta especial (€)"]:
        saldo += flujo
        if saldo < 0:
            deficits.append(saldo)  # negativo
            acumulado.append(0)
            saldo = 0
        else:
            deficits.append(0)
            acumulado.append(saldo)

    df_merge["Acumulado cuenta especial (€)"] = acumulado
    df_merge["Déficit cuenta especial (€)"] = deficits

    # Mostrar tabla resumen mensual de flujo de caja
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
        "Acumulado cuenta especial (€)",
        "Déficit cuenta especial (€)"
    ]
    df_resumen = df_merge[columnas_resumen].copy()

    def highlight_negativos(val):
        return "background-color: #fdd;" if isinstance(val, (int, float)) and val < 0 else ""

    columnas_numericas = df_resumen.select_dtypes(include=["number"]).columns

    st.dataframe(
        df_resumen.style
            .applymap(highlight_negativos, subset=["Déficit cuenta especial (€)"])
            .format({col: "{:,.2f}" for col in columnas_numericas}),
        use_container_width=True
    )

    # Gráfico flujo acumulado total
    st.subheader("📈 Gráfico de flujo acumulado total")
    fig_flujo = px.line(df_merge, x="Mes", y="Flujo acumulado (€)", markers=True)
    fig_flujo.update_layout(title="Evolución acumulada del flujo de caja", yaxis_title="€ acumulado")
    st.plotly_chart(fig_flujo, use_container_width=True)

    # Gráfico cuenta especial intervenida
    st.subheader("🏦 Gráfico de cuenta especial intervenida")
    fig_cuenta = px.line(df_merge, x="Mes", y="Acumulado cuenta especial (€)", markers=True)
    fig_cuenta.update_layout(title="Evolución acumulada de la cuenta especial", yaxis_title="€ acumulado")
    st.plotly_chart(fig_cuenta, use_container_width=True)

    # Tabla de necesidades de financiación
    st.subheader("💸 Necesidades de financiación mensuales")

    columnas_necesidades = [
        "Mes",
        "Coste suelo (€)",
        "Honorarios técnicos (€)",
        "Gastos administración (€)",
        "Costes financieros (€)",
        "Comisiones (€)",
        "Déficit cuenta especial (€)"
    ]
    for col in columnas_necesidades[1:]:
        if col not in df_merge.columns:
            df_merge[col] = 0

    df_merge["Total necesidades financiación (€)"] = df_merge[
        columnas_necesidades[1:]
    ].sum(axis=1)

    df_necesidades = df_merge[["Mes"] + columnas_necesidades[1:] + ["Total necesidades financiación (€)"]].copy()

    def resaltar_total(row):
        if row["Total necesidades financiación (€)"] != 0:
            return ["background-color: #ffe6e6"] * len(row)
        return [""] * len(row)

    columnas_num_necesidades = df_necesidades.select_dtypes(include=["number"]).columns

    st.dataframe(
        df_necesidades.style
            .apply(resaltar_total, axis=1)
            .format({col: "{:,.2f}" for col in columnas_num_necesidades}),
        use_container_width=True
    )

    st.session_state["df_flujo_final"] = df_resumen
    st.session_state["df_necesidades_financiacion"] = df_necesidades

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

    # === BLOQUE 2: Mostrar ventas por Mes
    st.markdown("### 🏘️ Ventas por Mes")

    df_viviendas = st.session_state.get("df_viviendas")

    if df_viviendas is not None and not df_viviendas.empty:
        df_ventas_resumen = (
            df_viviendas.copy()
            .assign(Mes=lambda df: df["Fecha venta"].dt.to_period("M").astype(str))
            .groupby("Mes")
            .size()
            .reset_index(name="Viviendas vendidas")
        )
        st.dataframe(df_ventas_resumen, use_container_width=True)
    else:
        st.info("ℹ️ No hay datos de ventas disponibles.")

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

    df_ventas_mes = df_ventas_resumen.copy()
    df_ventas_mes.columns = ["Mes", "Viviendas vendidas"]

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
                .applymap(highlight_negativos, subset=["Flujo acumulado (€)"])
                .format({col: "{:,.2f}" for col in columnas_numericas}),
            use_container_width=True
        )
    else:
        st.warning("⚠️ Aún no se ha generado el flujo de caja final.")
    
    # === BLOQUE 5: Gráfico de Gantt desde la pestaña de Costes ===
    st.markdown("### 📆 Cronograma de ejecución por capítulo")

    if "fig_gantt" in st.session_state:
        fig_gantt = st.session_state["fig_gantt"]
        st.plotly_chart(fig_gantt, use_container_width=True, key="gantt_resumen")
    else:
        st.info("ℹ️ El cronograma de ejecución todavía no se ha generado.")
