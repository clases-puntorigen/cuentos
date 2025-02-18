import config
from openai import OpenAI

def generar_cuento(trama):
    cliente = OpenAI(api_key=config.OPENAI_API_KEY)
    #prompt = f"Escribe un cuento basado en la siguiente trama: {trama}"
    trama = "Un joven llamado Alex que debe vencer tres jefes para escapar del juego."
    prompt = f"""Escribe una historia corta de máximo 1000 palabras sobre un joven atrapado en un videojuego 
    estilo RPG donde debe derrotar jefes para subir de nivel y encontrar la forma de salir. El protagonista es un gamer 
    hábil pero con poca confianza en sí mismo, y la ambientación debe ser un mundo de videojuego inmersivo con múltiples 
    biomas y mazmorras. A lo largo de la historia, el joven enfrenta al menos tres jefes, cada uno más difícil que el anterior, 
    lo que lo obliga a mejorar sus habilidades y descubrir un misterio detrás del juego. El clímax debe incluir un enfrentamiento 
    con el jefe final con un giro inesperado. La narración debe estar en tercera persona limitada, el tono debe ser dinámico y 
    lleno de acción con referencias a mecánicas de videojuegos. 
    Cuentame una historia sobre: {trama}
    """

    respuesta = cliente.chat.completions.create(
        #model="o3-mini-2025-01-31",
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )
    print(respuesta.choices[0].message.content)

if __name__ == "__main__":
    print("Generador de Cuentos")
    generar_cuento("Un niño encuentra un dragón en el bosque.")