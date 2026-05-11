# 🩺 MediAssist AI

A **strictly-scoped**, production-grade health assistant built with Streamlit, Groq, and CrewAI.

[![Deploy to Streamlit Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

---

## 🚀 Deploy to Streamlit Cloud (Free, 5 minutes)

### Step 1 — Push to GitHub
```
your-repo/
├── app.py
├── requirements.txt
├── .gitignore
└── .streamlit/
    ├── config.toml
    └── secrets.toml.example   ← template only, never the real file
```
> **Do not** commit `.streamlit/secrets.toml` or `.env` — they are in `.gitignore`.

### Step 2 — Create app on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
2. Click **New app**
3. Select your repo, branch (`main`), and set **Main file path** to `app.py`
4. Click **Deploy**

### Step 3 — Add your Groq API key as a Secret
1. In your app dashboard → **Settings → Secrets**
2. Paste:
```toml
GROQ_API_KEY = "gsk_your_key_here"
```
3. Click **Save** — the app restarts automatically

Get a free Groq key at → https://console.groq.com/keys

---

## 💻 Run Locally

```bash
# 1. Clone your repo
git clone https://github.com/you/mediassist && cd mediassist

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your key
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Open secrets.toml and paste your GROQ_API_KEY
# OR create a .env file: echo 'GROQ_API_KEY=gsk_...' > .env

# 4. Run
streamlit run app.py
```

---

## 🔑 API Key Priority (all environments)

```
Sidebar input  (highest — per-session override)
      ↓
Streamlit Secrets  (st.secrets — Streamlit Cloud)
      ↓
.env file  (local development)
      ↓
Error prompt  (app stops cleanly, tells user what to do)
```

---

## ✨ Features

| Feature | Detail |
|---|---|
| **Strict Scope Guard** | 2-layer filter: fast 1-token LLM classifier + system prompt. Refuses ALL non-health topics |
| **Model Selection** | Llama 3.3 70B · Llama 3.1 8B · Gemma 2 9B — switchable from sidebar |
| **Token Usage Modes** | Ultra Saver (80) · Saver (150) · Moderate (300) · Full Power (600) |
| **Message History** | Full in-session conversation memory with clear button |
| **Feedback Loop** | 👍 / 👎 per message — negative ratings injected as in-context training examples |
| **CrewAI Web Agents** | 2-agent pipeline: Medical Web Researcher → Health Communicator |
| **Safety Filter** | Blocks emergency/self-harm/prescription keywords before any LLM call |
| **API Key Flexibility** | Sidebar override · Streamlit Secrets · .env — all supported |

---

## 🤖 CrewAI Agent Pipeline

When **"Enable web search agents"** is toggled ON in the sidebar:

```
User Query → [Scope Guard] → [Agent 1: Web Researcher] → [Agent 2: Communicator] → Response
```

Falls back to direct Groq if the pipeline errors for any reason.

---

## 📁 File Structure

```
├── app.py                         ← Main Streamlit app
├── requirements.txt               ← Python dependencies
├── .gitignore                     ← Keeps secrets out of Git
├── .streamlit/
│   ├── config.toml                ← Theme + server settings
│   └── secrets.toml.example       ← Template (copy → secrets.toml locally)
└── mediassist_feedback.json       ← Auto-created on first rating (local only)
```

> **Note:** `mediassist_feedback.json` is ephemeral on Streamlit Cloud — it resets on each deployment. For persistent feedback storage in production, swap `save_feedback()` for a database (e.g. Supabase, Firebase, or a GitHub Gist via API).
