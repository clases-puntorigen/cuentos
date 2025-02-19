"""
Generador de Cuentos con Diálogos usando LangChain 
Este script usa LangChain de manera asíncrona para generar cuentos interactivos
y extraer los diálogos usando Pydantic para el parsing estructurado.
"""

import asyncio
import config
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

# 1. Definición de modelos Pydantic para el parsing de diálogos
class Dialogo(BaseModel):
    """Modelo para representar un diálogo individual."""
    personaje: str = Field(description="El personaje que habla")
    texto: str = Field(description="El texto del diálogo")

class ListaDialogos(BaseModel):
    """Modelo para representar una lista de diálogos."""
    dialogos: List[Dialogo] = Field(description="Lista de diálogos del texto")

# 2. Configuración del modelo de lenguaje
def crear_modelo():
    """Crea y configura el modelo de ChatOpenAI."""
    return ChatOpenAI(
        api_key=config.OPENAI_API_KEY,
        model="gpt-4o-2024-08-06",
        temperature=0.8  # Mayor temperatura = más creatividad
    )

# 3. Configuración de los prompts
def crear_prompt_cuento():
    """Crea el template del prompt para generar el cuento."""
    return ChatPromptTemplate.from_messages([
        ("system", """
        Eres un narrador muy creativo que:
        - Escribe historias con mucho diálogo
        - Describe brevemente a los personajes
        - Hace que animales y objetos puedan hablar
        - Mantiene coherencia con las partes anteriores de la historia
        """),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])

def crear_prompt_dialogos(parser: PydanticOutputParser):
    """Crea el template del prompt para extraer diálogos."""
    return ChatPromptTemplate.from_messages([
        ("system", "Eres un experto analista que identifica y extrae diálogos de textos narrativos."),
        ("human", """
        Analiza el siguiente texto y extrae todos los diálogos:
        {texto}

        {format_instructions}
        """)
    ])

# 4. Configuración de las cadenas
def crear_cadenas(modelo):
    """Crea las cadenas para generación de cuentos y extracción de diálogos."""
    # Cadena para el cuento
    prompt_cuento = crear_prompt_cuento()
    cadena_cuento = prompt_cuento | modelo
    historial = ChatMessageHistory()
    cadena_con_historial = RunnableWithMessageHistory(
        cadena_cuento,
        lambda session_id: historial,
        input_messages_key="input",
        history_messages_key="history"
    )
    
    # Cadena para los diálogos
    parser = PydanticOutputParser(pydantic_object=ListaDialogos)
    prompt_dialogos = crear_prompt_dialogos(parser)
    cadena_dialogos = prompt_dialogos | modelo | parser
    
    return cadena_con_historial, cadena_dialogos, historial

async def generar_cuento(cadena, trama: str = "", maximo_tokens: int = 500) -> str:
    """Genera una parte del cuento basado en la trama proporcionada."""
    config = {
        "configurable": {
            "session_id": "story_session",
            "max_tokens": maximo_tokens
        }
    }
    
    response = await cadena.ainvoke(
        {"input": f"Continúa o comienza el cuento basado en esta trama: {trama}"},
        config
    )
    return response.content

async def extraer_dialogos(cadena, texto: str) -> ListaDialogos:
    """Extrae los diálogos del texto usando el parser de Pydantic."""
    parser = PydanticOutputParser(pydantic_object=ListaDialogos)
    response = await cadena.ainvoke({
        "texto": texto,
        "format_instructions": parser.get_format_instructions()
    })
    return response

def formatear_dialogos(lista_dialogos: ListaDialogos) -> str:
    """Formatea la lista de diálogos para mostrar."""
    return "\n".join([
        f"[{d.personaje}]: \"{d.texto}\""
        for d in lista_dialogos.dialogos
    ])

async def main():
    """Función principal asíncrona que ejecuta el generador de cuentos."""
    # Inicializar componentes
    modelo = crear_modelo()
    cadena_cuento, cadena_dialogos, historial = crear_cadenas(modelo)
    
    print(" Generador de Cuentos con Diálogos ")
    print("Escribe las tramas de tu historia. El modelo irá generando el cuento parte por parte.")
    print("Al final, extraeremos todos los diálogos del cuento.")
    print("-" * 50)
    
    # Loop principal
    while True:
        trama = input("\n Cómo sigue tu trama: ")
        if trama.lower() == "salir":
            break
        
        # Generar parte del cuento
        print("\n Generando...", end="", flush=True)
        parte = await generar_cuento(cadena_cuento, trama)
        print("\r", end="")  # Limpiar el mensaje de "Generando..."
        print(f"\n Nueva parte del cuento:\n{parte}\n")
        print("-" * 50)

    # Obtener historia completa
    print("\n Historia completa:\n")
    historia_completa = "\n".join([
        msg.content 
        for msg in historial.messages 
        if isinstance(msg, AIMessage)
    ])
    print(historia_completa)
    
    # Extraer y mostrar diálogos
    print("\n Extrayendo diálogos...", end="", flush=True)
    dialogos = await extraer_dialogos(cadena_dialogos, historia_completa)
    print("\r", end="")
    print("\n Diálogos del cuento:\n")
    print(formatear_dialogos(dialogos))

if __name__ == "__main__":
    asyncio.run(main())