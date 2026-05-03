import google.generativeai as genai
from src.utils.config import Config

class LLMCall:
    def __init__(self):
        genai.configure(api_key=Config.LLM_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    async def get_response(self, system_instruction, user_input):
        prompt = f"{system_instruction}\n\nAnalyze this: {user_input}"
        response = await self.model.generate_content_async(prompt)
        return response.text