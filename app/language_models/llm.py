from abc import abstractmethod, ABC
from pathlib import Path

class LLM(ABC):
    @classmethod
    @abstractmethod
    def generate_code(self, prompt: str, static_site_url: str, file_path: Path) -> str | None:
        pass