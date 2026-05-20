# QuantForge — Live-Market LLM Alpha Research Agent

> An LLM-powered quantitative research agent that discovers, tests, critiques, and mutates mathematical trading signals using live market data and deterministic backtesting.

---

## What is QuantForge?

QuantForge is a **live-market autonomous alpha-signal discovery system**.

In simple words:

Imagine a quant researcher wants to find a short-term trading signal.

Normally, the researcher has to:

1. Think of a financial hypothesis.
2. Convert that hypothesis into a mathematical formula.
3. Fetch market data.
4. Backtest the formula.
5. Calculate Sharpe, fitness, turnover, drawdown, and returns.
6. Decide whether the signal is useful.
7. Modify the formula if the signal is weak.
8. Repeat the process many times.
9. Export the final alpha only if the statistics are strong.

QuantForge automates this workflow using an AI-agent architecture.

It acts like an autonomous quant research assistant that can:

- Take a user research goal.
- Fetch live/latest market candles from Binance or Yahoo Finance.
- Generate a mathematical alpha expression using an LLM.
- Run the alpha through a deterministic vectorized backtest sandbox.
- Calculate Sharpe, fitness, turnover, cumulative return, and max drawdown.
- Reject weak signals instead of pretending they work.
- Use a mathematical critic agent to diagnose why the alpha failed.
- Mutate the expression and test again.
- Export the alpha only if it passes strict quantitative thresholds.

This project is designed as a **Google/Jane Street-style AI Agent + Quantitative Finance project**, combining LLM agents, LangGraph-style orchestration, live market data, mathematical operators, vectorized backtesting, deterministic evaluation, and closed-loop self-correction.

---

## Why This Project Matters

Most AI projects only do this:

```text
Prompt → LLM → Answer
```

QuantForge goes further.

It connects AI agents with real quantitative verification:

- Live market data
- Mathematical expression generation
- Safe expression parsing
- Vectorized backtesting
- Strict statistical validation
- LLM-based critique and mutation
- Deterministic pass/fail decisioning
- Exportable alpha artifacts

This matters because in finance, an LLM cannot simply say, "this signal looks good."

The signal must be tested against actual market data.

QuantForge follows this principle:

> The LLM can generate and critique alpha ideas, but only the deterministic backtest engine can decide whether an alpha is valid.

That separation between **AI reasoning** and **hard mathematical verification** is what makes the project strong.

---

## Core Idea

```text
User Research Goal
      ↓
Expression Generator Agent
      ↓
Backtest Sandbox
      ↓
Evaluation Gate
      ↓
If failed → Mathematical Critic Agent
      ↓
Mutate Expression
      ↓
Backtest Again
      ↓
If passed → Export Validated Alpha
```

QuantForge does not blindly trust generated formulas.

It follows a strict, evidence-based loop:

1. Generate an alpha expression.
2. Test it on live/latest market data.
3. Calculate quantitative metrics.
4. Apply deterministic thresholds.
5. Reject or mutate the alpha.
6. Export only if the alpha passes.

---

## Architecture

QuantForge has **two execution paths** inside the same architecture.

- If the user provides an API key in `.env`, the Expression Generator and Mathematical Critic run as **LLM-powered agents**.
- If the user does not provide an API key, the system automatically falls back to the original **deterministic partial-agent logic** instead of crashing.
- In both paths, the market-data fetch, backtest sandbox, metrics engine, and evaluation gate remain real and deterministic.

