# QuantForge Full AI Agent — Live Market Autonomous Alpha-Signal Discoverer

QuantForge is a full LLM-powered AI agent system for autonomous alpha research. It follows the exact architecture:

```text
[Start: User Goal]
        ↓
1. Expression Generator  ── Math String ──► 2. Backtest Sandbox
        ▲                                      ↓
        │ Mutation Instructions          Sharpe / Fitness / Turnover
        │                                      ↓
4. Mathematical Critic ◄── Failed Data ── 3. Evaluation Gate
                                               ↓ pass
                                      Export Validated Alpha
```

## What makes this a real AI agent

The two reasoning nodes are now powered by an LLM:

- **Node 1: Expression Generator** calls OpenAI or Gemini and generates a strict alpha expression.
- **Node 4: Mathematical Critic** calls OpenAI or Gemini and diagnoses failed metrics, then emits a mutation instruction.

The safety-critical parts remain deterministic:

- **Node 2: Backtest Sandbox** executes the expression using Pandas/NumPy on real OHLCV data.
- **Node 3: Evaluation Gate** decides using hard thresholds: Sharpe, fitness, and turnover.

The LLM can propose and critique, but it cannot approve an alpha. Only the deterministic gate can approve.

## What makes this real market testing, not simulation

The production path does **not** generate fake or duplicate candles. During alpha testing it fetches latest/live OHLCV bars at runtime from:

- `binance` through `ccxt` for crypto, for example `BTC/USDT ETH/USDT SOL/USDT`
- `yahoo` through `yfinance` for stocks/ETFs, for example `AAPL MSFT NVDA SPY`
- `csv` or `parquet` if you provide your own real vendor data

If market data or the LLM key is missing, the project fails clearly. It does not silently replace the real system with fake data.

---

## 1. Install

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Mac/Linux
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 2. Create `.env`

Copy `.env.example` to `.env`.

### OpenAI mode

```env
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4o-mini
```

### Gemini mode

```env
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

For a full AI-agent demo, use `openai` or `gemini`. The `deterministic` provider is included only for tests/offline debugging.

---

## 3. Best real-time demo command: Binance crypto

Crypto trades 24/7, so this is the best live demo.

```bash
python apps.py \
  --llm-provider openai \
  --provider binance \
  --symbols BTC/USDT ETH/USDT SOL/USDT BNB/USDT XRP/USDT \
  --timeframe 1m \
  --limit 1000 \
  --max-mutations 5 \
  --goal "Find a short-term mean reversion alpha using price, returns, and volume"
```

Gemini version:

```bash
python apps.py \
  --llm-provider gemini \
  --provider binance \
  --symbols BTC/USDT ETH/USDT SOL/USDT BNB/USDT XRP/USDT \
  --timeframe 1m \
  --limit 1000 \
  --max-mutations 5 \
  --goal "Find a short-term mean reversion alpha using price, returns, and volume"
```

---

## 4. Stock-market command

```bash
python apps.py \
  --llm-provider openai \
  --provider yahoo \
  --symbols AAPL MSFT NVDA SPY \
  --period 5d \
  --interval 1m \
  --goal "Find intraday mean reversion alpha using volume and returns"
```

If the stock market is closed, the latest market candle will be the latest exchange-provided candle, not a fake current-time candle.

---

## 5. Run with your own real data

Your CSV/parquet must contain:

```text
timestamp,symbol,open,high,low,close,volume
```

```bash
python apps.py --llm-provider openai --provider csv --data-file data/my_market_data.csv --goal "Find mean reversion alpha"
python apps.py --llm-provider openai --provider parquet --data-file data/my_market_data.parquet --goal "Find mean reversion alpha"
```

---

## 6. Expected node trace

```text
NODE 1: Expression Generator (LLM)
NODE 2: Backtest Sandbox (Deterministic)
NODE 3: Evaluation Gate (Deterministic Router)
NODE 4: Mathematical Critic (LLM)
NODE 1: Expression Generator (LLM)
NODE 2: Backtest Sandbox (Deterministic)
NODE 3: Evaluation Gate (Deterministic Router)
EXPORT: Validated Alpha
```

---

## 7. Output

Validated alphas are exported to:

```text
outputs/validated_alphas.jsonl
```

Each record contains:

- runtime timestamp
- latest market candle timestamp
- user goal
- final expression
- Sharpe
- fitness
- turnover
- expression history
- critique history
- node trace
- LLM provider/model

---

## 8. Run tests

Tests use the deterministic test provider so they do not require paid API keys.

```bash
pytest -q
```

---

## Interview explanation

> QuantForge is a full LLM-powered autonomous quant research agent. The LLM generates alpha expressions and critiques failed results, but it cannot approve anything. A deterministic vectorized backtest engine runs the math on live/latest market data, and a hard evaluation gate decides using Sharpe, fitness, and turnover. This prevents LLM hallucination because every generated idea must survive mathematical verification.


## API-key fallback mode

QuantForge now supports both full AI-agent mode and the original partial/deterministic agent mode.

Default behavior:

```bash
python apps.py --llm-provider auto --llm-fallback auto --provider binance --symbols BTC/USDT ETH/USDT SOL/USDT --timeframe 1m --limit 1000 --goal "Find a short-term mean reversion alpha using price, returns, and volume"
```

How it works:

- If `OPENAI_API_KEY` exists, Node 1 and Node 4 use OpenAI.
- Else if `GOOGLE_API_KEY` or `GEMINI_API_KEY` exists, Node 1 and Node 4 use Gemini.
- Else QuantForge falls back to the original partial-agent mode, where Node 1 and Node 4 are deterministic rule-based agents.
- Market data is never faked. If Binance/Yahoo/vendor data cannot be fetched, the run fails.

Strict full-AI mode:

```bash
python apps.py --llm-provider openai --llm-fallback strict --provider binance --symbols BTC/USDT ETH/USDT SOL/USDT --timeframe 1m --limit 1000 --goal "Find a short-term mean reversion alpha"
```

Use strict mode when you want the project to fail if the LLM API key is missing. Use auto mode when you want it to remain runnable without paid API keys.
