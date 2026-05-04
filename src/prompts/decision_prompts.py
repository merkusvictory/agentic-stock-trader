from src.prompts.argument_prompts import PromptTemplate


JUDGE_SYSTEM = (
    "You are an impartial senior portfolio manager. Your job is to weigh bullish and "
    "bearish arguments objectively and make a clear trading decision."
)

JUDGE_PROMPT = PromptTemplate(
    "You are reviewing arguments about {symbol}. Think step by step:\n\n"
    "Step 1: Summarize the bull case in one sentence.\n"
    "Step 2: Summarize the bear case in one sentence.\n"
    "Step 3: Weigh the strength of each side.\n"
    "Step 4: State your decision and how confident you are (0.0 to 1.0).\n\n"
    "Bull case:\n{pros}\n\n"
    "Bear case:\n{cons}\n\n"
    "Respond in exactly this format:\n"
    "ACTION: BUY or HOLD or SELL\n"
    "CONFIDENCE: 0.XX\n"
    "REASONING: one or two sentences"
)

EVALUATOR_SYSTEM = (
    "You are a trading performance analyst. Review a completed trade and give honest, "
    "actionable feedback on what drove the outcome."
)

EVALUATOR_PROMPT = PromptTemplate(
    "Trade summary for {symbol}:\n"
    "- Action taken: {action}\n"
    "- Entry price: ${entry_price:.2f}\n"
    "- Current price: ${current_price:.2f}\n"
    "- PnL: {pnl_pct:.2f}%\n\n"
    "Based on this outcome:\n"
    "1. Was this a good trade given what was known at the time?\n"
    "2. What signals were missed or over-weighted?\n"
    "3. List 2-3 specific adjustments for future decisions.\n\n"
    "Respond in exactly this format:\n"
    "VERDICT: one sentence assessment\n"
    "ADJUSTMENTS:\n"
    "- adjustment one\n"
    "- adjustment two\n"
    "- adjustment three"
)
