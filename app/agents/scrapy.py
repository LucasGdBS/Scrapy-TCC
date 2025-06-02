from language_models.llm import LLM
from pathlib import Path
import importlib.util
import hashlib

class Scrapy:
    def __init__(self, llm: LLM, folder: Path | str = Path(f'./scrapers')):
        self.llm = llm
        self.folder = Path(folder)

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
            result = self.__load_and_run_func(file_path)
            print(result)
        else:
            try_again = 'Y'
            while try_again == 'Y':
                self.llm.generate_and_validate(file_path=file_path, static_site_url=static_site_url, prompt=extract_prompt)
                result = self.__load_and_run_func(file_path)
                print(result)

                try_again = input("Deseja criar outro script? Y/N: ").upper()
    
