import os
import pickle
from datetime import datetime
import streamlit as st

# Carpeta donde se guardan las versiones
CARPETA_VERSIONES = "versiones"

# Asegurar que existe
os.makedirs(CARPETA_VERSIONES, exist_ok=True)

def guardar_version(nombre: str):
    if not nombre:
        raise ValueError("El nombre de la versión no puede estar vacío.")

    nombre_archivo = f"{nombre}.pkl"
    ruta = os.path.join(CARPETA_VERSIONES, nombre_archivo)

    datos = {
        "session_state": dict(st.session_state),
        "fecha": datetime.now()
    }

    with open(ruta, "wb") as f:
        pickle.dump(datos, f)

def cargar_version(nombre: str):
    nombre_archivo = f"{nombre}.pkl"
    ruta = os.path.join(CARPETA_VERSIONES, nombre_archivo)

    if not os.path.exists(ruta):
        raise FileNotFoundError(f"La versión '{nombre}' no existe.")

    with open(ruta, "rb") as f:
        datos = pickle.load(f)

    st.session_state.clear()
    for k, v in datos["session_state"].items():
        st.session_state[k] = v

def listar_versiones():
    versiones = []
    for archivo in os.listdir(CARPETA_VERSIONES):
        if archivo.endswith(".pkl"):
            versiones.append(archivo.replace(".pkl", ""))
    return sorted(versiones)