```text
                           [ Start: User Goal ]
                                    │
                                    ▼
                     ┌───────────────────────────┐
                     │ Runtime Mode Resolver      │
                     │ Checks .env / API keys     │
                     └─────────────┬─────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
        ┌───────────────────────┐     ┌────────────────────────┐
        │ API Key Present        │     │ API Key Missing         │
        │ Use Full LLM Agents    │     │ Use Fallback Agents     │
        └───────────┬───────────┘     └────────────┬───────────┘
                    │                              │
                    └──────────────┬───────────────┘
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         LANGGRAPH ORCHESTRATOR                               │
│                                                                              │
│   ┌───────────────────────────┐                  ┌────────────────────────┐  │
│   │ 1. Expression Generator   │ ── Math String ─►│ 2. Backtest Sandbox    │  │
│   │ LLM if key exists         │                  │ Live OHLCV Data        │  │
│   │ Fallback if no key        │                  │ Pandas / NumPy Engine  │  │
│   └─────────────▲─────────────┘                  └───────────┬────────────┘  │
│                 │                                            │               │
│                 │ Mutation Instructions                       │               │
│                 │                                            ▼               │
│   ┌───────────────────────────┐                  ┌────────────────────────┐  │
│   │ 4. Mathematical Critic    │ ◄── Failed Data ─│ 3. Evaluation Gate     │  │
│   │ LLM if key exists         │                  │ Deterministic Router   │  │
│   │ Fallback if no key        │                  │ Sharpe/Fitness/Turnover│  │
│   └───────────────────────────┘                  └───────────┬────────────┘  │
│                                                              │               │
└──────────────────────────────────────────────────────────────┼───────────────┘
                                                               │ Pass
                                                               ▼
                                                     [ Export Validated Alpha ]
```

### Execution Path A: Full LLM Agent Mode

```text
.env contains OPENAI_API_KEY or GOOGLE_API_KEY
        ↓
Expression Generator = LLM-powered alpha formula generation
        ↓
Backtest Sandbox = deterministic live-market test
        ↓
Evaluation Gate = deterministic pass/fail decision
        ↓
Mathematical Critic = LLM-powered failure diagnosis and mutation
```

### Execution Path B: Fallback Partial-Agent Mode

```text
.env missing or API key empty
        ↓
Expression Generator = deterministic fallback formula logic
        ↓
Backtest Sandbox = deterministic live-market test
        ↓
Evaluation Gate = deterministic pass/fail decision
        ↓
Mathematical Critic = deterministic fallback mutation logic
```

The fallback mode only replaces the LLM reasoning nodes. It does **not** replace market data with fake data. The alpha is still tested using live/latest OHLCV candles.

---

## Technical Stack

| Area | Technology |
| --- | --- |
| Agent Workflow | LangGraph-style StateGraph / fallback graph runner |
| LLM Provider | OpenAI / Gemini / deterministic fallback |
| Data Source | Binance live OHLCV, Yahoo Finance latest candles |
| Market Data Engine | ccxt, yfinance |
| Backtesting | Pandas, NumPy |
| Expression Safety | AST-based expression validator |
| State Validation | Pydantic |
| Metrics | Sharpe, fitness, turnover, drawdown, returns |
| Testing | pytest |
| Runtime | Python |
| Output | JSON alpha reports and run reports |
| Local Execution | Python virtual environment |

---

## What QuantForge Does in the Demo

The user gives a goal such as:

```text
Find a short-term mean reversion alpha using price, returns, and volume
```

QuantForge then:

1. Captures the runtime timestamp.
2. Fetches latest Binance 1-minute candles.
3. Freezes the live market snapshot for that run.
4. Sends the goal to the Expression Generator.
5. Generates an alpha expression such as:

```text
-rank(decay_linear(ts_rank(close, 10), 20))
```

6. Runs the expression on real OHLCV data.
7. Calculates metrics such as:

```text
Sharpe
Fitness
Turnover
Average bar return
Cumulative return
Max drawdown
Latest market timestamp
```

8. Routes through the Evaluation Gate.
9. If the alpha fails, the Mathematical Critic suggests a mutation.
10. The loop repeats until the alpha passes or max mutations are reached.

---

## Project Features

### 1. Live Market Data Testing

QuantForge can fetch live/latest candles from Binance.

Example:

```bash
python apps.py --llm-provider auto --llm-fallback auto --provider binance --symbols BTC/USDT ETH/USDT SOL/USDT BNB/USDT XRP/USDT --timeframe 1m --limit 1000 --goal "Find a short-term mean reversion alpha using price, returns, and volume"
```

If 5 symbols are used with 1000 candles each, the sandbox receives:

```text
5 symbols × 1000 candles = 5000 market rows
```

This is real market data, not synthetic or duplicated fake data.

---

### 2. LLM Expression Generator

The Expression Generator converts the user goal into a strict mathematical alpha expression.

Example:

```text
Goal:
Find a short-term mean reversion alpha using price and volume.

Generated expression:
-rank(decay_linear(ts_rank(close, 10), 20))
```

The LLM is restricted to allowed operators such as:

