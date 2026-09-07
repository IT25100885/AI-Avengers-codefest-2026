import json
import os
import re
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables from .env if present
load_dotenv()

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = "llama-3.3-70b-versatile"


def get_groq_client(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> OpenAI:
    """Get an OpenAI-compatible client configured for Groq.

    Args:
        api_key: Optional Groq API key. If not provided, reads GROQ_API_KEY from environment.
        base_url: Optional base URL. Defaults to Groq OpenAI-compatible endpoint.

    Returns:
        OpenAI: Initialized client instance.

    Raises:
        ValueError: If GROQ_API_KEY is not set or provided.
    """
    resolved_api_key = api_key or os.getenv("GROQ_API_KEY")
    if not resolved_api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. Please provide it directly or set it in your environment / .env file."
        )

    resolved_base_url = base_url or os.getenv("GROQ_BASE_URL", GROQ_BASE_URL)
    return OpenAI(
        api_key=resolved_api_key,
        base_url=resolved_base_url,
    )


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True,
)
def call_llm(
    messages: List[Dict[str, Any]],
    model: Optional[str] = None,
    temperature: float = 0.2,
    client: Optional[OpenAI] = None,
    **kwargs: Any,
) -> str:
    """Execute an LLM chat completion call with exponential backoff retry logic.

    Args:
        messages: List of message dictionaries (e.g. [{'role': 'user', 'content': '...'}]).
        model: Model name. If omitted, defaults to LLM_MODEL from environment or 'llama-3.3-70b-versatile'.
        temperature: Sampling temperature (default: 0.2).
        client: Optional OpenAI client instance.
        **kwargs: Additional parameters passed to client.chat.completions.create.

    Returns:
        str: Response text from the model.
    """
    active_client = client or get_groq_client()
    target_model = model or os.getenv("LLM_MODEL", DEFAULT_MODEL)

    response = active_client.chat.completions.create(
        model=target_model,
        messages=messages,
        temperature=temperature,
        **kwargs,
    )

    choice = response.choices[0]
    return choice.message.content or ""


def _strip_markdown_code_fences(content: str) -> str:
    """Strip markdown code fence blocks (```json ... ``` or ``` ... ```) from a string."""
    trimmed = content.strip()
    # Match markdown code fences like ```json ... ``` or ``` ... ```
    pattern = r"^```(?:json)?\s*([\s\S]*?)\s*```$"
    match = re.match(pattern, trimmed, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return trimmed


def call_llm_json(
    messages: List[Dict[str, Any]],
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_retries: int = 2,
    client: Optional[OpenAI] = None,
    **kwargs: Any,
) -> Union[Dict[str, Any], List[Any]]:
    """Execute an LLM call and parse the response as JSON.

    If parsing fails, re-prompts the model with instructions to output only valid JSON,
    up to max_retries times.

    Args:
        messages: List of message dictionaries.
        model: Model name. If omitted, defaults to LLM_MODEL from environment.
        temperature: Sampling temperature (default: 0.0 for structured JSON).
        max_retries: Maximum number of re-prompt attempts if JSON parsing fails (default: 2).
        client: Optional OpenAI client instance.
        **kwargs: Additional parameters passed to call_llm.

    Returns:
        dict or list: Parsed JSON data from the model.

    Raises:
        ValueError: If valid JSON cannot be obtained after max_retries attempts.
    """
    conversation = list(messages)
    last_raw_response = ""
    last_error: Optional[Exception] = None

    for attempt in range(max_retries + 1):
        if attempt > 0:
            conversation.append({"role": "assistant", "content": last_raw_response})
            conversation.append(
                {
                    "role": "user",
                    "content": (
                        f"The previous response could not be parsed as valid JSON (Error: {last_error}). "
                        "Please provide ONLY the raw, valid JSON object or array without any additional text, "
                        "markdown explanation, or commentary."
                    ),
                }
            )

        raw_response = call_llm(
            messages=conversation,
            model=model,
            temperature=temperature,
            client=client,
            **kwargs,
        )
        last_raw_response = raw_response
        cleaned_text = _strip_markdown_code_fences(raw_response)

        try:
            return json.loads(cleaned_text)
        except (json.JSONDecodeError, TypeError) as exc:
            last_error = exc

    raise ValueError(
        f"Failed to parse valid JSON from LLM after {max_retries} retries. "
        f"Last error: {last_error}. Last raw response: {last_raw_response}"
    )
