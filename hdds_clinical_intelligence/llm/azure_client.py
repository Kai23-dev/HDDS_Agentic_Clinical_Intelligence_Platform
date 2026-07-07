"""
Central Azure OpenAI client for chat completions and embeddings.

All Azure access goes through here so the rest of the code never touches the SDK
directly. Everything is env-configured and guarded by `is_configured()`, so the
app degrades gracefully when Azure credentials are absent.

Required env vars (set on the company laptop / Azure App Service):
    AZURE_OPENAI_ENDPOINT           e.g. https://my-resource.openai.azure.com/
    AZURE_OPENAI_API_KEY            key from the Azure OpenAI resource
    AZURE_OPENAI_API_VERSION        e.g. 2024-06-01 (has a sensible default)
    AZURE_OPENAI_CHAT_DEPLOYMENT    the *deployment name* of your chat model
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT  deployment name of your embedding model
"""

import os
from typing import List

_client = None


def is_configured() -> bool:
    """True only when the minimum Azure OpenAI credentials are present."""
    return bool(os.getenv("AZURE_OPENAI_ENDPOINT") and os.getenv("AZURE_OPENAI_API_KEY"))


def _get_client():
    """Lazily construct and cache the AzureOpenAI client."""
    global _client
    if _client is None:
        from openai import AzureOpenAI  # imported lazily so the dep is optional
        _client = AzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-06-01"),
        )
    return _client


def chat(messages: List[dict], temperature: float = 0.2, max_tokens: int = 800, timeout: float = 6.0) -> str:
    """Run a chat completion. `messages` is the standard [{role, content}] list.

    `timeout` (seconds) keeps a misconfigured/unreachable deployment from hanging
    the request; the caller is expected to fall back to another backend on error.
    """
    deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o")
    resp = _get_client().chat.completions.create(
        model=deployment,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
    )
    return resp.choices[0].message.content or ""


def embed(texts: List[str]) -> List[List[float]]:
    """Return one embedding vector per input text."""
    deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
    resp = _get_client().embeddings.create(model=deployment, input=texts)
    return [d.embedding for d in resp.data]
