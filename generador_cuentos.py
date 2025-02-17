import config
from openai import OpenAI

def generar_cuento(trama):
    cliente = OpenAI(api_key=config.OPENAI_API_KEY)
    #prompt = f"Escribe un cuento basado en la siguiente trama: {trama}"
    prompt = f"""
    Cuentame una historia sobre: {trama}

    Devuelveme un cuento que tenga los siguientes elementos:
    - Un niño
    - Una botella de Coca Cola
    - Un pastel de La Ligua
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