from abc import abstractmethod, ABC
from pathlib import Path
import importlib.util
import traceback

class LLM(ABC):
    @classmethod
    @abstractmethod
    def generate_code(self, prompt: str, static_site_url: str) -> str | None:
        """
        Generate code based on the provided prompt and static site URL.
        This method should be implemented by subclasses. The generated code must include a function named 'run'.
        Args:
            prompt (str): The prompt describing the code to be generated.
            static_site_url (str): The URL of the static site to be used as context.
        Returns:
            str | None: The generated code as a string, or None if code generation fails.
        """
        pass

    def validate_scraper(self, file_path: Path) -> tuple[bool, str]:
        try:
            spec = importlib.util.spec_from_file_location("scraper_module", file_path)
            scraper_module = importlib.util.module_from_spec(spec)            
            spec.loader.exec_module(scraper_module)

            if not hasattr(scraper_module, "run"):
                return False, "Function 'run' not detected in the code"
            
            result = scraper_module.run()

            if result and isinstance(result, (list, dict, str)):
                return True, ""
            else:
                return False, "The code executed but returned empty or unexpected result"
        
        except Exception:
            return False, traceback.format_exc()
    # TODO: não enviar a URL, e sim o HTML limpo
    def generate_and_validate(
            self, prompt: str,
            static_site_url: str,
            file_path: Path,
            max_attempts: int = 3
    ) -> str | None:
        initial_prompt = prompt

        for _ in range(max_attempts):
            code = self.generate_code(prompt, static_site_url)

            header = f"# Site URL: {static_site_url}\n# Prompt: {initial_prompt}\n\n"
            full_code = header + code
            file_path.write_text(full_code, encoding='utf-8')

            is_valid, error_message = self.validate_scraper(file_path)

            if is_valid:
                print("✅ Code generated successfully!")
                return True
            
            print(f"❌ Invalid code. Error:\n{error_message}")

            prompt += f"\n\nThe generated code had the following error:\n{error_message}\nPlease fix and generate again, keeping the initial objective."
        
        print("🚫 Failed to generate valid code after several attempts.")
        return False