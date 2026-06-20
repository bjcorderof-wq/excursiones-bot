# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 16:39:03 2026

@author: bcordero
"""

from fastapi import FastAPI
from sheets import obtener_destinos

app = FastAPI()


@app.get("/")
def home():
    return {"status": "ok"}


@app.get("/destinos")
def listar_destinos():
    return obtener_destinos()