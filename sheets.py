import os
import json
import gspread

from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Modo local
if os.path.exists("credentials.json"):

    gc = gspread.service_account(
        filename="credentials.json"
    )

# Modo Railway
else:

    credentials_json = os.getenv(
        "GOOGLE_CREDENTIALS"
    )

    if not credentials_json:
        raise Exception(
            "No existe la variable GOOGLE_CREDENTIALS"
        )

    credentials_dict = json.loads(
        credentials_json
    )

    credentials = Credentials.from_service_account_info(
        credentials_dict,
        scopes=SCOPES
    )

    gc = gspread.authorize(credentials)

# Abrir spreadsheet
spreadsheet = gc.open("Excursiones Meza")

# Hojas
destinos = spreadsheet.worksheet("Destinos")
reservas = spreadsheet.worksheet("Reservas")
pagos = spreadsheet.worksheet("Pagos")
vendedores = spreadsheet.worksheet("Vendedores")
itinerario = spreadsheet.worksheet("Itinerario")


def obtener_destinos():
    return destinos.get_all_records()


def obtener_reservas():
    return reservas.get_all_records()


def obtener_vendedores():
    return vendedores.get_all_records()


def obtener_pagos():
    return pagos.get_all_records()


def obtener_itinerario():
    return itinerario.get_all_records()


def obtener_itinerario_por_viaje(id_viaje: str):
    datos = itinerario.get_all_records()

    resultado = [
        fila for fila in datos
        if str(fila.get("ID_Viaje", "")).strip().upper() == id_viaje.strip().upper()
    ]

    return resultado


###############

def normalizar_texto(texto):
    return str(texto).strip().lower()


def buscar_viaje_por_texto(consulta: str):
    consulta_norm = normalizar_texto(consulta)
    viajes = destinos.get_all_records()

    for viaje in viajes:
        nombre = normalizar_texto(viaje.get("Nombre", ""))
        destino = normalizar_texto(viaje.get("Destino", ""))
        id_viaje = normalizar_texto(viaje.get("ID_Viaje", ""))

        if (
            consulta_norm in nombre
            or consulta_norm in destino
            or consulta_norm in id_viaje
            or nombre in consulta_norm
            or destino in consulta_norm
        ):
            return viaje

    return None


def obtener_itinerario_por_consulta(consulta: str):
    viaje = buscar_viaje_por_texto(consulta)

    if not viaje:
        return {
            "encontrado": False,
            "mensaje": "No se encontró un viaje relacionado con la consulta.",
            "consulta": consulta,
            "viaje": None,
            "itinerario": []
        }

    id_viaje = viaje.get("ID_Viaje")
    datos_itinerario = itinerario.get_all_records()

    resultado = [
        fila for fila in datos_itinerario
        if normalizar_texto(fila.get("ID_Viaje", "")) == normalizar_texto(id_viaje)
    ]

    return {
        "encontrado": True,
        "viaje": viaje,
        "itinerario": resultado
    }