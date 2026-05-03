from src.services.llm_call import LLMCall

class Scout:
    def __init__(self, llm: LLMCall):
        self.llm = llm
        self.system_instruction = "You are a highly critical yet cautious financial analyst. Find the HIDDEN DOWNSIDE in every news story."

    async def get_latest(self, news_text):
        # return await self.llm.get_response(self.system_instruction, news_text)
        pass