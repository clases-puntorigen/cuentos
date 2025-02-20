from utils.remote_expose import exposeRemote
from ia import cliente

import config, os, replicate
from pydantic import BaseModel, Field
from typing import List, Literal

class Voz(BaseModel):
    archivo: str = Field(..., description="Nombre del archivo .mp3")

def eligir_voz(prompt):
    # obtenemos lista de archivos .mp3 en carpeta 'voces' y hacemos una lista
    archivos = os.listdir("voces")
    archivos_mp3 = "\n".join([archivo for archivo in archivos if archivo.endswith(".mp3")])
    prompt = f"""
# elige uno de los siguientes archivos .mp3:
{archivos_mp3}

# que su nombre mejor represente lo solicitado en el siguiente prompt:
{prompt}
    """
    respuesta = cliente.chat.completions.create(
        #model="o3-mini-2025-01-31",
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "Eres un experto en entender los tonos de voz que deben usarse segun lo solicitado por el usuario."},
            {"role": "user", "content": prompt},
        ],
        response_model=Voz,
        temperature=0.5, # controla la creatividad
    )
    return respuesta.archivo

def generar_audio(voz:str = "voces/narrador1.mp3", texto:str = "Hola", archivo:str = "output.wav"):
    with exposeRemote(voz) as narrador:
        output = replicate.run(
            "chenxwh/openvoice:d548923c9d7fc9330a3b7c7f9e2f91b2ee90c83311a351dfcd32af353799223d",
            input={
                "audio": narrador,
                "text": texto,
                "language": "ES",
                "speed": 1
            },
        )
    with open(archivo, "wb") as file:
        file.write(output.read())

if __name__ == "__main__":
    voz_descrita = input("Describe la voz: ")
    voz = eligir_voz(voz_descrita)
    print(f"Voz elegida: {voz}")