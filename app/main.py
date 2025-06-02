from decouple import config as env
from language_models.gemini import Gemini
from agents.scrapy import Scrapy

GEMINI_API_KEY = env('GEMINI_API_KEY')
gemini = Gemini(
    api_key=GEMINI_API_KEY,
    system_instruction=(
        "You are a Python code generator.\n"
        "Respond exclusively with code.\n"
        "No comments, no explanations, no markdown, no extra text.\n"
        "Only pure, valid, and executable code.\n"
        "Create a function named 'run' that executes the code and returns the data.\n"
        "Do not forget to set the User-Agent header.\n"
        "Return the data in dict format.\n"
        "Generate scraping code for:"
    )
)

scrapy = Scrapy(gemini)

# Script
def main():
    static_site_url = input("Coloque a URL do site estatico que você quer raspar: ")
    extract_prompt = input("Explique quais dados você quer: ")

    scrapy.scrapy(static_site_url, extract_prompt)

main()
