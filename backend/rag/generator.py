from __future__ import annotations

from backend.config import Settings


class GroqAnswerGenerator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY is not set.")

        try:
            from groq import Groq
        except ImportError as exc:
            raise ImportError("Install groq to run LLM generation.") from exc

        self.client = Groq(api_key=settings.groq_api_key)

    def generate(self, messages: list[dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=self.settings.groq_model_name,
            messages=messages,
            temperature=self.settings.llm_temperature,
            max_tokens=self.settings.llm_max_tokens,
        )
        return response.choices[0].message.content.strip()
