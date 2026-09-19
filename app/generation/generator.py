from app.generation.prompts import SYSTEM_PROMPT, build_generation_prompt
from app.llm.client import LLMClient


class Generator:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def generate(self, message: str, results: list) -> str:
        if not results:
            return (
                "The available documents do not provide enough information "
                "to answer this question."
            )

        return self.llm_client.generate(
            prompt=build_generation_prompt(message, results),
            system_prompt=SYSTEM_PROMPT,
        )
