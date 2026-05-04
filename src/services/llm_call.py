import asyncio
from google import genai
from google.genai import errors
from src.utils.config import Config


class LLMCall:
    def __init__(self):
        self.client = genai.Client(api_key=Config.LLM_API_KEY)
        self.model = "gemini-3-flash-preview"

    async def get_response(self, system_instruction: str, user_input: str) -> str:
        prompt = f"{system_instruction}\n\n{user_input}"
        for attempt in range(5):
            try:
                response = await self.client.aio.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
                return response.text
            except errors.ServerError:
                if attempt == 4:
                    raise
                wait = 10 * (attempt + 1)
                print(f"Server busy, retrying in {wait}s...")
                await asyncio.sleep(wait)
