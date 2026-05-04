import os
from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    pass


class Config:
    ALPACA_KEY = os.getenv("ALPACA_KEY")
    ALPACA_SECRET = os.getenv("ALPACA_SECRET")
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    PAPER_TRADING = os.getenv("ALPACA_PAPER", "true").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
