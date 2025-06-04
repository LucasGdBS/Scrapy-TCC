from language_models.llm import LLM
from web_page.web_page import WebPage
from pathlib import Path
import importlib.util
import hashlib

# TODO: Trocar os prints por logs -> Loguru
class Scrapy:
    def __init__(self, llm: LLM, web_page:WebPage, folder: Path | str = Path(f'./scrapers')):
        self.llm = llm
        self.folder = Path(folder)
        self.web_page = web_page

    def __generate_hash(self, url: str, prompt: str):
        unique_key = url + prompt
        return hashlib.sha256(unique_key.encode()).hexdigest()
    
    def __load_and_run_func(self, filepath: Path):
        spec = importlib.util.spec_from_file_location("scraper", filepath)
        scraper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scraper)
        return scraper.run()

    def scrapy(self, static_site_url: str, extract_prompt: str):
        hash = self.__generate_hash(static_site_url, extract_prompt)
        file_path = self.folder / f'{hash}.py'

        if file_path.exists():
            is_valid, validation_message = self.llm.validate_scraper(file_path)
            if is_valid:
                try:
                    result = self.__load_and_run_func(file_path)
                    print(result)
                    return
                except Exception:
                    print("❌ The validated script failed during execution. Generating a new one.")
            else:
                print(f"⚠️ Existing script is invalid: {validation_message}. Generating a new one.")

        try_again = 'Y'
        while try_again == 'Y':
            is_dynamic = self.web_page.is_dynamic
            self.llm.generate_and_validate(
                file_path=file_path,
                static_site_url=static_site_url,
                prompt=extract_prompt + (' The site is dynamic, so use Sync Playwright.' if is_dynamic else ' The site is static, so use BeatifulSoup and requests')
            )

            result = self.__load_and_run_func(file_path)
            print(result)

            try_again = input("Deseja criar outro script? Y/N: ").strip().upper()
    
