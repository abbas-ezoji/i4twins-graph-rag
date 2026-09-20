import re

from app.structure.extractor import StructureExtractor
from app.structure.models import (
    Entity,
    Fact,
    StructuredDocument,
)


class BasicStructureExtractor(StructureExtractor):

    EQUIPMENT_PATTERN = re.compile(
        r"\b[A-Z]{1,5}-\d{1,5}\b"
    )

    PRESSURE_PATTERN = re.compile(
        r"(?P<value>\d+(?:\.\d+)?)\s*"
        r"(?P<unit>bar|psi|kPa|MPa)\b",
        re.IGNORECASE,
    )

    def extract(
        self,
        document_id: str,
        title: str,
        text: str,
    ) -> StructuredDocument:

        entities: list[Entity] = []
        facts: list[Fact] = []

        # --------------------------------------------------
        # Equipment/entity extraction
        # --------------------------------------------------

        equipment_matches = self.EQUIPMENT_PATTERN.findall(text)

        seen_entities: set[str] = set()

        for value in equipment_matches:
            normalized = value.upper()

            if normalized in seen_entities:
                continue

            seen_entities.add(normalized)

            entities.append(
                Entity(
                    text=value,
                    entity_type="equipment",
                    normalized=normalized,
                )
            )

        # --------------------------------------------------
        # Simple pressure extraction
        # --------------------------------------------------

        pressure_matches = self.PRESSURE_PATTERN.finditer(text)

        for match in pressure_matches:
            value = float(match.group("value"))
            unit = match.group("unit")

            facts.append(
                Fact(
                    subject=(
                        entities[0].normalized
                        if entities
                        else "unknown"
                    ),
                    predicate="pressure",
                    value=value,
                    unit=unit,
                    source_text=match.group(0),
                )
            )

        return StructuredDocument(
            document_id=document_id,
            title=title,
            text=text,
            entities=entities,
            facts=facts,
            metadata={
                "extractor": "basic",
                "extractor_version": "0.1",
            },
        )