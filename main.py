from decouple import config as env
from pathlib import Path
import importlib.util
import hashlib
from google import genai
from google.genai import types
from functools import wraps
import time

GEMINI_API_KEY = env('GEMINI_API_KEY')

def timeit(func):
    """
    Decorator that measures and prints the execution time of the decorated function.
    Args:
        func (callable): The function whose execution time is to be measured.
    Returns:
        callable: A wrapper function that executes the original function, prints its execution time, and returns its result.
    Example:
        @timeit
        def my_function():
            # function body
    """
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'\033[93mFunction {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds\033[0m')
        return result
    return timeit_wrapper

def generate_code(prompt: str, static_site_url: str, file_path: Path):
    client = genai.Client(
        api_key=GEMINI_API_KEY,
    )

    model = "gemini-2.5-flash-preview-05-20"
    system_instruction = (
        "You are a Python code generator.\n"
        "Respond exclusively with code.\n"
        "No comments, no explanations, no markdown, no extra text.\n"
        "Only pure, valid, and executable code.\n"
        "Create a function named 'run' that executes the code and returns the data.\n"
        "Do not forget to set the User-Agent header.\n"
        "Return the data in dict format.\n"
        "Generate scraping code for:"
    )

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=f"{system_instruction}\n{prompt}\nhtml:{static_site_url}"
                )
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(
            f"# Site URL: {static_site_url}\n# Prompt: {prompt}\n"
        )
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            file.write(chunk.text)


def generate_hash(url: str, prompt: str):
    unique_key = url + prompt
    return hashlib.sha256(unique_key.encode()).hexdigest()

def load_and_run_scrapper(filepath: Path):
    spec = importlib.util.spec_from_file_location("scrapper", filepath)
    scraper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scraper)
    return scraper.run()

# Script
def script():
    static_site_url = input("Coloque a URL do site estatico que você quer raspar: ")
    extract_prompt = input("Explique quais dados você quer: ")

    hash = generate_hash(static_site_url, extract_prompt)
    file_path = Path(f'./scrapers/{hash}.py')

    if file_path.exists():
        result = load_and_run_scrapper(file_path)
        print(result)
    else:
        try_again = 'Y'
        while try_again == 'Y':
            generate_code(file_path=file_path, static_site_url=static_site_url, prompt=extract_prompt)
            result = load_and_run_scrapper(file_path)
            print(result)

            try_again = input("Deseja criar outro script? Y/N: ").upper()

script()
