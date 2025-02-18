import config
from openai import OpenAI

cliente = OpenAI(api_key=config.OPENAI_API_KEY)

def dame_los_dialogos(texto):
    prompt = f"""
    # Analiza el siguiente texto:
    {texto}

    # Obten los dialogos del texto con sus respectivos personajes en el siguiente formato en orden:
    [personaje]: "dialogo"

    # Ejemplo:
    [Juan]: "Hola, ¿como estas?"
    [Maria]: "Bien, gracias. ¿Y tu?"
    [Juan]: "Tambien estoy bien, gracias."
    """
    respuesta = cliente.chat.completions.create(
        #model="o3-mini-2025-01-31",
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "Eres un experto lector y analista que entiendes libros, cuentos y preparas dialogos para el cine."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5, # controla la creatividad
    )
    return respuesta.choices[0].message.content

def generar_cuento(memoria="", trama="", maximo=500):
    prompt = """
    # Escribe un cuento basado en la siguiente trama:
    {trama}

    # El cuento comienza así:
    {memoria}
    """.format(trama=trama, memoria=memoria, maximo_palabras=maximo)

    respuesta = cliente.chat.completions.create(
        #model="o3-mini-2025-01-31",
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "Eres un narrador muy creativo, te encanta escribir historias con mucho dialogo, siempre describiendo brevemente a los personajes primero. En tus historias los animales y objetos inanimados hablan con palabras humanas."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.8, # controla la creatividad
        max_tokens=maximo # longitud maxima del cuento/trozo
    )
    return respuesta.choices[0].message.content

if __name__ == "__main__":
    print("Generador de Cuentos con IA ✨")
    cuento = ""
    while True:
        trama = input("Escribe la trama de tu cuento (o escribe 'salir' para terminar):")
        if trama.lower() == "salir":
            break
        parte = generar_cuento(cuento, trama)
        print(f"\n✨ Aqui esta la parte del cuento:\n{parte}")
        cuento += parte

    print("\n\n✨ Aqui esta el cuento completo:\n")
    print(cuento)
    dialogos = dame_los_dialogos(cuento)
    print("\n\n✨ Aqui estan los dialogos del cuento:\n", dialogos)