```text
rank()
ts_rank()
ts_mean()
ts_std_dev()
decay_linear()
zscore()
delta()
correlation()
```

The system validates the expression before executing it.

---

### 3. Deterministic Backtest Sandbox

The Backtest Sandbox is not an LLM.

It is a deterministic engine that:

- Parses the expression safely.
- Applies mathematical operators to market data.
- Calculates portfolio-style signal returns.
- Computes performance metrics.

This makes the system verification-based instead of prompt-based.

---

### 4. Evaluation Gate

The Evaluation Gate is a strict deterministic router.

Default pass conditions:

```text
Sharpe >= 1.5
Fitness >= 1.0
Turnover <= 0.7
```

If the alpha passes:

```text
Export Validated Alpha
```

If it fails:

```text
Route to Mathematical Critic
```

This prevents the LLM from deciding success by itself.

---

### 5. Mathematical Critic Agent

The Mathematical Critic studies failed metrics and suggests a mutation.

Example:

```text
Problem:
Sharpe is too low and turnover is unstable.

Mutation instruction:
Smooth the signal using decay_linear and increase the time-series window.
```

Then the Expression Generator uses this feedback to create a new formula.

---

### 6. LLM Fallback Mode

QuantForge gives the user a practical choice.

If the user wants a full AI-agent run, they can add an API key in `.env`:

```env
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4o-mini
```

Then the workflow becomes:

```text
Expression Generator = LLM agent
Mathematical Critic = LLM agent
```

If the user does not want to use an API key, they can leave `.env` empty and run the same command:

```text
Expression Generator = original deterministic partial-agent logic
Mathematical Critic = original deterministic partial-agent logic
```

This means the project does **not** crash when an API key is missing. It automatically switches to fallback mode:

```text
--llm-provider auto --llm-fallback auto
```

The important point:

> Fallback mode only changes the reasoning nodes. It does not change the market-data path. The alpha is still tested on live/latest Binance or Yahoo market data.

---

### 7. No Synthetic Market Data in Production

Production mode does not silently generate fake candles.

If live data fetching fails, the system should clearly report failure instead of pretending synthetic data is real.

This is important for credibility.

---

### 8. Exported Results

After a run, QuantForge stores results inside:

```text
data/results/
```

Example exported fields:

```json
{
  "decision": "discard_hypothesis_max_mutations",
  "expression": "-rank(decay_linear(ts_rank(close, 10), 20))",
  "iterations": 5,
  "market_rows": 5000,
  "latest_market_timestamp": "2026-05-20 20:02:00+00:00",
  "sharpe": 0.479801,
  "fitness": 0.004013,
  "turnover": 0.191333,
  "cumulative_return": 0.003966,
  "max_drawdown": -0.004147
}
```

A rejected alpha is not a failure of the project.

It means the system honestly rejected a weak signal.

---

## How to Run Locally

This is the easiest mode for development.

### Step 1: Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/quantforge-live-alpha-agent.git
cd quantforge-live-alpha-agent
```

### Step 2: Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Create environment file

On Windows:

```powershell
copy .env.example .env
```

On macOS/Linux:

```bash
cp .env.example .env
```

### Step 5: Configure `.env`

For fallback mode, you can leave the keys empty:

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
GOOGLE_API_KEY=
GEMINI_MODEL=gemini-1.5-flash
```

For full LLM mode with OpenAI:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

For Gemini:

```env
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

### Step 6: Run the project without API key

This uses deterministic fallback agents but still tests on live Binance data:

```bash
python apps.py --llm-provider auto --llm-fallback auto --provider binance --symbols BTC/USDT ETH/USDT SOL/USDT BNB/USDT XRP/USDT --timeframe 1m --limit 1000 --goal "Find a short-term mean reversion alpha using price, returns, and volume"
```

### Step 7: Run the project with OpenAI

```bash
python apps.py --llm-provider openai --llm-fallback auto --provider binance --symbols BTC/USDT ETH/USDT SOL/USDT BNB/USDT XRP/USDT --timeframe 1m --limit 1000 --goal "Find a short-term mean reversion alpha using price, returns, and volume"
```

### Step 8: Run strict LLM mode

Use this only when you want the app to fail if the LLM key is missing:

```bash
python apps.py --llm-provider openai --llm-fallback strict --provider binance --symbols BTC/USDT ETH/USDT SOL/USDT --timeframe 1m --limit 1000 --goal "Find a crypto mean reversion alpha"
```

---

## Example Output

```text
Production mode: no synthetic/duplicate market data fallback.
LLM mode: auto | fallback=auto
Goal: Find a short-term mean reversion alpha using price, returns, and volume
Provider: binance | Symbols: BTC/USDT, ETH/USDT, SOL/USDT, BNB/USDT, XRP/USDT

