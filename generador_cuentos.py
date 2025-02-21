from ia import cliente, cliente_viejo
from pydantic import BaseModel, Field
from typing import List, Literal
from generar_audio import eligir_voz, generar_audio
import asyncio

class Personaje(BaseModel):
    nombre: str = Field(description="El nombre del personaje")
    edad: int = Field(..., gt=0, description="La edad del personaje")
    descripcion: str = Field(..., description="La descripcion del personaje")
    rol: str = Field(..., description="El rol en la historia (heroe, villano, mentor, etc.)")
    voz: str = Field(..., description="Describa la voz")

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
        # generamos la descripcion de la voz con IA
        voz = eligir_voz(f"{nombre} es un {rol} de {edad} años. {descripcion}", personajes)
        try:
            personaje = Personaje(nombre=nombre, edad=edad, descripcion=descripcion, rol=rol, voz=voz)
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

def generar_cuento(personajes, memoria="", trama="", maximo=500,final=False):
    texto_personajes = ""
    for personaje in personajes:
        texto_personajes += f"{personaje.nombre} es un {personaje.rol} de {personaje.edad} años. {personaje.descripcion}\n"

    #texto_personajes = "\n".join([f"{p.nombre} es un {p.rol} de {p.edad} años. {p.descripcion}\n" for p in personajes])
    trama_ = f"""
    # A partir de esto, desarrolla la historia basada en la siguiente trama:
    {trama}
    """
    if final:
        maximo = None
        trama_ = "# A partir de esto, desarrolla un final para la historia."
    prompt = f"""
    # La historia comienza con los siguientes personajes:
    {texto_personajes}

    {trama_}

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


#--------------------------#
async def main():
    print("Generador de Cuentos con IA ✨")
    #personajes = obtener_personajes()
    personajes = [
        Personaje(
            nombre = "perro",
            edad = 20,
            descripcion = "de color negro, grande, y voz profunda, de raza labrador.",
            rol = "villano",
            voz = "personaje1.mp3"
        ),
        Personaje(
            nombre = "gato",
            edad = 20,
            descripcion = "de color naranjo, pequeño, y voz chillona, de raza angora.",
            rol = "heroe",
            voz = "nube1.mp3"
        )
    ]
    
    personajes_dict = {p.nombre: p for p in personajes}
    cuento = ""
    while True:
        trama = input("Escribe la trama de tu cuento (o escribe 'salir' para terminar):")
        if trama.lower() == "salir":
            if cuento.strip(): # para verificar, que haya cuento antes de generar un final.
                print("\n✨ Generando el final de la historia ✨\n")
                parte = generar_cuento(personajes=personajes, memoria=cuento,final=True) # aqui es true porque debe generar el final
                print(parte)
                cuento += parte
                break
        parte = generar_cuento(personajes=personajes, memoria=cuento, trama=trama,final=False) 
        print(f"\n✨ Aqui esta la parte del cuento:\n{parte}")
        cuento += parte

    print("\n\n✨ Aqui esta el cuento completo:\n")
    print(cuento)
    fragmentos = dame_los_dialogos(cuento)
    print("\n\n✨ Aqui estan la historia estructurada del cuento:\n", fragmentos)
    print("**"*20)
    
    #await dialogos_audios(fragmentos, personajes_dict)

if __name__ == "__main__":
    asyncio.run(main())

"""   async def generar_audio_async(voz, contenido, archivo_destino):
    # Si `generar_audio` no es asíncrona, la ejecutamos en un hilo separado
        await asyncio.to_thread(generar_audio, voz, contenido, archivo_destino)
        # asyncio.to_thread se utiliza para funciones que normente bloquiarian el hilo principal, para no bloquiar el resto del programa

    async def dialosgos_audios(fragmento,personajes_dict):
        procesos = []
        for i, fragmento in enumerate(fragmentos.fragmentos[0].eventos):
            print(f"\n✨ Procesando la parte {i+1}:\n")
            if fragmento.personaje and fragmento.personaje in personajes_dict:
                proceso = generar_audio("voces/"+personajes_dict[fragmento.personaje].voz, fragmento.contenido, f"audios/parte_{i+1}.wav")
                procesos.append(proceso)

            elif fragmento.personaje and fragmento.personaje not in personajes_dict:
                # el personaje puede no haber sido agregado por el usuario; tenemos que inventarle una voz
                print("⚠️ El personaje", fragmento.personaje, "no se ha agregado. Le inventaremos una voz.")
                voz = eligir_voz(f"{fragmento.personaje} dice {fragmento.contenido}", personajes)
                personajes_dict[fragmento.personaje] = Personaje(nombre=fragmento.personaje, edad=100, descripcion="", rol="secundario", voz=voz)
                proceso = generar_audio("voces/"+voz, fragmento.contenido, f"audios/parte_{i+1}.wav")
                procesos.append(proceso)
            else:
                proceso = generar_audio("voces/narrador1.mp3", fragmento.contenido, f"audios/parte_{i+1}.wav")
                procesos.append(proceso)
        await asyncio.gather(*procesos)

"""