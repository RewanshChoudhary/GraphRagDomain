from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate

from model_interface import llm


class RAGAnswer(BaseModel):
    answer: str
    sources: list[str]


prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful assistant. Answer the question using ONLY the "
        "provided context. If the context doesn't contain enough information "
        "to answer, say so clearly.",
    ),
    (
        "human",
        "Context:\n{context}\n\nQuestion: {question}",
    ),
])

structured_llm = llm.with_structured_output(RAGAnswer)
chain = prompt | structured_llm


def extract_answer(query: str, context: str) -> RAGAnswer:
    return chain.invoke({"context": context, "question": query})