Node Trace:
NODE 1: Expression Generator
NODE 2: Backtest Sandbox
NODE 3: Evaluation Gate
NODE 4: Mathematical Critic
NODE 1: Expression Generator
NODE 2: Backtest Sandbox
NODE 3: Evaluation Gate

Final Alpha Decision:
Decision: discard_hypothesis_max_mutations
Expression: -rank(decay_linear(ts_rank(close, 10), 20))
Iterations: 5
Market rows: 5000
Latest market timestamp: 2026-05-20 20:02:00+00:00
Sharpe: 0.479801
Fitness: 0.004013
Turnover: 0.191333
```

This output is realistic.

It means the agent tested a real signal on live market candles and rejected it because the metrics were not strong enough.

---

## Run Tests

```bash
pytest -q
```

Expected output:

```text
11 passed
```

---

## Repository Structure

```text
quantforge-live-alpha-agent/
│
├── apps.py
├── requirements.txt
├── README.md
├── .env.example
│
├── quantforge/
│   ├── graph/
│   │   ├── state.py
│   │   ├── workflow.py
│   │   └── router.py
│   │
│   ├── agents/
│   │   ├── expression_generator.py
│   │   ├── mathematical_critic.py
│   │   ├── llm_client.py
│   │   └── fallback_agent.py
│   │
│   ├── market_data/
│   │   ├── binance_loader.py
│   │   ├── yahoo_loader.py
│   │   └── snapshot.py
│   │
│   ├── sandbox/
│   │   ├── expression_parser.py
│   │   ├── operators.py
│   │   ├── backtester.py
│   │   └── metrics.py
│   │
│   ├── exporter/
│   │   ├── alpha_exporter.py
│   │   └── report_generator.py
│   │
│   └── utils/
│       └── logging.py
│
├── data/
│   └── results/
│
└── tests/
    ├── test_expression_parser.py
    ├── test_operators.py
    ├── test_backtester.py
    ├── test_metrics.py
    └── test_workflow.py
