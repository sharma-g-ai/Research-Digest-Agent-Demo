import os

from langchain_openai import ChatOpenAI


def get_llm(temperature: float = 0) -> ChatOpenAI:
    """Return a ChatOpenAI instance pointed at the LiteLLM proxy.

    Reads LITELLM_BASE_URL, LITELLM_API_KEY, and LLM_MODEL from environment
    variables. load_dotenv() must be called before this function is used —
    that is the responsibility of main.py.

    Args:
        temperature: Sampling temperature. Defaults to 0 for deterministic
            output. Pass a non-zero value only when variation is explicitly
            required.

    Returns:
        A configured ChatOpenAI instance.
    """
    from dotenv import load_dotenv

    load_dotenv()
    base_url = os.getenv("LITELLM_PROXY_URL")
    api_key = os.getenv("LITELLM_API_KEY")
    model = os.getenv("LLM_MODEL") or "gpt-4o"
    return ChatOpenAI(
        base_url=base_url,
        api_key=api_key,
        model=model,
        temperature=temperature,
    )
