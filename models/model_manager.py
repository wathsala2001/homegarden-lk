import os
from typing import Any, Optional

from dotenv import load_dotenv
from groq import Groq


# Load private values from the .env file.
load_dotenv()


class ModelConfigurationError(Exception):
    """
    Raised when an API key or model name is missing.
    """


class ModelRequestError(Exception):
    """
    Raised when a Groq model request fails.
    """


def get_required_value(name: str) -> str:
    """
    Read one required environment variable.
    """

    value = os.getenv(name, "").strip()

    if not value:
        raise ModelConfigurationError(
            f"Missing environment value: {name}"
        )

    return value


def create_groq_client() -> Groq:
    """
    Create the Groq client using the private API key.
    """

    api_key = get_required_value("GROQ_API_KEY")

    return Groq(api_key=api_key)


def call_groq_model(
    model_name: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 1000,
    temperature: float = 0.1,
    reasoning_format: Optional[str] = None,
    reasoning_effort: Optional[str] = None,
    response_format: Optional[dict[str, Any]] = None,
) -> str:
    """
    Send a request to one selected Groq model.
    """

    try:
        client = create_groq_client()

        request_options: dict[str, Any] = {
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "temperature": temperature,
            "max_completion_tokens": max_tokens,
        }

        if reasoning_format is not None:
            request_options["reasoning_format"] = (
                reasoning_format
            )

        if reasoning_effort is not None:
            request_options["reasoning_effort"] = (
                reasoning_effort
            )

        if response_format is not None:
            request_options["response_format"] = (
                response_format
            )

        response = client.chat.completions.create(
            **request_options
        )

        if not response.choices:
            raise ModelRequestError(
                "The model returned no response choices."
            )

        content: Optional[str] = (
            response.choices[0].message.content
        )

        if not content or not content.strip():
            raise ModelRequestError(
                "The model returned an empty final response."
            )

        return content.strip()

    except ModelConfigurationError:
        raise

    except ModelRequestError:
        raise

    except Exception as error:
        raise ModelRequestError(
            f"Groq request failed: {error}"
        ) from error


def call_router_model(
    system_prompt: str,
    user_prompt: str,
) -> str:
    """
    Model 1:
    Fast question routing and planning.
    """

    return call_groq_model(
        model_name=get_required_value("ROUTER_MODEL"),
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=700,
        temperature=0.1,
    )


def call_rerank_model(
    system_prompt: str,
    user_prompt: str,
) -> str:
    """
    Model 2:
    Check and re-rank retrieved gardening evidence.
    """

    return call_groq_model(
        model_name=get_required_value("RERANK_MODEL"),
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=2200,
        temperature=0.0,
        reasoning_format="hidden",
        reasoning_effort="low",
        response_format={
            "type": "json_object",
        },
    )


def call_final_model(
    system_prompt: str,
    user_prompt: str,
    json_mode: bool = False,
) -> str:
    """
    Model 3:
    Generate the final answer and perform reflection.
    """

    selected_response_format = None

    if json_mode:
        selected_response_format = {
            "type": "json_object",
        }

    return call_groq_model(
        model_name=get_required_value("FINAL_MODEL"),
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=3000,
        temperature=0.1,
        reasoning_format="hidden",
        reasoning_effort="low",
        response_format=selected_response_format,
    )


def get_model_configuration() -> dict[str, str]:
    """
    Return the three model names without revealing the API key.
    """

    return {
        "router_model": os.getenv(
            "ROUTER_MODEL",
            "Not configured",
        ),
        "rerank_model": os.getenv(
            "RERANK_MODEL",
            "Not configured",
        ),
        "final_model": os.getenv(
            "FINAL_MODEL",
            "Not configured",
        ),
    }