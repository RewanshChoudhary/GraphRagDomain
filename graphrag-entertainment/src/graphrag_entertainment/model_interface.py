import logging
import os
from typing import Any, Optional, Type

import dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

provider = os.getenv("LLM_PROVIDER", "gemini").lower()
model = os.getenv("LLM_MODEL")
api_key = os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_BASE_URL")
  
temperature = float(os.getenv("LLM_TEMPERATURE", "0.0"))

logger.info("Initializing LLM model: %s (provider: %s)", model, provider)

if provider == "lmstudio":
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(
        model=model,
        api_key=api_key or "lm-studio",
        base_url=base_url or "http://localhost:1234/v1",
        temperature=temperature,
    )
else:
    llm = ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=temperature,
    )


def get_llm(structured_response: Optional[Type[BaseModel]] = None):
    if structured_response is None:
        return llm

    return llm.with_structured_output(structured_response)


def get_agent(structured_response: Optional[Type[BaseModel]],system_prompt:str,context_schema:Optional[Any]=None):

    agent = create_agent(
        model=llm,
        response_format=structured_response,
        system_prompt=system_prompt,
        context_schema=context_schema,

    )

    return agent
