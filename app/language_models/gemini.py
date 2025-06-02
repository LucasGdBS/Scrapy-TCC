from pathlib import Path
from language_models.llm import LLM
from google import genai
from google.genai import types


class Gemini(LLM):
    def __init__(self, system_instruction: str, api_key: str, model: str = "gemini-2.5-flash-preview-05-20"):
        self.system_instruction = system_instruction
        self.__api_key = api_key
        self.__model = model
        

    def generate_code(self, prompt: str, static_site_url: str, file_path: Path):
        client = genai.Client(
            api_key=self.__api_key,
        )

        contents = [types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f'{self.system_instruction}\n{prompt}\nhtml:{static_site_url}')
            ]
        )]

        generate_content_config = types.GenerateContentConfig(
            response_mime_type="text/plain",
        )

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(
                f"# Site URL: {static_site_url}\n# Prompt: {prompt}\n"
            )
            for chunk in client.models.generate_content_stream(
                model=self.__model,
                contents=contents,
                config=generate_content_config,
            ):
                file.write(chunk.text)


