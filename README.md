# ResearchMind: Multi-Agent AI Research System (Groq, free)

Search Agent -> Reader Agent -> Writer Chain -> Critic Chain, with a Streamlit UI.

## Run (3 steps)
1. Get free keys (no card needed):
   - Groq:   https://console.groq.com  (API Keys -> Create API Key)
   - Tavily: https://tavily.com
2. Open `.env`, paste both keys (no quotes, no spaces), save.
3. Double-click `run.bat`  (or: `python -m pip install -r requirements.txt` then `python -m streamlit run app.py`)

Open http://localhost:8501, type a topic, click Run.

Free tier is rate limited; the app retries automatically. Never share your `.env`.
