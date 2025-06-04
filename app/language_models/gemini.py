from language_models.llm import LLM
from google import genai
from google.genai import types
from web_page.web_page import WebPage


class Gemini(LLM):
    def __init__(self, system_instruction: str, api_key: str, model: str = "gemini-2.5-flash-preview-05-20"):
        self.system_instruction = system_instruction
        self.__api_key = api_key
        self.__model = model
        

    def generate_code(self, prompt: str, web_page: WebPage):
        client = genai.Client(
            api_key=self.__api_key,
        )

        contents = [types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=f'{self.system_instruction}\n{prompt}\nurl:{web_page.url}html:{web_page.html}'
                )
            ]
        )]

        generate_content_config = types.GenerateContentConfig(
            response_mime_type="text/plain",
        )

        code = ""
        for chunk in client.models.generate_content_stream(
            model=self.__model,
            contents=contents,
            config=generate_content_config,
        ):
            code += chunk.text
        return code
                


