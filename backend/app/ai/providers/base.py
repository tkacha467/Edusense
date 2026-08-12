"""Base LLM Provider abstract interface."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, Optional


class BaseLLMProvider(ABC):
    """Abstract interface for LLM providers (Gemini, OpenAI, Claude, Llama)."""

    @abstractmethod
    def generate_completion(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        json_mode: bool = False,
        max_tokens: int = 2048
    ) -> str:
        """Generates a text or structured JSON completion."""
        pass

    @abstractmethod
    def generate_stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7
    ) -> Generator[str, None, None]:
        """Streams completion tokens."""
        pass