```

---

## What Works Without an API Key?

Without an API key, these parts still work:

- Live Binance market data fetching
- Latest candle timestamp capture
- Expression generation through deterministic fallback
- Mathematical critique through deterministic fallback
- Vectorized backtesting
- Sharpe, fitness, turnover, drawdown calculation
- Evaluation gate routing
- Alpha rejection/export logic
- JSON report generation
- pytest test suite

These parts require an API key:

- LLM-based expression generation
- LLM-based mathematical critique
- More creative alpha mutation
- Natural-language reasoning over failed metrics

---

## Important Notes

### This is not a trading bot

QuantForge does not place real orders.

It is a research system that discovers and tests alpha ideas.

### This is not financial advice

The exported alpha is not a recommendation to trade.

It is a research artifact that should be validated with more data, out-of-sample tests, transaction costs, risk controls, and paper trading before any real use.

### Live candle data is not tick-level HFT data

The current version uses OHLCV candles.

It is a live-market alpha research agent, not a colocated HFT execution system.

---

## Why This Is More Than a Basic AI Project

A basic AI project:

```text
Prompt → LLM → Text Answer
```

QuantForge:

```text
User Goal
→ LLM Expression Generator
→ Live Market Data Snapshot
→ Deterministic Backtest Sandbox
→ Statistical Evaluation Gate
→ LLM Mathematical Critic
→ Formula Mutation
→ Re-test
→ Export or Reject Alpha
```

This makes it a true agentic quantitative research system.

It includes:

- Multi-step agent workflow
- LLM tool usage
- State transitions
- Conditional routing
- Quantitative verification
- Live market data integration
- Safe expression execution
- Closed-loop self-correction
- Deterministic final decisioning

---

## Design Principles

### 1. Verification Over Guessing

The LLM is not allowed to decide whether an alpha is good.

The deterministic backtest engine makes that decision.

### 2. Real Data Over Synthetic Data

Production mode uses live/latest market candles.

It does not silently replace failed data fetches with fake synthetic data.

### 3. Clear Fallback Behavior

If the API key is missing, the project can still run in deterministic fallback mode.

### 4. Modular Agent Design

Each component can be replaced independently:

- Binance can be replaced with another exchange.
- Yahoo Finance can be replaced with a paid data vendor.
- OpenAI can be replaced with Gemini or a local model.
- The backtester can be upgraded with slippage and transaction costs.
- The exporter can be connected to a research database.

### 5. Honest Alpha Rejection

If the alpha fails, the system rejects it.

That is a feature, not a bug.

---

## Future Improvements

Planned upgrades:

- WebSocket live candle streaming
- Frozen market snapshot for every mutation loop
- Out-of-sample validation
- Walk-forward testing
- Transaction cost modeling
- Slippage modeling
- Risk-adjusted portfolio construction
- Self-correlation checks
- Alpha library and similarity search
- Paper trading mode
- Streamlit or FastAPI dashboard
- Prometheus metrics for agent runs
- Docker deployment
- CI/CD with GitHub Actions
- Multi-exchange support
- Order book / L2 data integration

---

## Resume Bullet

**QuantForge — Live-Market LLM Alpha Research Agent | Python · LangGraph · OpenAI/Gemini · Binance · Pandas · NumPy · Quant Backtesting**

- Built a live-market AI agent that generates mathematical trading signals from user goals, tests them on latest Binance OHLCV candles, and validates them through deterministic Sharpe, fitness, turnover, and drawdown metrics.
- Designed a closed-loop LangGraph-style workflow with LLM-powered expression generation, deterministic vectorized backtesting, strict evaluation routing, mathematical critique, mutation, and alpha export.
- Implemented safe expression parsing, fallback agent mode without API keys, live data ingestion, JSON run reports, and pytest coverage for parser, operators, metrics, and workflow components.

---

## Interview Explanation

> QuantForge is a live-market autonomous alpha research agent. The system takes a quant research goal, fetches the latest market candles, generates a mathematical alpha expression through an LLM, and tests that expression inside a deterministic vectorized backtest sandbox. The LLM is not trusted to decide success. The final decision is made by hard metrics such as Sharpe, fitness, turnover, cumulative return, and drawdown. If the signal fails, a mathematical critic agent diagnoses the failure and mutates the formula. This creates a closed-loop AI quant researcher that combines generative AI with rigorous statistical verification.

---

## How to Push This Project to GitHub

### Step 1: Open PowerShell in the project folder

```powershell
cd "C:\Users\Vedant Jhunjhunwala\Downloads\quantforge_full_ai_agent_with_fallback"
```

### Step 2: Initialize Git

```powershell
git init
```

### Step 3: Create `.gitignore`

Create a file named `.gitignore` and add:

```gitignore
.venv/
__pycache__/
*.pyc
.env
.DS_Store
.pytest_cache/
data/results/
*.zip
```

Do not upload `.env` because it may contain API keys.

### Step 4: Add project files

```powershell
git add .
```

### Step 5: Commit

```powershell
git commit -m "Initial commit: QuantForge live-market AI alpha research agent"
```

### Step 6: Create a GitHub repository

1. Go to GitHub.
2. Click **New repository**.
3. Repository name:

```text
quantforge-live-alpha-agent
```

4. Keep it **Public**.
5. Do not add a README from GitHub because this project already has one.
6. Click **Create repository**.

### Step 7: Add remote origin

Replace `YOUR_USERNAME` with your GitHub username:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/quantforge-live-alpha-agent.git
```

If you get this error:

```text
remote origin already exists
```

Use:

```powershell
git remote set-url origin https://github.com/YOUR_USERNAME/quantforge-live-alpha-agent.git
```

### Step 8: Rename branch to main

```powershell
git branch -M main
```

### Step 9: Push to GitHub

```powershell
git push -u origin main
```

---

## How to Update README Later

After editing `README.md`, run:

```powershell
git add README.md
git commit -m "Improve README with architecture and setup instructions"
git push
```

---

## License

This project is intended for educational, research, and portfolio purposes.

It is not financial advice and should not be used for live trading without additional validation, risk controls, and regulatory review.
