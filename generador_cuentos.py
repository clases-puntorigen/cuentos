import config
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Literal

cliente_viejo = OpenAI(api_key=config.OPENAI_API_KEY)
cliente = instructor.from_openai(cliente_viejo)

class Personaje(BaseModel):
    nombre: str = Field(description="El nombre del personaje")
    edad: int = Field(..., gt=0, description="La edad del personaje")
    descripcion: str = Field(..., description="La descripcion del personaje")
    rol: str = Field(..., description="El rol en la historia (heroe, villano, mentor, etc.)")

def obtener_personajes() -> List[Personaje]:
    personajes = []
    print("Agrega personajes a tu historia:")
    while True:
        nombre = input("Nombre del personaje (o escribe listo para terminar):")
        if nombre.lower() == "listo":
            break
        edad = int(input("Edad del personaje:"))
        descripcion = input("Descripcion del personaje:")
        rol = input("Rol del personaje:")
        try:
            personaje = Personaje(nombre=nombre, edad=edad, descripcion=descripcion, rol=rol)
            personajes.append(personaje)
            print(f"Personaje agregado: {personaje.model_dump_json()}")
        except ValueError as e:
            print(f"Error: {e}")
    return personajes

class EventoHistoria(BaseModel):
    tipo: Literal["narrativa", "dialogo"] = Field(..., title="Tipo de evento (narrativa o dialogo)")
    contenido: str = Field(..., title="Texto de la narrativa o diálogo")
    personaje: str = Field(default=None, title="Nombre del personaje si es un diálogo")

class FragmentoHistoria(BaseModel):
    eventos: List[EventoHistoria] = Field(..., title="Lista de eventos (narrativa y diálogos combinados)")

class HistoriaCompleta(BaseModel):
    titulo: str = Field(..., title="Título de la historia")
    personajes: List[str] = Field(..., title="Lista de personajes en la historia")
    fragmentos: List[FragmentoHistoria] = []

def dame_los_dialogos(texto):
    prompt = f"""
    # Analiza el siguiente texto:
    {texto}

    # Obten los dialogos del texto con sus respectivos personajes
    """
    respuesta = cliente.chat.completions.create(
        #model="o3-mini-2025-01-31",
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "Eres un experto lector y analista que entiendes libros, cuentos y preparas dialogos para el cine."},
            {"role": "user", "content": prompt},
        ],
        response_model=HistoriaCompleta,
        temperature=0.5, # controla la creatividad
    )
    return respuesta

def generar_cuento(personajes, memoria="", trama="", maximo=500):
    texto_personajes = ""
    for personaje in personajes:
        texto_personajes += f"{personaje.nombre} es un {personaje.rol} de {personaje.edad} años. {personaje.descripcion}\n"

    #texto_personajes = "\n".join([f"{p.nombre} es un {p.rol} de {p.edad} años. {p.descripcion}\n" for p in personajes])

    prompt = f"""
    # La historia comienza con los siguientes personajes:
    {texto_personajes}

    # A partir de esto, desarrolla la historia basada en la siguiente trama:
    {trama}

    # El cuento comienza así:
    {memoria}
    """

    respuesta = cliente_viejo.chat.completions.create(
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
    personajes = obtener_personajes()
    cuento = ""
    while True:
        trama = input("Escribe la trama de tu cuento (o escribe 'salir' para terminar):")
        if trama.lower() == "salir":
            break
        parte = generar_cuento(personajes, cuento, trama)
        print(f"\n✨ Aqui esta la parte del cuento:\n{parte}")
        cuento += parte

    print("\n\n✨ Aqui esta el cuento completo:\n")
    print(cuento)
    dialogos = dame_los_dialogos(cuento)
    print("\n\n✨ Aqui estan la historia estructurada del cuento:\n", dialogos)
    #for dialogo in dialogos.dialogos:
    #    print(f"Personaje: {dialogo.personaje}\nDice: {dialogo.texto}")