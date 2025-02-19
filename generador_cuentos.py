"""
Generador de Cuentos con LangChain 📚
Este script usa LangChain de manera asíncrona para generar cuentos interactivos,
manteniendo la coherencia de la historia usando un historial de mensajes.
"""

import asyncio
import config
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# 1. Configuración del modelo de lenguaje
def crear_modelo():
    """Crea y configura el modelo de ChatOpenAI."""
    return ChatOpenAI(
        api_key=config.OPENAI_API_KEY,
        model="gpt-4o-2024-08-06",
        temperature=0.8  # Mayor temperatura = más creatividad
    )

# 2. Configuración del prompt
def crear_prompt():
    """Crea el template del prompt con el sistema y el historial."""
    return ChatPromptTemplate.from_messages([
        # Instrucciones para el modelo
        ("system", """
        Eres un narrador muy creativo que:
        - Escribe historias con mucho diálogo
        - Describe brevemente a los personajes
        - Hace que animales y objetos puedan hablar
        - Mantiene coherencia con las partes anteriores de la historia
        """),
        # Placeholder para el historial de la conversación
        MessagesPlaceholder(variable_name="history"),
        # Input del usuario
        ("human", "{input}")
    ])

# 3. Configuración de la cadena con historial
def crear_cadena_con_historial(modelo, prompt):
    """Crea una cadena que mantiene el historial de la conversación."""
    # Crear la cadena básica
    cadena = prompt | modelo
    
    # Crear el historial de mensajes
    historial = ChatMessageHistory()
    
    # Crear la cadena con historial
    return RunnableWithMessageHistory(
        cadena,
        lambda session_id: historial,
        input_messages_key="input",
        history_messages_key="history"
    ), historial

async def generar_cuento(cadena, trama: str = "", maximo_tokens: int = 500) -> str:
    """
    Genera una parte del cuento basado en la trama proporcionada.
    
    Args:
        cadena: La cadena de LangChain con historial
        trama: La trama para continuar la historia
        maximo_tokens: Longitud máxima de la respuesta
    
    Returns:
        str: La siguiente parte del cuento
    """
    config = {
        "configurable": {
            "session_id": "story_session",
            "max_tokens": maximo_tokens
        }
    }
    
    # Usar ainvoke para llamada asíncrona
    response = await cadena.ainvoke(
        {"input": f"Continúa o comienza el cuento basado en esta trama: {trama}"},
        config
    )
    return response.content

async def main():
    """Función principal asíncrona que ejecuta el generador de cuentos."""
    # Inicializar componentes
    modelo = crear_modelo()
    prompt = crear_prompt()
    cadena, historial = crear_cadena_con_historial(modelo, prompt)
    
    print("🌟 Generador de Cuentos con IA 📚")
    print("Escribe las tramas de tu historia. El modelo irá generando el cuento parte por parte.")
    print("Para terminar, escribe 'salir'")
    print("-" * 50)
    
    # Loop principal
    while True:
        trama = input("\n✍️  Como sigue tu trama: ")
        if trama.lower() == "salir":
            break
        
        # Esperar la respuesta asíncrona
        print("\n⌛ Generando...", end="", flush=True)
        parte = await generar_cuento(cadena, trama)
        print("\r", end="")  # Limpiar el mensaje de "Generando..."
        print(f"\n📝 Nueva parte del cuento:\n{parte}\n")
        print("-" * 50)

    # Mostrar historia completa
    print("\n📚 Historia completa:\n")
    historia_completa = "\n".join([
        msg.content 
        for msg in historial.messages 
        if isinstance(msg, AIMessage)
    ])
    print(historia_completa)

if __name__ == "__main__":
    # Ejecutar el loop de eventos de asyncio
    asyncio.run(main())
