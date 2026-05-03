from src.services.llm_call import LLMCall

class ProAnalyst:
    def __init__(self, llm: LLMCall):
        self.llm = llm
        self.system_instruction = "You are a growth-focused analyst. Find the HIDDEN UPSIDE in every news story."

    async def analyze(self, news_text):
        return await self.llm.get_response(self.system_instruction, news_text)