import os
import json
from datetime import datetime
from groq import Groq
import streamlit as st

# ── load_dotenv — local dev only; silently skipped on Streamlit Cloud ─────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ── Optional CrewAI import (graceful fallback if not installed) ──────────────
try:
    from crewai import Agent, Task, Crew, Process, LLM
    from crewai_tools import DuckDuckGoSearchTool
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MediAssist AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS (zero black) ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,300&family=Playfair+Display:wght@500;600&display=swap');

/* ── Root reset ── */
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* ── App background ── */
.stApp {
    background: linear-gradient(145deg, #f0fdfa 0%, #ecfdf5 40%, #eff6ff 100%);
    min-height: 100vh;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f0fdf4 60%, #f0fdfa 100%);
    border-right: 1.5px solid #6ee7b7;
    box-shadow: 4px 0 20px rgba(16,185,129,0.08);
}

section[data-testid="stSidebar"] > div { padding-top: 1.5rem; }

/* Sidebar headings */
section[data-testid="stSidebar"] h2 {
    color: #0f766e !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 1.3rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em;
}

section[data-testid="stSidebar"] h3 {
    color: #115e59 !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 4px !important;
}

/* ── Main page header ── */
.hero-wrap {
    text-align: center;
    padding: 0.8rem 0 0.4rem;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    font-weight: 600;
    color: #0f766e;
    letter-spacing: -0.02em;
    margin-bottom: 4px;
}
.hero-sub {
    color: #5eead4;
    font-size: 0.88rem;
    font-weight: 500;
    letter-spacing: 0.04em;
}

/* ── Chat messages ── */
div[data-testid="stChatMessage"] {
    border-radius: 14px !important;
    margin: 5px 0 !important;
    padding: 2px 4px !important;
    backdrop-filter: blur(8px);
}

/* User bubble */
div[data-testid="stChatMessage"][data-role="user"],
div[data-testid="stChatMessage"]:has(> div > [data-testid="stChatMessageAvatarUser"]) {
    background: rgba(239,246,255,0.85) !important;
    border: 1px solid #bfdbfe !important;
}

/* Assistant bubble */
div[data-testid="stChatMessage"][data-role="assistant"],
div[data-testid="stChatMessage"]:has(> div > [data-testid="stChatMessageAvatarAssistant"]) {
    background: rgba(240,253,250,0.9) !important;
    border: 1px solid #99f6e4 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #f0fdf4, #eff6ff) !important;
    border: 1.5px solid #6ee7b7 !important;
    color: #0f766e !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 1px 6px rgba(16,185,129,0.12) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #6ee7b7, #93c5fd) !important;
    color: #064e3b !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(16,185,129,0.25) !important;
}

/* ── Selectbox & toggle labels ── */
.stSelectbox label, .stToggle label, div[data-testid="stWidgetLabel"] p {
    color: #374151 !important;
    font-weight: 500 !important;
    font-size: 0.83rem !important;
}

/* ── Select box focus ring ── */
.stSelectbox [data-baseweb="select"] {
    border-radius: 10px !important;
}

/* ── Metrics ── */
div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.8);
    border: 1px solid #d1fae5;
    border-radius: 12px;
    padding: 10px 14px !important;
    box-shadow: 0 1px 6px rgba(16,185,129,0.08);
}
div[data-testid="metric-container"] label {
    color: #6b7280 !important;
    font-size: 0.72rem !important;
}
div[data-testid="stMetricValue"] {
    color: #0f766e !important;
    font-weight: 700 !important;
}

/* ── Alerts ── */
.stAlert {
    border-radius: 12px !important;
}
div[data-testid="stNotification"] [data-testid="stMarkdownContainer"] p {
    font-size: 0.88rem !important;
}

