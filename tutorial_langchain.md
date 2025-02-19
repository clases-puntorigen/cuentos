# Tutorial: Uso Básico de LangChain en Python 🐍

Este tutorial te enseñará los conceptos básicos de LangChain utilizando ejemplos prácticos de generación de cuentos. Aprenderás cómo crear aplicaciones que interactúan con modelos de lenguaje de manera estructurada y mantenible.

## 1. Instalación y Configuración Inicial

Primero, necesitas instalar LangChain y sus dependencias:

```bash
pip install langchain langchain-openai python-dotenv
```

Para usar OpenAI, necesitas configurar tu API key. Es una buena práctica mantenerla en un archivo de configuración separado:

```python
# config.py
OPENAI_API_KEY = "tu-api-key-aquí"
```

## 2. Componentes Básicos de LangChain

### 2.1 Modelo de Lenguaje

El modelo es el componente que procesa el lenguaje natural. En nuestro caso, usamos ChatOpenAI:

```python
from langchain_openai import ChatOpenAI

def crear_modelo():
    return ChatOpenAI(
        api_key=config.OPENAI_API_KEY,
        model="gpt-4",
        temperature=0.8  # Mayor temperatura = más creatividad
    )
```

### 2.2 Prompts

Los prompts son las instrucciones que le damos al modelo. LangChain usa templates para estructurarlos:

```python
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

def crear_prompt():
    return ChatPromptTemplate.from_messages([
        # Instrucciones para el sistema
        ("system", "Instrucciones aquí..."),
        # Historial de mensajes
        MessagesPlaceholder(variable_name="history"),
        # Input del usuario
        ("human", "{input}")
    ])
```

### 2.3 Cadenas (Chains)

Las cadenas conectan los diferentes componentes. Por ejemplo, conectar un prompt con un modelo:

```python
# Cadena básica
cadena = prompt | modelo

# Cadena con historial
cadena_con_historial = RunnableWithMessageHistory(
    cadena,
    lambda session_id: historial,
    input_messages_key="input",
    history_messages_key="history"
)
```

## 3. Características Avanzadas

### 3.1 Parsing Estructurado con Pydantic

LangChain puede estructurar las respuestas del modelo usando Pydantic:

```python
from pydantic import BaseModel, Field
from typing import List

class Dialogo(BaseModel):
    personaje: str = Field(description="El personaje que habla")
    texto: str = Field(description="El texto del diálogo")

class ListaDialogos(BaseModel):
    dialogos: List[Dialogo]
```

### 3.2 Operaciones Asíncronas

LangChain soporta operaciones asíncronas para mejor rendimiento:

```python
async def generar_cuento(cadena, trama: str = "", maximo_tokens: int = 500):
    config = {
        "configurable": {
            "session_id": "story_session",
            "max_tokens": maximo_tokens
        }
    }
    
    response = await cadena.ainvoke(
        {"input": f"Continúa el cuento basado en: {trama}"},
        config
    )
    return response.content
```

## 4. Ejemplo Práctico

Aquí hay un ejemplo completo que muestra cómo juntar todo:

```python
async def main():
    # 1. Inicializar componentes
    modelo = crear_modelo()
    prompt = crear_prompt()
    cadena, historial = crear_cadena_con_historial(modelo, prompt)
    
    # 2. Loop principal
    while True:
        trama = input("✍️  Como sigue tu trama: ")
        if trama.lower() == "salir":
            break
            
        # 3. Generar contenido
        resultado = await generar_cuento(cadena, trama)
        print("\n", resultado, "\n")

if __name__ == "__main__":
    asyncio.run(main())
```

## 5. Consejos y Mejores Prácticas

1. **Manejo de API Keys**: Siempre guarda las API keys en archivos de configuración separados.
2. **Uso de Async**: Utiliza operaciones asíncronas para mejor rendimiento en aplicaciones interactivas.
3. **Estructuración**: Usa Pydantic para estructurar las respuestas del modelo cuando necesites procesarlas.
4. **Historial**: Implementa un sistema de historial cuando necesites mantener contexto en una conversación.

## 6. Recursos Adicionales

- [Documentación oficial de LangChain](https://python.langchain.com/docs/get_started/introduction.html)
- [Guía de ChatOpenAI](https://python.langchain.com/docs/integrations/chat/openai)
- [Tutorial de Pydantic](https://docs.pydantic.dev/latest/)
