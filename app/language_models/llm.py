from abc import abstractmethod, ABC
from pathlib import Path
import importlib.util
import traceback

class LLM(ABC):
    @classmethod
    @abstractmethod
    def generate_code(self, prompt: str, static_site_url: str, file_path: Path) -> str | None:
        pass

    def validate_scraper(self, file_path: Path) -> tuple[bool, str]:
        try:
            spec = importlib.util.spec_from_file_location("scraper_module", file_path)
            scraper_module = importlib.util.module_from_spec(spec)            
            spec.loader.exec_module(scraper_module)

            if not hasattr(scraper_module, "run"):
                return False, "Função 'run' não detectada no código"
            
            result = scraper_module.run()

            if result and isinstance(result, (list, dict, str)):
                return True, ""
            else:
                return False, "O código foi executado mas retornou vazio ou inesperado"
        
        except Exception:
            return False, traceback.format_exc()
    
    def generate_and_validate(
            self, prompt: str,
            static_site_url: str,
            file_path: Path,
            max_attempts: int = 3
    ) -> str | None:
        for _ in range(max_attempts):
            self.generate_code(prompt, static_site_url, file_path)

            is_valid, error_message = self.validate_scraper(file_path)

            if is_valid:
                print("✅ Código gerado com sucesso!")
                return True
            
            print(f"❌ Código inválido. Erro:\n{error_message}")

            prompt += f"\n\nO código gerado apresentou o seguinte erro:\n{error_message}\nCorrija e gere novamente, mantendo o objetivo inicial."
        
        print("🚫 Falha ao gerar um código válido após várias tentativas.")
        return False