/* ── Progress bar ── */
div[data-testid="stProgressBar"] > div {
    background: linear-gradient(90deg, #6ee7b7, #38bdf8) !important;
}

/* ── Chat input ── */
div[data-testid="stChatInputContainer"] {
    border-top: 1.5px solid #99f6e4;
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(10px);
    border-radius: 0 0 14px 14px;
}
textarea[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.9) !important;
    border: 1.5px solid #6ee7b7 !important;
    border-radius: 12px !important;
    color: #1e293b !important;
}

/* ── Divider ── */
hr { border-color: #d1fae5 !important; opacity: 0.8; }

/* ── Caption / small text ── */
small, .stCaption p { color: #94a3b8 !important; font-size: 0.75rem !important; }

/* ── Feedback row ── */
.fb-label {
    color: #94a3b8;
    font-size: 0.72rem;
    margin: 2px 0 4px;
    font-style: italic;
}
.fb-done {
    display: inline-block;
    background: linear-gradient(90deg,#d1fae5,#dbeafe);
    color: #065f46;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 20px;
    margin-top: 4px;
}

/* ── Agent pill badges ── */
.agent-pill {
    display: inline-block;
    background: linear-gradient(90deg, #6ee7b7, #93c5fd);
    color: #064e3b;
    font-size: 0.73rem;
    font-weight: 700;
    padding: 3px 11px;
    border-radius: 20px;
    margin: 2px;
    letter-spacing: 0.02em;
}
.pipeline-row {
    text-align: center;
    margin: 6px 0 2px;
}
.arrow { color: #94a3b8; margin: 0 2px; font-size: 0.85rem; }

/* ── Spinner text ── */
.stSpinner p { color: #0f766e !important; font-weight: 500 !important; }

/* ── Toggle styling ── */
.stToggle > label > div[data-checked="true"] {
    background: linear-gradient(90deg, #6ee7b7, #38bdf8) !important;
}

/* ── API key input ── */
div[data-testid="stTextInput"] input[type="password"],
div[data-testid="stTextInput"] input[type="text"] {
    background: rgba(255,255,255,0.9) !important;
    border: 1.5px solid #6ee7b7 !important;
    border-radius: 10px !important;
    color: #1e293b !important;
    font-size: 0.82rem !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #0f766e !important;
    box-shadow: 0 0 0 3px rgba(16,185,129,0.15) !important;
}
.key-status-ok {
    display: inline-flex; align-items: center; gap: 6px;
    background: linear-gradient(90deg, #d1fae5, #dbeafe);
    color: #065f46; font-size: 0.73rem; font-weight: 700;
    padding: 3px 12px; border-radius: 20px; margin-top: 4px;
}
.key-status-warn {
    display: inline-flex; align-items: center; gap: 6px;
    background: #fef3c7; color: #92400e;
    font-size: 0.73rem; font-weight: 700;
    padding: 3px 12px; border-radius: 20px; margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────────────────
def _read_env_key():
    try:
        return st.secrets["GROQ_API_KEY"]          # Streamlit Cloud secrets
    except (KeyError, FileNotFoundError):
        return os.getenv("GROQ_API_KEY")            # local .env fallback

GROQ_API_KEY = _read_env_key()

MODELS = {
    "🧠 Llama 3.3 70B — Best Quality": "llama-3.3-70b-versatile",
    "⚡ Llama 3.1 8B — Fastest": "llama-3.1-8b-instant",
    "🔬 Gemma 2 9B — Efficient": "gemma2-9b-it",
}

TOKEN_MODES = {
    "⚡ Ultra Saver — ~80 tokens": {
        "max_tokens": 80, "temperature": 0.3,
        "desc": "Ultra-brief. Best for simple yes/no health facts.",
    },
    "💾 Saver — ~150 tokens": {
        "max_tokens": 150, "temperature": 0.45,
        "desc": "Short and focused. Good for quick clarifications.",
    },
    "⚖️ Moderate — ~300 tokens": {
        "max_tokens": 300, "temperature": 0.7,
        "desc": "Balanced detail. Recommended for most questions.",
    },
    "🔋 Full Power — ~600 tokens": {
        "max_tokens": 600, "temperature": 0.85,
        "desc": "Comprehensive. Use for complex health topics.",
    },
}

# System prompt — strictly scoped, feedback-aware base
BASE_SYSTEM_PROMPT = """You are MediAssist, a strictly scoped health and medical information assistant.

═══════════════════════════════════════════
ABSOLUTE SCOPE RULE — READ FIRST
═══════════════════════════════════════════
You EXCLUSIVELY answer questions about:
  health, medicine, wellness, anatomy, physiology, symptoms,
  diseases, nutrition, fitness, mental health, medications (general
  info only), first aid fundamentals, and medical terminology.

If the user's question is NOT within the above topics — even slightly —
respond with EXACTLY this sentence and nothing else:
  "I'm MediAssist and I only answer health and medical questions.
   Please use the appropriate resource for other topics."

Do NOT offer tips, apologies, or explanations for off-topic queries.
Do NOT help with: programming, technology, math, history, law, finance,
cooking (unless nutrition-focused), entertainment, languages, or ANY
non-health subject.

═══════════════════════════════════════════
FOR HEALTH QUESTIONS
═══════════════════════════════════════════
- Respond warmly, clearly, and empathetically
- Maximum 4 sentences (strictly)
- Always recommend consulting a qualified healthcare professional
- NEVER diagnose a specific condition
- NEVER prescribe medications or dosages
- For any emergency: direct immediately to emergency services
"""

FEEDBACK_FILE = "mediassist_feedback.json"

UNSAFE_KEYWORDS = [
    "prescribe", "dosage", "how much should i take", "what medication",
    "which pill", "overdose", "drug combination",
    "kill myself", "hurt myself", "suicide", "self harm", "end my life",
    "heart attack", "stroke", "can't breathe", "cannot breathe",
    "unconscious", "not breathing", "choking",
]

# ── Groq client — created after sidebar resolves the active key ──────────────
# (defined below, after sidebar renders)
client: Groq | None = None

# ── Feedback helpers ──────────────────────────────────────────────────────────
def load_feedback() -> list:
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_feedback(entry: dict) -> None:
    data = load_feedback()
    data.append(entry)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_feedback_context() -> str:
    """
    Feedback training loop: inject the last 3 negatively-rated
    (question, response) pairs so the model learns in-context what
    NOT to do in future responses.
    """
    data = load_feedback()
    negatives = [f for f in data if f.get("rating") == "👎"][-3:]
    if not negatives:
        return ""
    examples = "\n".join(
        f"  • Q: {n.get('question','')[:80]} | Poor pattern to avoid in response: {n.get('response','')[:100]}…"
        for n in negatives
    )
    return (
        "\n\n═══════════════════════════\n"
        "IMPROVEMENT FEEDBACK (from recent poor ratings — avoid these response patterns):\n"
        + examples
    )

# ── Safety / Scope helpers ────────────────────────────────────────────────────
def is_unsafe(message: str) -> bool:
    msg = message.lower()
    return any(kw in msg for kw in UNSAFE_KEYWORDS)

def is_health_related(message: str, model_id: str) -> bool:
    """Fast 1-token scope guard via Groq."""
    try:
        resp = client.chat.completions.create(
            model=model_id,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Classify the user's message. "
                        "Reply with ONLY the single word HEALTH if it concerns health, "
                        "medicine, wellness, anatomy, symptoms, nutrition, fitness, or "
                        "mental health. Otherwise reply with ONLY the single word OTHER."
                    ),
                },
                {"role": "user", "content": message},
            ],
            max_tokens=5,
            temperature=0.0,
        )
        label = resp.choices[0].message.content.strip().upper()
        return "HEALTH" in label
    except Exception:
        return True  # fail open — let the system prompt handle edge cases

# ── CrewAI multi-agent workflow ───────────────────────────────────────────────
def run_health_crew(model_id: str, query: str, max_tokens: int, api_key: str) -> str:
    """
    Two-agent pipeline:
      1. Medical Web Researcher  — searches DuckDuckGo for current health facts
      2. Health Communicator     — synthesises research into a concise, warm reply
    """
    llm = LLM(
        model=f"groq/{model_id}",
        api_key=api_key,
        temperature=0.7,
        max_tokens=max_tokens,
    )

    search_tool = DuckDuckGoSearchTool()

    # ── Agent 1 ──
    researcher = Agent(
        role="Medical Web Researcher",
        goal="Find 2-3 key, accurate health facts from trusted sources for the given health query.",
        backstory=(
            "You are a specialist medical researcher who retrieves health information "
            "exclusively from authoritative sources: WHO, NIH, Mayo Clinic, WebMD, CDC. "
            "You only research health and medical topics and clearly note the source."
        ),
        tools=[search_tool],
        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=3,
    )

    # ── Agent 2 ──
    communicator = Agent(
        role="Health Communication Specialist",
        goal=(
            "Turn the researcher's findings into a clear, warm, empathetic health "
            "response of exactly 3-4 sentences."
        ),
        backstory=(
            "You are a compassionate health educator who explains medical information "
            "in plain language. You always remind users to consult a real doctor for "
            "personal advice, and you NEVER diagnose or prescribe."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    # ── Task 1 ──
    research_task = Task(
        description=(
            f"Search the web for reliable, up-to-date health information about: '{query}'. "
            "Retrieve 2-3 specific facts with source names. Health topics only."
        ),
        agent=researcher,
        expected_output="2-3 bullet-point facts about the health topic with source names.",
    )

    # ── Task 2 ──
    synthesis_task = Task(
        description=(
            f"Using only the research provided, write a 3-4 sentence health response to: '{query}'. "
            "Tone: warm, clear, empathetic. End with a reminder to see a healthcare professional. "
            "Do NOT diagnose or prescribe."
        ),
        agent=communicator,
        expected_output="A concise, empathetic 3-4 sentence health response.",
        context=[research_task],
    )

    crew = Crew(
        agents=[researcher, communicator],
        tasks=[research_task, synthesis_task],
        process=Process.sequential,
        verbose=False,
    )

    result = crew.kickoff()
    return str(result).strip()

# ── Session state init ────────────────────────────────────────────────────────
for key, default in {
    "messages": [],
    "feedback_given": {},
    "pending_rating": None,   # (msg_index, rating)
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Handle deferred feedback saves (avoids rerun loops) ──────────────────────
if st.session_state.pending_rating is not None:
    idx, rating = st.session_state.pending_rating
    fkey = f"f_{idx}"
    st.session_state.feedback_given[fkey] = rating
    question = (
        st.session_state.messages[idx - 1]["content"]
        if idx > 0
        else ""
    )
    response = st.session_state.messages[idx]["content"]
    save_feedback({
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "response": response,
        "rating": rating,
    })
    st.session_state.pending_rating = None

# ═══════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🩺 MediAssist")
    st.caption("Settings & Controls")
    st.divider()

    # ── API Key override ─────────────────────────────────────
    st.markdown("### 🔑 Groq API Key")
    sidebar_key = st.text_input(
        "api key",
        type="password",
        placeholder="gsk_… (overrides .env key)",
        label_visibility="collapsed",
        help="Optional. Paste your Groq API key here to override the .env value for this session.",
    )

    _sidebar_key_present = bool(sidebar_key and sidebar_key.strip())
    _secrets_present = False
    _secrets_label = ""
    try:
        _ = st.secrets["GROQ_API_KEY"]
        _secrets_present = True
        _secrets_label = "☁️ Using key from Streamlit Secrets"
    except (KeyError, FileNotFoundError):
        pass
    _env_present = bool(os.getenv("GROQ_API_KEY"))

    if _sidebar_key_present:
        st.markdown(
            '<span class="key-status-ok">✅ Using key from sidebar</span>',
            unsafe_allow_html=True,
        )
    elif _secrets_present:
        st.markdown(
            f'<span class="key-status-ok">{_secrets_label}</span>',
            unsafe_allow_html=True,
        )
    elif _env_present:
        st.markdown(
            '<span class="key-status-ok">🌿 Using key from .env</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="key-status-warn">⚠️ No API key found</span>',
            unsafe_allow_html=True,
        )
        st.caption("Add GROQ_API_KEY to Streamlit Secrets, your .env, or paste above.")

    st.divider()

    # ── Model selection ──────────────────────────────────────
    st.markdown("### 🤖 AI Model")
    model_name = st.selectbox(
        "model",
        list(MODELS.keys()),
        index=0,
        label_visibility="collapsed",
    )
    selected_model = MODELS[model_name]

    st.divider()

    # ── Token usage mode ─────────────────────────────────────
    st.markdown("### 🎛️ Token Usage Mode")
    token_mode = st.selectbox(
        "token mode",
        list(TOKEN_MODES.keys()),
        index=2,
        label_visibility="collapsed",
    )
    tok = TOKEN_MODES[token_mode]
    st.caption(tok["desc"])
    col_a, col_b = st.columns(2)
    col_a.metric("Max tokens", tok["max_tokens"])
    col_b.metric("Temp", tok["temperature"])

    st.divider()

    # ── Web search agents ────────────────────────────────────
    st.markdown("### 🌐 CrewAI Web Agents")
    if not CREWAI_AVAILABLE:
        st.warning(
            "CrewAI not installed.\n"
            "Run: `pip install crewai crewai-tools`"
        )
        use_web = False
    else:
        use_web = st.toggle(
            "Enable web search agents",
            value=False,
            help="Researcher → Communicator pipeline. Slower but uses live web data.",
        )
        if use_web:
            st.success("🟢 2-Agent pipeline active\n\n🔍 Researcher  →  💬 Communicator")
        else:
            st.info("💨 Direct mode — faster responses")

    st.divider()

    # ── Chat history ─────────────────────────────────────────
    st.markdown("### 💬 Chat History")
    n_ex = len(st.session_state.messages) // 2
    st.caption(
        "No messages yet." if n_ex == 0 else f"{n_ex} exchange{'s' if n_ex != 1 else ''} in session."
    )
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.feedback_given = {}
            st.rerun()

    st.divider()

    # ── Feedback stats ───────────────────────────────────────
    st.markdown("### 📊 Training Feedback")
    fb_data = load_feedback()
    if fb_data:
        good = sum(1 for f in fb_data if f.get("rating") == "👍")
        bad  = sum(1 for f in fb_data if f.get("rating") == "👎")
        total = len(fb_data)
        c1, c2 = st.columns(2)
        c1.metric("👍 Helpful", good)
        c2.metric("👎 Poor", bad)
        pct = int(good / total * 100) if total else 0
        st.progress(pct / 100, text=f"{pct}% satisfaction across {total} ratings")
        st.caption(
            "Negative feedback is automatically used to improve future responses."
        )
    else:
        st.caption("No feedback yet — rate responses below to help train MediAssist!")

# ═══════════════════════════════════════════════════════════════════
# RESOLVE ACTIVE API KEY & BUILD CLIENT
# (sidebar must have rendered first so sidebar_key is available)
# ═══════════════════════════════════════════════════════════════════
# Priority: sidebar input > Streamlit Cloud secrets > local .env
ACTIVE_KEY = (
    sidebar_key.strip()
    if sidebar_key and sidebar_key.strip()
    else GROQ_API_KEY
)

if not ACTIVE_KEY:
    st.error(
        "⚠️ **No Groq API key found.**  \n\n"
        "**Streamlit Cloud:** add `GROQ_API_KEY` under *Settings → Secrets*  \n"
        "**Local:** add it to your `.env` file  \n"
        "**Any environment:** paste it in the sidebar 🔑 field above."
    )
    st.stop()

client = Groq(api_key=ACTIVE_KEY)

# ═══════════════════════════════════════════════════════════════════
# MAIN PANEL
# ═══════════════════════════════════════════════════════════════════
st.markdown(
    """
    <div class="hero-wrap">
        <div class="hero-title">🩺 MediAssist AI</div>
        <div class="hero-sub">STRICTLY HEALTH & WELLNESS · ALWAYS CONSULT A DOCTOR FOR PERSONAL ADVICE</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if use_web:
    st.markdown(
        """
        <div class="pipeline-row">
            <span class="agent-pill">🔍 Web Researcher</span>
            <span class="arrow">→</span>
            <span class="agent-pill">💬 Health Communicator</span>
            <span class="arrow">→</span>
            <span class="agent-pill">✅ Verified Response</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# ── Render chat history with inline feedback ──────────────────────
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant":
            fkey = f"f_{i}"
            if fkey in st.session_state.feedback_given:
                rating = st.session_state.feedback_given[fkey]
                st.markdown(
                    f'<span class="fb-done">{rating} Feedback recorded — thank you!</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<p class="fb-label">Was this response helpful?</p>',
                    unsafe_allow_html=True,
                )
                fc1, fc2, fc3 = st.columns([1, 1, 10])
                with fc1:
                    if st.button("👍", key=f"up_{i}"):
                        st.session_state.pending_rating = (i, "👍")
                        st.rerun()
                with fc2:
                    if st.button("👎", key=f"dn_{i}"):
                        st.session_state.pending_rating = (i, "👎")
                        st.rerun()

# ── Chat input handler ────────────────────────────────────────────
if prompt := st.chat_input("Ask a health or wellness question…"):

    # ── 1. Unsafe / emergency guard ──────────────────────────
    if is_unsafe(prompt):
        with st.chat_message("assistant"):
            st.error(
                "🚨 **Urgent or Sensitive Request Detected**\n\n"
                "Please contact **emergency services** (115 in Pakistan / 911 / 999) "
                "or a qualified healthcare professional immediately. "
                "MediAssist cannot handle emergencies."
            )
        st.stop()

    # ── 2. Show user message ─────────────────────────────────
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ── 3. Generate reply ────────────────────────────────────
    with st.chat_message("assistant"):

        # Scope gate — fast 1-token check
        with st.spinner("Checking health relevance…"):
            health_ok = is_health_related(prompt, selected_model)

        if not health_ok:
            reply = (
                "I'm MediAssist and I only answer health and medical questions. "
                "Please use the appropriate resource for other topics."
            )
            st.markdown(reply)

        elif use_web and CREWAI_AVAILABLE:
            # Multi-agent path
            placeholder = st.empty()
            placeholder.info(
                "🤖 **Agent pipeline running…**  \n"
                "🔍 Researcher searching live medical sources  →  "
                "💬 Communicator preparing your response"
            )
            try:
                reply = run_health_crew(selected_model, prompt, tok["max_tokens"], ACTIVE_KEY)
                placeholder.empty()
                st.markdown(reply)
            except Exception as crew_err:
                placeholder.empty()
                st.warning(
                    f"⚠️ Agent pipeline error — falling back to direct mode.  \n"
                    f"_(Reason: {crew_err})_"
                )
                # Fallback: direct Groq call
                system_prompt = BASE_SYSTEM_PROMPT + get_feedback_context()
                fallback = client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *st.session_state.messages,
                    ],
                    temperature=tok["temperature"],
                    max_tokens=tok["max_tokens"],
                )
                reply = fallback.choices[0].message.content.strip()
                st.markdown(reply)

        else:
            # Direct Groq path
            with st.spinner("💭 Thinking…"):
                system_prompt = BASE_SYSTEM_PROMPT + get_feedback_context()
                response = client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *st.session_state.messages,
                    ],
                    temperature=tok["temperature"],
                    max_tokens=tok["max_tokens"],
                )
                reply = response.choices[0].message.content.strip()
            st.markdown(reply)

    # ── 4. Persist and rerender ───────────────────────────────
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
