"""
LLM Service Abstraction Layer

Centralizes all LLM interactions. Swap providers here without touching agent code.
Supports: OpenAI, Anthropic, Azure OpenAI, Ollama, Gemini, etc.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from enum import Enum
import os
from dataclasses import dataclass


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    OLLAMA = "ollama"
    GEMINI = "gemini"
    GROQ = "groq"
    COHERE = "cohere"


@dataclass
class LLMResponse:
    """Standardized LLM response."""
    content: str
    tokens_used: Optional[int] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class LLMConfig:
    """LLM Configuration."""
    provider: LLMProvider
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    timeout: int = 30
    extra_params: Optional[Dict[str, Any]] = None


class BaseLLMService(ABC):
    """Abstract base class for LLM services."""

    def __init__(self, config: LLMConfig):
        """Initialize LLM service."""
        self.config = config
        self.provider = config.provider.value

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate response from LLM.
        
        Args:
            prompt: Main prompt
            system_prompt: Optional system instructions
            **kwargs: Provider-specific parameters
            
        Returns:
            LLMResponse with content and metadata
        """
        pass

    @abstractmethod
    async def generate_streaming(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        """
        Stream response from LLM (async generator).
        
        Args:
            prompt: Main prompt
            system_prompt: Optional system instructions
            **kwargs: Provider-specific parameters
            
        Yields:
            str chunks of response content
        """
        pass

    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        pass


class OpenAIService(BaseLLMService):
    """OpenAI LLM Service."""

    def __init__(self, config: LLMConfig):
        """Initialize OpenAI service."""
        super().__init__(config)
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=config.api_key or os.getenv("OPENAI_API_KEY"))
        except ImportError:
            raise ImportError("openai package required: pip install openai")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response from OpenAI API."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            timeout=self.config.timeout,
            **(self.config.extra_params or {}),
            **kwargs
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            tokens_used=response.usage.total_tokens if response.usage else None,
            model=response.model,
            provider=self.provider,
            raw_response=response.model_dump() if hasattr(response, "model_dump") else None
        )

    async def generate_streaming(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        """Stream response from OpenAI API."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        with await self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            stream=True,
            timeout=self.config.timeout,
            **(self.config.extra_params or {}),
            **kwargs
        ) as stream:
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens using tiktoken."""
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.config.model)
            return len(encoding.encode(text))
        except ImportError:
            # Rough estimate: 1 token ≈ 4 characters
            return len(text) // 4


class AnthropicService(BaseLLMService):
    """Anthropic Claude LLM Service."""

    def __init__(self, config: LLMConfig):
        """Initialize Anthropic service."""
        super().__init__(config)
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=config.api_key or os.getenv("ANTHROPIC_API_KEY"))
        except ImportError:
            raise ImportError("anthropic package required: pip install anthropic")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response from Anthropic API."""
        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens or 1024,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.temperature,
            timeout=self.config.timeout,
            **(self.config.extra_params or {}),
            **kwargs
        )

        return LLMResponse(
            content=response.content[0].text if response.content else "",
            tokens_used=response.usage.output_tokens if response.usage else None,
            model=response.model,
            provider=self.provider,
            raw_response=response.model_dump() if hasattr(response, "model_dump") else None
        )

    async def generate_streaming(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        """Stream response from Anthropic API."""
        with self.client.messages.stream(
            model=self.config.model,
            max_tokens=self.config.max_tokens or 1024,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.temperature,
            timeout=self.config.timeout,
            **(self.config.extra_params or {}),
            **kwargs
        ) as stream:
            for text in stream.text_stream:
                yield text

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation for Anthropic."""
        # Anthropic uses roughly 75 tokens per 500 characters
        return int((len(text) / 500) * 75)


class LLMFactory:
    """Factory for creating LLM service instances."""

    _providers = {
        LLMProvider.OPENAI: OpenAIService,
        LLMProvider.ANTHROPIC: AnthropicService,
        # Add more providers as needed
    }

    @classmethod
    def create_service(cls, config: LLMConfig) -> BaseLLMService:
        """
        Create LLM service based on config.
        
        Args:
            config: LLMConfig with provider and model details
            
        Returns:
            Appropriate BaseLLMService subclass instance
            
        Raises:
            ValueError: If provider not supported
        """
        service_class = cls._providers.get(config.provider)
        if not service_class:
            supported = ", ".join([p.value for p in cls._providers.keys()])
            raise ValueError(
                f"Provider '{config.provider.value}' not supported. "
                f"Supported: {supported}"
            )
        return service_class(config)

    @classmethod
    def register_provider(
        cls,
        provider: LLMProvider,
        service_class: type
    ):
        """Register custom LLM provider."""
        cls._providers[provider] = service_class


# Global singleton instance (lazy-loaded)
_llm_service: Optional[BaseLLMService] = None


def get_llm_service() -> BaseLLMService:
    """Get or create global LLM service instance."""
    global _llm_service
    
    if _llm_service is None:
        # Load configuration from environment
        provider_str = os.getenv("LLM_PROVIDER", "openai").lower()
        provider = LLMProvider(provider_str)
        
        config = LLMConfig(
            provider=provider,
            model=os.getenv("LLM_MODEL", "gpt-4"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4000")) if os.getenv("LLM_MAX_TOKENS") else None,
            api_key=os.getenv("LLM_API_KEY"),
            api_base=os.getenv("LLM_API_BASE"),
            timeout=int(os.getenv("LLM_TIMEOUT", "30"))
        )
        
        _llm_service = LLMFactory.create_service(config)
    
    return _llm_service


def set_llm_service(service: BaseLLMService) -> None:
    """Override global LLM service instance (useful for testing)."""
    global _llm_service
    _llm_service = service


def reset_llm_service() -> None:
    """Reset global LLM service (useful for testing)."""
    global _llm_service
    _llm_service = None
