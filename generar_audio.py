from utils.remote_expose import exposeRemote
from ia import cliente

import config, os, replicate, json
from pydantic import BaseModel, Field
from typing import List, Literal

class Voz(BaseModel):
    archivo: str = Field(..., description="Nombre del archivo .mp3")

def eligir_voz(prompt="", personajes=None):
    personajes_dict = {}
    if personajes:
        # Solo guardamos el mapeo de personaje -> voz
        personajes_dict = {p.nombre: p.voz for p in personajes}
    # obtenemos lista de archivos .mp3 en carpeta 'voces' y hacemos una lista
    archivos = os.listdir("voces")
    # exclude the 'narrator.mp3' file from archivos
    archivos = [archivo for archivo in archivos if archivo != "narrator.mp3"]
    archivos_mp3 = "\n".join([archivo for archivo in archivos if archivo.endswith(".mp3")])
    prompt = f"""
# elige uno de los siguientes archivos .mp3:
{archivos_mp3}

# en donde el archivo mejor represente lo solicitado en el siguiente prompt:
{prompt}

# intenta no usar voces que ya estén asignadas a otros personajes:
{json.dumps(personajes_dict, indent=2)}
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
            "ttsds/openvoice_2:795fe9c3fc9d3d4cfac1ca97d8c8d33b522b42068daec53ab3c74f775dd506c8",
            #"chenxwh/openvoice:d548923c9d7fc9330a3b7c7f9e2f91b2ee90c83311a351dfcd32af353799223d",
            input={
                #"audio": narrador,
                "speaker_reference": narrador,
                "text": texto,
                #"language": "ES",
                "language": "es",
                #"speed": 1
            },
        )
    with open(archivo, "wb") as file:
        file.write(output.read())

if __name__ == "__main__":
    voz_descrita = input("Describe la voz: ")
    voz = eligir_voz(voz_descrita)
    print(f"Voz elegida: {voz}")