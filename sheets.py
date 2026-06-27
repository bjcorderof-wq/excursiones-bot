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