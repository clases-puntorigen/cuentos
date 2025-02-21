import config
import instructor
from openai import OpenAI
import logging

# Configure logging for OpenAI and related libraries
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("instructor").setLevel(logging.WARNING)

cliente_viejo = OpenAI(api_key=config.OPENAI_API_KEY)
cliente = instructor.from_openai(cliente_viejo)
