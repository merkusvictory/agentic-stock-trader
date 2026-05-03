import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ALPACA_KEY = os.getenv("ALPACA_KEY")
    ALPACA_SECRET = os.getenv("ALPACA_SECRET")
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    PAPER_TRADING = True 
    LOG_LEVEL = "INFO"