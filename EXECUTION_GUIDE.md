# 🚀 Execution Guide — TrustDesk

## ✅ Prerequisites (Already Done!)
- Python 3.12.4 ✅
- Virtual environment created at `.venv` ✅
- All packages installed (langgraph, langchain, langchain-openai, etc.) ✅

---

## Step 1 — Configure your OpenAI API Key

A `.env` file is already created in the project folder. Open it and **replace the placeholder** with your real API key:

```env
OPENAI_API_KEY=your-openai-api-key-here
```

> Get your key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys).

Optionally, uncomment the line below in `.env` to override the default model (`gpt-4.1-mini`):

```env
# MODEL_NAME=openai:gpt-4o-mini
```

> [!NOTE]
> The `.env` file is automatically loaded by `agent.py` via `python-dotenv`. No terminal commands needed to set environment variables.

---

## Step 2 — Activate the Virtual Environment

Navigate to the `trustdesk` folder and activate the virtual environment:

```powershell
cd c:\Users\IUMESHYA\workspace\AI_workspace\trustdesk
.\.venv\Scripts\Activate.ps1
```

Your terminal prompt will change to show `(.venv)`.

---

## Step 3 — Run the App

### Option A: Launch the Gradio Web Interface (Recommended)

```powershell
python gradio_app.py
```

Then open your browser to **http://127.0.0.1:7860**.
You will see an interactive dashboard allowing you to:
- Choose from sample tickets (`T-1001`, `T-1002`, `T-1003`) or enter a custom ID.
- Inspect ticket metadata in real-time.
- Click **Resolve Ticket** to trigger the TrustDesk agent.
- View guardrail checks and grounding warnings.
- Interactively **Approve** or **Reject & Escalate** when sensitive actions are detected.

---

### Option B: Run in Terminal (CLI)

```powershell
python app.py
```

You'll be prompted:

```
Ticket ID [T-1001]:
```

Enter one of the available ticket IDs (from `data/tickets.json`):
- `T-1001`
- `T-1002`
- `T-1003`

The agent will:
1. Fetch the ticket
2. Search the knowledge base
3. Draft a grounded response
4. Ask for **human approval** if a sensitive action (e.g., refund) is detected

---

## Step 4 (Optional) — Run the Evaluation Suite

```powershell
python evaluate.py
```

---

## Step 5 (Optional) — Run Unit Tests

```powershell
pytest tests/
```

---

## 📁 Key Files at a Glance

| File | Purpose |
|------|---------|
| `gradio_app.py` | Interactive Gradio Web UI |
| `app.py` | CLI entry point |
| `agent.py` | LangGraph agent logic |
| `tools.py` | Ticket, KB, and escalation tools |
| `guardrails.py` | Grounding & approval checks |
| `data/tickets.json` | Sample tickets |
| `data/kb.json` | Knowledge base articles |
| `.env` | API key & model configuration |

---

> [!IMPORTANT]
> **The only thing you need to do is paste your `OPENAI_API_KEY` into the `.env` file** — everything else (venv, packages, dotenv loading) is already in place!
