import os
import json
import gspread

from google.oauth2.service_account import Credentials
from datetime import datetime

#%%

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


#%%

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


#%%


def generar_siguiente_id(hoja, prefijo):
    registros = hoja.get_all_records()

    if not registros:
        return f"{prefijo}001"

    ids = []
    primera_columna = hoja.row_values(1)[0]

    for fila in registros:
        valor = str(fila.get(primera_columna, "")).replace(prefijo, "")
        if valor.isdigit():
            ids.append(int(valor))

    siguiente = max(ids) + 1 if ids else 1
    return f"{prefijo}{siguiente:03d}"


def actualizar_cupo_disponible(id_viaje, cantidad_personas):
    datos = destinos.get_all_records()
    valores = destinos.get_all_values()
    encabezados = valores[0]

    col_id = encabezados.index("ID_Viaje") + 1
    col_cupo = encabezados.index("Cupo_Disponible") + 1

    for i, fila in enumerate(datos, start=2):
        if str(fila.get("ID_Viaje")).strip().upper() == str(id_viaje).strip().upper():
            cupo_actual = int(fila.get("Cupo_Disponible", 0))

            if cupo_actual < cantidad_personas:
                return {
                    "ok": False,
                    "mensaje": "No hay cupos suficientes",
                    "cupo_disponible": cupo_actual
                }

            nuevo_cupo = cupo_actual - cantidad_personas
            destinos.update_cell(i, col_cupo, nuevo_cupo)

            return {
                "ok": True,
                "cupo_anterior": cupo_actual,
                "cupo_nuevo": nuevo_cupo
            }

    return {
        "ok": False,
        "mensaje": "No se encontró el viaje"
    }


def agregar_fila_por_encabezados(hoja, datos):
    encabezados = hoja.row_values(1)
    fila = [datos.get(col, "") for col in encabezados]
    hoja.append_row(fila)


def registrar_reserva_pago(consulta, cliente, vendedor, cantidad_personas, monto_abono, comentario=""):
    viaje = buscar_viaje_por_texto(consulta)

    if not viaje:
        return {
            "ok": False,
            "mensaje": "No se encontró un viaje relacionado con la consulta."
        }

    id_viaje = viaje.get("ID_Viaje")
    nombre_viaje = viaje.get("Nombre")
    precio = float(viaje.get("Precio_USD", 0))

    monto_total = precio * cantidad_personas
    saldo_pendiente = monto_total - monto_abono

    resultado_cupo = actualizar_cupo_disponible(id_viaje, cantidad_personas)

    if not resultado_cupo.get("ok"):
        return resultado_cupo

    fecha_actual = datetime.now().strftime("%d/%m/%Y")

    id_reserva = generar_siguiente_id(reservas, "R")

    estado = "Reserva con abono" if monto_abono > 0 else "Pendiente de pago"

    agregar_fila_por_encabezados(reservas, {
        "ID_Reserva": id_reserva,
        "Nombre": nombre_viaje,
        "Vendedor": vendedor,
        "Cliente": cliente,
        "Cantidad_Personas": cantidad_personas,
        "Fecha_Reserva": fecha_actual,
        "Estado": estado,
        "Monto_Total": monto_total,
        "Saldo_Pendiente": saldo_pendiente
    })

    id_pago = None

    if monto_abono > 0:
        id_pago = generar_siguiente_id(pagos, "P")

        agregar_fila_por_encabezados(pagos, {
            "ID_Pago": id_pago,
            "ID_Reserva": id_reserva,
            "Cliente": cliente,
            "Monto": monto_abono,
            "Fecha": fecha_actual,
            "Comentario": comentario or f"Abono reserva {id_reserva} - {nombre_viaje}"
        })

    return {
        "ok": True,
        "mensaje": "Reserva y pago registrados correctamente",
        "reserva": {
            "id_reserva": id_reserva,
            "cliente": cliente,
            "viaje": nombre_viaje,
            "cantidad_personas": cantidad_personas,
            "monto_total": monto_total,
            "saldo_pendiente": saldo_pendiente,
            "estado": estado
        },
        "pago": {
            "id_pago": id_pago,
            "monto_abono": monto_abono
        },
        "cupos": resultado_cupo
    }

#%%
def registrar_abono_reserva(cliente, monto_abono, comentario=""):
    reservas_data = reservas.get_all_records()
    reservas_values = reservas.get_all_values()
    encabezados_reservas = reservas_values[0]

    col_saldo = encabezados_reservas.index("Saldo_Pendiente") + 1
    col_id_reserva = encabezados_reservas.index("ID_Reserva") + 1

    reserva_encontrada = None
    fila_reserva = None

    for i, fila in enumerate(reservas_data, start=2):
        if str(fila.get("Cliente", "")).strip().lower() == str(cliente).strip().lower():
            reserva_encontrada = fila
            fila_reserva = i
            break

    if not reserva_encontrada:
        return {
            "ok": False,
            "mensaje": "No se encontró una reserva para este cliente."
        }

    id_reserva = reserva_encontrada.get("ID_Reserva")
    nombre_viaje = reserva_encontrada.get("Nombre")
    saldo_actual = float(reserva_encontrada.get("Saldo_Pendiente", 0))

    nuevo_saldo = saldo_actual - monto_abono

    if nuevo_saldo < 0:
        nuevo_saldo = 0

    reservas.update_cell(fila_reserva, col_saldo, nuevo_saldo)

    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    id_pago = generar_siguiente_id(pagos, "P")

    agregar_fila_por_encabezados(pagos, {
        "ID_Pago": id_pago,
        "ID_Reserva": id_reserva,
        "Cliente": cliente,
        "Monto": monto_abono,
        "Fecha": fecha_actual,
        "Comentario": comentario or f"Abono adicional reserva {id_reserva}"
    })

    return {
        "ok": True,
        "mensaje": "Abono registrado correctamente",
        "pago": {
            "id_pago": id_pago,
            "cliente": cliente,
            "monto_abono": monto_abono
        },
        "reserva": {
            "id_reserva": id_reserva,
            "viaje": nombre_viaje,
            "saldo_anterior": saldo_actual,
            "saldo_pendiente": nuevo_saldo
        }
    }