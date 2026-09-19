from dataclasses import dataclass

from app.generation.generator import Generator


class FakeLLM:
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        assert "P-200" in prompt
        assert system_prompt
        return "The answer is supported by DOC-01."


@dataclass
class Result:
    document_id: str
    title: str
    text: str
    score: float


def test_generation():
    generator = Generator(FakeLLM())
    results = [
        Result(
            document_id="DOC-01",
            title="Pump specification",
            text="P-200 maximum pressure is 16 bar.",
            score=0.95,
        )
    ]

    answer = generator.generate(
        "What is the maximum pressure of P-200?",
        results,
    )

    assert "DOC-01" in answer
