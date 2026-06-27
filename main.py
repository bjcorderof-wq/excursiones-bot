# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 16:39:03 2026

@author: bcordero
"""

from fastapi import FastAPI
from sheets import obtener_destinos
from sheets import obtener_itinerario_por_viaje, obtener_itinerario_por_consulta

app = FastAPI()


@app.get("/")
def home():
    return {"status": "ok"}


@app.get("/destinos")
def listar_destinos():
    return obtener_destinos()

@app.get("/itinerario/{id_viaje}")
def consultar_itinerario(id_viaje: str):
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
def consultar_itinerario(consulta: str):
    return obtener_itinerario_por_consulta(consulta)

@app.get("/itinerario_texto/{consulta}")
def consultar_itinerario_texto(consulta: str):
    return obtener_itinerario_por_consulta(consulta)

from pydantic import BaseModel

class ItinerarioRequest(BaseModel):
    consulta: str


@app.post("/itinerario")
def consultar_itinerario_post(data: ItinerarioRequest):
    return obtener_itinerario_por_consulta(data.consulta)