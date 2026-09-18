"""
rover-api  ·  BACKEND (interno)
Simula el computador de a bordo de un rover en Marte.
Expone la cámara (una imagen) y procesa los comandos de operación,
devolviendo la telemetría actualizada. No tiene interfaz.
"""
import os
from flask import Flask, jsonify, request, send_file

app = Flask(__name__)
CAMARA = os.path.join(os.path.dirname(__file__), "camara.jpg")

# Estado del rover (en memoria). Simulación con 1 réplica.
rover = {
    "bateria": 87, "temp": -63, "x": 0, "y": 0,
    "rumbo": 0, "senal": 92, "sol": 428, "fotos": 0, "estado": "Operativo",
}
RUMBOS = ["Norte", "Noreste", "Este", "Sureste", "Sur", "Suroeste", "Oeste", "Noroeste"]


def rumbo_texto(grados):
    return RUMBOS[int((grados % 360) / 45)]


def telemetria():
    r = dict(rover)
    r["rumbo_texto"] = rumbo_texto(rover["rumbo"])
    return r


def gastar_bateria(n):
    rover["bateria"] = max(0, rover["bateria"] - n)
    if rover["bateria"] <= 15:
        rover["estado"] = "Batería baja"


@app.get("/health")
def health():
    return jsonify(status="healthy"), 200


@app.get("/camara")
def camara():
    # La "cámara de a bordo": devuelve la imagen del terreno marciano.
    return send_file(CAMARA, mimetype="image/jpeg")


@app.post("/comando")
def comando():
    accion = (request.get_json(silent=True) or {}).get("accion", "")
    import math
    if accion == "avanzar":
        rad = math.radians(rover["rumbo"])
        rover["x"] += round(math.sin(rad))
        rover["y"] += round(math.cos(rad))
        gastar_bateria(2)
        msg = f"Avanzando 1 m hacia el {rumbo_texto(rover['rumbo'])}. Terreno rocoso, tracción estable."
    elif accion == "retroceder":
        rad = math.radians(rover["rumbo"])
        rover["x"] -= round(math.sin(rad))
        rover["y"] -= round(math.cos(rad))
        gastar_bateria(2)
        msg = "Retrocediendo 1 m. Maniobra completada."
    elif accion == "girar_izq":
        rover["rumbo"] = (rover["rumbo"] - 45) % 360
        gastar_bateria(1)
        msg = f"Giro a la izquierda. Nuevo rumbo: {rumbo_texto(rover['rumbo'])}."
    elif accion == "girar_der":
        rover["rumbo"] = (rover["rumbo"] + 45) % 360
        gastar_bateria(1)
        msg = f"Giro a la derecha. Nuevo rumbo: {rumbo_texto(rover['rumbo'])}."
    elif accion == "panoramica":
        rover["fotos"] += 1
        gastar_bateria(3)
        msg = f"Imagen panorámica capturada (#{rover['fotos']}). Enviando a la Tierra…"
    elif accion == "diagnostico":
        msg = ("Diagnóstico: Motores OK · Cámara OK · Antena OK · "
               f"Paneles solares OK · Batería {rover['bateria']}%.")
    elif accion == "estado":
        msg = "Reporte de estado emitido."
    else:
        return jsonify(error="Acción no reconocida"), 400

    return jsonify(mensaje=msg, telemetria=telemetria())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
