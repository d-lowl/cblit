"""LLM."""
from langchain import OpenAI
from langchain.llms.base import BaseLLM


def get_llm(temperature: float = 0) -> BaseLLM:
    """Get LLM to use in Langchain sessions.

    Args:
        temperature (float): temperature

    Returns:
        BaseLLM: Langchain compatible LLM
    """
    return OpenAI(temperature=temperature)  # type: ignore [call-arg]
