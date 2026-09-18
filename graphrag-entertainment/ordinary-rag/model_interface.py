import logging
import os

import dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

model = os.getenv("LLM_MODEL")
api_key = os.getenv("LLM_API_KEY")

logger.info("Initializing ordinary-rag LLM model: %s", model)

llm = ChatGoogleGenerativeAI(
    model=model,
    google_api_key=api_key,
)
