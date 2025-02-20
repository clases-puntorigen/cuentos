import config
import instructor
from openai import OpenAI

cliente_viejo = OpenAI(api_key=config.OPENAI_API_KEY)
cliente = instructor.from_openai(cliente_viejo)
