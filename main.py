# -*- coding: utf-8 -*-

from fastapi import FastAPI
from pydantic import BaseModel

from sheets import (
    obtener_destinos,
    obtener_itinerario_por_viaje,
    obtener_itinerario_por_consulta
)

app = FastAPI(
    title="Excursiones Meza API",
    version="1.0.0",
    servers=[
        {
            "url": "https://excursiones-bot-production.up.railway.app",
            "description": "Producción"
        }
    ]
)


class ItinerarioRequest(BaseModel):
    consulta: str


@app.get("/")
def home():
    return {
        "status": "ok",
        "version": "openapi-v2"
    }


@app.get("/destinos")
def listar_destinos():
    return obtener_destinos()


@app.get("/itinerario/{id_viaje}")
def consultar_itinerario_por_id(id_viaje: str):
    resultado = obtener_itinerario_por_viaje(id_viaje)

    if not resultado:
        return {
            "mensaje": "No se encontró itinerario para este viaje",
            "id_viaje": id_viaje,
            "itinerario": []
        }

    return {
        "id_viaje": id_viaje,
        "itinerario": resultado
    }


@app.get("/itinerario")
def consultar_itinerario_get(consulta: str):
    return obtener_itinerario_por_consulta(consulta)


@app.get("/itinerario_texto/{consulta}")
def consultar_itinerario_texto(consulta: str):
    return obtener_itinerario_por_consulta(consulta)


@app.post("/itinerario")
def consultar_itinerario_post(data: ItinerarioRequest):
    return obtener_itinerario_por_consulta(data.consulta)