from dataclasses import dataclass


@dataclass(frozen=True)
class PromptTemplate:
    template: str

    def format(self, **kwargs) -> str:
        return self.template.format(**kwargs)


SCOUT_SYSTEM = (
    "You are a financial news analyst. Synthesize the provided news articles into a "
    "clear, factual digest. Focus on earnings, product launches, regulatory news, "
    "partnerships, and market impact. Do not speculate."
)

SCOUT_DIGEST = PromptTemplate(
    "Summarize the following news articles about {symbol} in 3-5 sentences.\n\n"
    "Articles:\n{articles}"
)

PROS_SYSTEM = (
    "You are an optimistic equity analyst. Your job is to find the strongest "
    "buy arguments in any given news story."
)

PROS_ARGUMENTS = PromptTemplate(
    "Example:\n"
    "News: Apple reported 15% revenue growth driven by strong iPhone sales and "
    "services expansion.\n"
    "Bullish arguments:\n"
    "- Strong consumer demand signals continued market leadership\n"
    "- Services segment diversification reduces hardware dependency\n"
    "- Revenue growth outpaces analyst expectations, suggesting upward price pressure\n\n"
    "Now analyze the following news about {symbol} step by step:\n\n"
    "Step 1: Identify the key positive signals in the news.\n"
    "Step 2: Explain how each signal could drive the stock price higher.\n"
    "Step 3: List 3-5 distinct bullish arguments as bullet points.\n\n"
    "News digest:\n{digest}\n\n"
    "Bullish arguments:"
)

CONS_SYSTEM = (
    "You are a skeptical risk analyst. Your job is to identify the strongest "
    "arguments against buying a stock, including hidden risks."
)

CONS_ARGUMENTS = PromptTemplate(
    "Example 1:\n"
    "News: Microsoft reported cloud revenue growth of 20%, beating estimates.\n"
    "Bearish arguments:\n"
    "- Growth deceleration from prior quarter's 28% raises sustainability concerns\n"
    "- Increasing capital expenditures compress near-term margins\n"
    "- Competitive pressure from AWS and Google Cloud could erode market share\n\n"
    "Example 2:\n"
    "News: Tesla delivered record vehicles in Q4 but gross margins narrowed.\n"
    "Bearish arguments:\n"
    "- Margin compression signals pricing power erosion\n"
    "- Record deliveries driven by discounts, not organic demand\n"
    "- Rising EV competition from legacy automakers threatens market share\n\n"
    "Now analyze the following news about {symbol} step by step:\n\n"
    "Step 1: Identify the key risks or negative signals hidden in the news.\n"
    "Step 2: Explain how each risk could push the stock price lower.\n"
    "Step 3: List 3-5 distinct bearish arguments as bullet points.\n\n"
    "News digest:\n{digest}\n\n"
    "Bearish arguments:"
)
