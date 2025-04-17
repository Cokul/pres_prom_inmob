import os
import pickle
import glob
from datetime import datetime
import streamlit as st
from streamlit.errors import StreamlitValueAssignmentNotAllowedError

# Carpeta base donde se almacenan las versiones
CARPETA_BASE = os.path.join(os.getcwd(), "versiones")


def ruta_proyecto(nombre_proyecto: str = "default") -> str:
    """
    Devuelve la ruta de la carpeta de versiones para un proyecto dado, creando
    la carpeta base y la carpeta del proyecto si no existen.
    """
    os.makedirs(CARPETA_BASE, exist_ok=True)
    proyecto_dir = os.path.join(CARPETA_BASE, nombre_proyecto)
    os.makedirs(proyecto_dir, exist_ok=True)
    return proyecto_dir


def guardar_version(nombre_version: str, nombre_proyecto: str = "default") -> None:
    """
    Guarda el estado actual de st.session_state en un archivo pickle.
    El nombre del archivo será '<nombre_version>.pkl' dentro de la carpeta del proyecto.
    """
    if not nombre_version or not nombre_version.strip():
        raise ValueError("Debe indicar un nombre válido para la versión.")
    proyecto_dir = ruta_proyecto(nombre_proyecto)
    ruta_archivo = os.path.join(proyecto_dir, f"{nombre_version}.pkl")
    datos = {
        "fecha": datetime.now(),
        "st_session": dict(st.session_state)
    }
    with open(ruta_archivo, "wb") as f:
        pickle.dump(datos, f)


def cargar_version(nombre_version: str, nombre_proyecto: str = "default") -> None:
    """
    Carga una versión guardada restaurando valores en st.session_state.
    Evita modificar valores bloqueados por Streamlit (botones, widgets, etc.).
    """
    if not nombre_version or not nombre_version.strip():
        raise ValueError("Debe indicar el nombre de la versión a cargar.")
    proyecto_dir = ruta_proyecto(nombre_proyecto)
    ruta_archivo = os.path.join(proyecto_dir, f"{nombre_version}.pkl")
    if not os.path.isfile(ruta_archivo):
        raise FileNotFoundError(f"La versión '{nombre_version}' no existe.")
    with open(ruta_archivo, "rb") as f:
        datos = pickle.load(f)
    session_data = datos.get("st_session", {})
    for llave, valor in session_data.items():
        # No sobreescribir flags booleanos de botones/widgets
        if isinstance(valor, bool):
            continue
        try:
            st.session_state[llave] = valor
        except StreamlitValueAssignmentNotAllowedError:
            continue
        except Exception:
            continue


def listar_versiones(nombre_proyecto: str = "default"):
    """
    Devuelve lista de versiones con 'nombre' y 'fecha', ordenadas de más reciente a más antigua.
    """
    proyecto_dir = ruta_proyecto(nombre_proyecto)
    patron = os.path.join(proyecto_dir, "*.pkl")
    archivos = glob.glob(patron)
    versiones = []
    archivos.sort(key=os.path.getmtime, reverse=True)
    for ruta_archivo in archivos:
        nombre = os.path.splitext(os.path.basename(ruta_archivo))[0]
        ts = os.path.getmtime(ruta_archivo)
        fecha = datetime.fromtimestamp(ts)
        versiones.append({"nombre": nombre, "fecha": fecha})
    return versiones


def duplicar_version(origen: str, nuevo_nombre: str, nombre_proyecto: str = "default") -> None:
    """
    Duplica una versión existente con un nuevo nombre.
    """
    if not origen or not nuevo_nombre or not nuevo_nombre.strip():
        raise ValueError("Debe indicar un origen y un nuevo nombre válidos.")
    proyecto_dir = ruta_proyecto(nombre_proyecto)
    ruta_origen = os.path.join(proyecto_dir, f"{origen}.pkl")
    if not os.path.isfile(ruta_origen):
        raise FileNotFoundError(f"La versión origen '{origen}' no existe.")
    ruta_destino = os.path.join(proyecto_dir, f"{nuevo_nombre}.pkl")
    with open(ruta_origen, "rb") as f:
        datos = pickle.load(f)
    datos["fecha"] = datetime.now()
    with open(ruta_destino, "wb") as f:
        pickle.dump(datos, f)


def eliminar_version(nombre_version: str, nombre_proyecto: str = "default") -> None:
    """
    Elimina una versión guardada.
    """
    if not nombre_version or not nombre_version.strip():
        raise ValueError("Debe indicar el nombre de la versión a eliminar.")
    proyecto_dir = ruta_proyecto(nombre_proyecto)
    ruta_archivo = os.path.join(proyecto_dir, f"{nombre_version}.pkl")
    if os.path.isfile(ruta_archivo):
        os.remove(ruta_archivo)
