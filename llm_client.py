# LLM Abstraction Layer
from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel
from openai import OpenAI
from config import settings


class LLMResponse(BaseModel):
    """Standard response format for all LLM providers"""
    text: str
    model: str
    tokens_used: Optional[int] = None


class BaseLLM(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def invoke(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """
        Invoke the LLM with a prompt.

        Args:
            user_prompt: The user's prompt/question
            system_prompt: Optional system prompt for behavior control

        Returns:
            LLMResponse with the generated text
        """
        pass


class OpenAILLM(BaseLLM):
    """OpenAI implementation using GPT-4o-mini for cost efficiency"""

    def __init__(self, model: str = "gpt-4o-mini", api_key: Optional[str] = None):
        """
        Initialize OpenAI client.

        Args:
            model: Model to use (default: gpt-4o-mini for cost efficiency)
            api_key: OpenAI API key (defaults to config)
        """
        self.model = model
        self.client = OpenAI(api_key=api_key or settings.openai_key)

    def invoke(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """
        Invoke OpenAI API.

        Args:
            user_prompt: The user's prompt
            system_prompt: Optional system prompt

        Returns:
            LLMResponse with generated text
        """
        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        messages.append({
            "role": "user",
            "content": user_prompt
        })

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.0  # Deterministic for compliance use case
            )

            return LLMResponse(
                text=response.choices[0].message.content,
                model=self.model,
                tokens_used=response.usage.total_tokens if response.usage else None
            )
        except Exception as e:
            # Graceful degradation - return error message
            return LLMResponse(
                text=f"LLM Error: {str(e)}",
                model=self.model,
                tokens_used=None
            )


def get_llm_client(provider: str = "openai", model: Optional[str] = None) -> BaseLLM:
    """
    Factory function to get the appropriate LLM client.

    Args:
        provider: LLM provider ("openai", "claude", etc.)
        model: Specific model to use (provider-specific defaults if None)

    Returns:
        Configured LLM client

    Example:
        llm = get_llm_client("openai", "gpt-4o-mini")
        response = llm.invoke("What is 2+2?", system_prompt="You are a calculator")
    """
    if provider.lower() == "openai":
        return OpenAILLM(model=model or "gpt-4o-mini")
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
