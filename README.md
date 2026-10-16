# 🌱 Kraiiv Agentic Grant Research Bot

> Powered by **Google Gemini 4 Argon** — automatically researches and prioritises grant funding opportunities for your project.

Built specifically for **[Kraiiv](https://kraiiv.xyz)** — the healthy-eating habit tracker for African food that rewards users with airtime, data, groceries, and Bitcoin sats.

---

## What it does

This bot runs a **4-step agentic pipeline** using Gemini 4 Argon's deep reasoning:

| Step | What happens |
|------|-------------|
| 1️⃣  Understand | Analyses your project — mission, SDGs, stage, impact, narratives |
| 2️⃣  Search | Finds 20+ real grant opportunities across health, Africa tech, Bitcoin, food systems, DFIs |
| 3️⃣  Score | Scores each grant on fit, effort, and likelihood — ranks into tiers |
| 4️⃣  Report | Produces a full polished report with 30-day action plan, templates, and 12-month roadmap |

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your Gemini API key

Get your key free at **[aistudio.google.com](https://aistudio.google.com)**.

**PowerShell (Windows):**
```powershell
$env:GEMINI_API_KEY = "your-key-here"
```

**Bash (Mac/Linux):**
```bash
export GEMINI_API_KEY="your-key-here"
```

---

## Run it

### Default — Kraiiv project (baked in, no args needed)
```bash
python main.py
```

### Custom project URL
```bash
python main.py --url https://yourproject.com
```

### Custom description
```bash
python main.py --desc "We build affordable solar-powered cold storage for smallholder farmers in East Africa..."
```

---

## Output

- **Console**: Full report printed live as it generates
- **File**: Saved to `reports/grant_report_YYYYMMDD_HHMMSS.md`

Copy the report into Notion, Google Docs, or your team's workspace.

---

## Thinking levels used

| Step | Thinking Level | Why |
|------|---------------|-----|
| Understand | `medium` | Balanced — structured extraction |
| Search | `high` | Deep recall of real funding landscape |
| Score | `high` | Complex multi-factor reasoning |
| Report | `high` | Long-form, coherent synthesis |

---

## Adapting for other projects

Edit `KRAIIV_CONTEXT` in `main.py`, or just pass `--desc` with your own project description. The bot works for any startup or NGO seeking grants.

---

*Made in Lagos. Be intentional.*
