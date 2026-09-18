import logging
import os
from typing import Optional, Type, Any

import dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from torch._C import OptionalType

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

model = os.getenv("LLM_MODEL")
api_key = os.getenv("LLM_API_KEY")

logger.info("Initializing LLM model: %s", model)

llm = ChatGoogleGenerativeAI(
    model=model,
    google_api_key=api_key
)


def get_agent(structured_response: Optional[Type[BaseModel]],system_prompt:str,context_schema:Optional[Any]=None):

    agent = create_agent(
        model=llm,
        response_format=structured_response,
        system_prompt=system_prompt,
        context_schema=context_schema,

    )

    return agent


