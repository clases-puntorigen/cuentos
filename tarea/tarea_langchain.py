import os
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import SimpleSequentialChain 

# Cargar variables de entorno
load_dotenv()

# Inicializar el modelo
llm = OpenAI(temperature=0.7)

# Chain para generar destino
template_destino = PromptTemplate(
    input_variables=["presupuesto"],
    template="Sugiere un destino turístico para un presupuesto de {presupuesto} dólares."
)
chain_destino = LLMChain(llm=llm, prompt=template_destino)

# Chain para generar actividades
template_actividades = PromptTemplate(
    input_variables=["destino"],
    template="Sugiere 3 actividades principales para hacer en {destino}."
)
chain_actividades = LLMChain(llm=llm, prompt=template_actividades)

# Combinar chains
chain_completa = SimpleSequentialChain(
    chains=[chain_destino, chain_actividades],
    verbose=True
)

# Ejecutar cadena completa con un presupuesto de ejemplo
resultado = chain_completa.run("1000")
print(resultado)
