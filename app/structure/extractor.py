from abc import ABC, abstractmethod

from app.structure.models import StructuredDocument


class StructureExtractor(ABC):

    @abstractmethod
    def extract(
        self,
        document_id: str,
        title: str,
        text: str,
    ) -> StructuredDocument:
        raise NotImplementedError