import streamlit as st
import json
import time
import plotly.graph_objects as go
from openai import OpenAI
from anthropic import Anthropic

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Prompt Enhancer v2",
    page_icon="PE",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown('<style>[data-testid="stSidebar"] {min-width: 280px; max-width: 280px;} [data-testid="collapsedControl"] {display: none;}</style>', unsafe_allow_html=True)
# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Import font ── */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    /* ── Force light theme ── */
    [data-testid="stAppViewContainer"],
    [data-testid="stApp"],
    .main,
    section[data-testid="stSidebar"] > div {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    [data-testid="stAppViewContainer"] {
        background: #ffffff !important;
    }
    /* Header: keep sidebar toggle, kill everything else */
    [data-testid="stHeader"] {
        background: #ffffff !important;
    }
    [data-testid="stToolbar"] {
        display: none !important;
    }
    [data-testid="stDecoration"] {
        display: none !important;
    }
    /* Style sidebar toggle - make visible */
    [data-testid="collapsedControl"] {
        top: 0.5rem !important;
        left: 0.5rem !important;
        z-index: 999 !important;
    }
    [data-testid="collapsedControl"] svg {
        color: #333 !important;
        stroke: #333 !important;
    }

    /* ── Global ── */
    html, body, [class*="css"],
    p, span, label, div, li, td, th, input, textarea, select, button, a {
        font-family: 'IBM Plex Sans', -apple-system, sans-serif !important;
        color: #1a1a1a;
    }
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 2rem;
        max-width: 1400px;
        margin-top: -2rem !important;
    }
    .main .block-container > div:first-child {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div {
        background: #f5f6f8 !important;
        border-right: 1px solid #e2e4e9;
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 0.8rem;
    }
    [data-testid="stSidebar"] * {
        color: #1a1a1a !important;
    }
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] .stCaption p {
        color: #888 !important;
        font-size: 0.7rem !important;
    }
    
    /* ── Typography — 13px base, consistent everywhere ── */
    h1 { font-size: 0.95rem !important; font-weight: 700 !important; color: #1a1a1a !important; margin-bottom: 0.2rem !important; }
    h2 { font-size: 0.88rem !important; font-weight: 700 !important; color: #1a1a1a !important; }
    h3 { font-size: 0.82rem !important; font-weight: 600 !important; color: #1a1a1a !important; }
    h4 { font-size: 0.78rem !important; font-weight: 600 !important; color: #333 !important; margin-top: 0 !important; margin-bottom: 0.25rem !important; }
    p, span, label, li { font-size: 0.8rem !important; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        border-bottom: 1px solid #e5e7eb;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        padding: 0.5rem 1.2rem;
        color: #666;
        border-bottom: 2px solid transparent;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #444;
    }
    .stTabs [aria-selected="true"] {
        color: #2563eb !important;
        border-bottom: 2px solid #2563eb !important;
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 0.5rem;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #2563eb !important;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* ── Text areas and inputs ── */
    .stTextArea textarea,
    .stTextInput input {
        font-size: 0.8rem !important;
        background: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 5px !important;
        color: #1a1a1a !important;
        padding: 0.45rem 0.6rem !important;
        line-height: 1.45 !important;
    }
    .stTextArea textarea:focus,
    .stTextInput input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 2px rgba(37,99,235,0.1) !important;
    }
    .stTextArea label,
    .stTextInput label {
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        color: #555 !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        border-radius: 5px !important;
        padding: 0.3rem 0.8rem !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button[kind="primary"] {
        background: #2563eb !important;
        border: none !important;
        color: #fff !important;
        font-weight: 600 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #1d4ed8 !important;
    }
    .stButton > button[kind="secondary"] {
        background: #fff !important;
        border: 1px solid #d1d5db !important;
        color: #555 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: #999 !important;
        color: #1a1a1a !important;
    }

    /* ── Select box ── */
    .stSelectbox [data-baseweb="select"] {
        font-family: 'IBM Plex Sans', sans-serif !important;
    }
    .stSelectbox [data-baseweb="select"] > div {
        background: #fff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 6px !important;
        font-size: 0.84rem !important;
    }

    /* ── Slider ── */
    .stSlider label {
        font-size: 0.75rem !important;
        color: #555 !important;
    }

    /* ── Metrics ── */
    [data-testid="stMetric"] {
        background: #f8f9fb;
        border: 1px solid #e5e7eb;
        border-radius: 5px;
        padding: 0.4rem 0.6rem;
    }
    [data-testid="stMetric"] label {
        font-size: 0.62rem !important;
        color: #888 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        color: #1a1a1a !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.84rem !important;
        color: #333 !important;
        background: #f8f9fb !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 6px !important;
    }
    /* Fix icon text leak in expanders */
    .streamlit-expanderHeader span[data-testid="stExpanderIconText"] {
        display: none !important;
    }
    details summary span:first-child {
        font-size: 0 !important;
        width: 1rem !important;
        display: inline-block !important;
    }        
    .streamlit-expanderContent {
        border: 1px solid #e5e7eb !important;
        border-top: none !important;
        border-radius: 0 0 6px 6px !important;
        background: #fdfdfe !important;
    }

    /* ── Code blocks ── */
    .stCodeBlock code {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.8rem !important;
        line-height: 1.55 !important;
    }

    /* ── Alerts ── */
    .stAlert {
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 0.82rem !important;
        border-radius: 6px !important;
    }

    /* ── Radio buttons ── */
    .stRadio label {
        font-size: 0.78rem !important;
    }

    /* ── Number input ── */
    .stNumberInput input {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.84rem !important;
        background: #fff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 6px !important;
    }
    .stNumberInput label {
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 0.8rem !important;
    }

    /* ── Dividers ── */
    hr {
        border-color: #e5e7eb !important;
        margin: 0.6rem 0 !important;
    }

    /* ── Captions ── */
    .stCaption, .stCaption p {
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 0.72rem !important;
        color: #999 !important;
    }

    /* ── Plotly chart ── */
    .stPlotlyChart {
        background: #f8f9fb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 0.4rem;
    }

    /* ── Dataframe ── */
    .stDataFrame {
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 0.82rem !important;
        border-radius: 6px;
    }

    /* ── Hide Streamlit branding ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* ── Compact sector pill buttons ── */
    .stTabs [data-baseweb="tab-panel"] .stButton > button {
        padding: 0.15rem 0.55rem !important;
        font-size: 0.68rem !important;
        min-height: 0 !important;
        height: 1.5rem !important;
        line-height: 1 !important;
        border-radius: 4px !important;
        font-weight: 500 !important;
    }

    /* ── Sidebar section labels ── */
    .sidebar-section-label {
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: #999;
        margin-top: 0.3rem;
        margin-bottom: 0.15rem;
        padding-bottom: 0.15rem;
        border-bottom: 1px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

# Models — Pricing verified May 2026 (per 1M tokens)
MODELS = {
    "openai": {
        "gpt-4o-mini": {
            "name": "GPT-4o Mini",
            "type": "LLM",
            "cream": "Low cost · Fast · General · Good accuracy · Text+Vision",
            "input_cost": 0.15,
            "output_cost": 0.60,
        },
        "gpt-4o": {
            "name": "GPT-4o",
            "type": "LLM",
            "cream": "Medium cost · Moderate · General+Expert · High accuracy · Multi-modal",
            "input_cost": 2.50,
            "output_cost": 10.00,
        },
        "gpt-4.1": {
            "name": "GPT-4.1",
            "type": "LLM",
            "cream": "Medium cost · Moderate · Coding+Long context · High accuracy · Text",
            "input_cost": 2.00,
            "output_cost": 8.00,
        },
        "o3": {
            "name": "o3 (Reasoning)",
            "type": "Reasoning",
            "cream": "Medium cost · Slower · Expert reasoning · High accuracy · Text",
            "input_cost": 2.00,
            "output_cost": 8.00,
        },
        "o4-mini": {
            "name": "o4-mini (Reasoning)",
            "type": "Reasoning",
            "cream": "Low cost · Fast reasoning · General · Good accuracy · Text",
            "input_cost": 0.55,
            "output_cost": 2.20,
        },
        "gpt-5.4": {
            "name": "GPT-5.4",
            "type": "LLM",
            "cream": "Medium-high cost · Moderate · Expert · High accuracy · Multi-modal 1M ctx",
            "input_cost": 2.50,
            "output_cost": 15.00,
        },
        "gpt-5.5": {
            "name": "GPT-5.5",
            "type": "LLM",
            "cream": "High cost · Moderate · Expert · Highest accuracy · Multi-modal 1M ctx",
            "input_cost": 5.00,
            "output_cost": 30.00,
        },
    },
    "anthropic": {
        "claude-haiku-4-5-20251001": {
            "name": "Claude Haiku 4.5",
            "type": "LLM",
            "cream": "Low cost · Fast · General · Good accuracy · Text+Vision 200K ctx",
            "input_cost": 1.00,
            "output_cost": 5.00,
        },
        "claude-sonnet-4-6": {
            "name": "Claude Sonnet 4.6",
            "type": "LLM",
            "cream": "Medium cost · Fast · General+Expert · High accuracy · Multi-modal 1M ctx",
            "input_cost": 3.00,
            "output_cost": 15.00,
        },
        "claude-opus-4-6": {
            "name": "Claude Opus 4.6",
            "type": "LLM",
            "cream": "High cost · Moderate · Expert · Highest accuracy · Multi-modal 1M ctx",
            "input_cost": 5.00,
            "output_cost": 25.00,
        },
    },
}

PRICING_DATE = "May 2026"

# Sector templates
SECTOR_TEMPLATES = {
    "custom": {
        "label": "Custom / Blank",
        "context": "",
        "constraints": "",
        "structure": "",
        "checkpoints": "",
        "review": "",
    },
    "general": {
        "label": "General Business",
        "context": "Domain: [your industry]. Audience: [decision-makers/end-users]. Goal: [specific business outcome]. Data sources: [approved references].",
        "constraints": "Tone: professional, concise. No jargon without explanation. No speculation — flag uncertainties. Comply with [relevant policies].",
        "structure": "Format: structured headings. Lead with executive summary. Include: problem definition, analysis, recommendations, risks. Length: [target word count].",
        "checkpoints": "List all assumptions. Flag low-confidence areas. Identify 3 risks with mitigation strategies. Note areas requiring human review.",
        "review": "Human approval required before external distribution. Verify all data points against source. Final decision authority: [role].",
    },
    "healthcare": {
        "label": "Healthcare",
        "context": "Domain: healthcare/clinical. Audience: [clinicians/patients/administrators]. Goal: [clinical outcome/patient safety]. Data sources: [approved clinical guidelines, peer-reviewed sources only].",
        "constraints": "Never provide diagnostic conclusions. Flag all clinical uncertainties. Comply with HIPAA/patient privacy. No fabricated medical data. Tone: empathetic, clear, evidence-based.",
        "structure": "Format: clinical brief. Include: patient context, assessment, evidence-based recommendations, contraindications, follow-up. Plain language summaries for patient-facing content.",
        "checkpoints": "Flag all assumptions about patient conditions. Confidence levels mandatory. Identify drug interaction risks. Areas requiring clinician review: ALL clinical recommendations.",
        "review": "Mandatory clinician review before any patient communication. Escalation trigger: any mention of emergency symptoms. Audit trail required.",
    },
    "fintech": {
        "label": "Financial Services",
        "context": "Domain: financial services/fintech. Audience: [customers/compliance team/regulators]. Goal: [regulatory compliance/customer communication/risk assessment]. Data sources: [RBI guidelines, internal policy documents].",
        "constraints": "No financial advice. Comply with KYC/AML regulations. PII handling per data protection policy. Tone: respectful, transparent. No speculative market commentary.",
        "structure": "Format: [compliance brief/customer communication/risk report]. Include: regulatory references, required disclosures, privacy notices. FAQ section for customer-facing content.",
        "checkpoints": "Flag compliance risks. Document all regulatory assumptions. Friction risk assessment for customer experience. Confidence levels on regulatory interpretations.",
        "review": "Compliance officer approval required. Legal review for any regulatory references. Customer experience impact assessment before deployment.",
    },
    "product": {
        "label": "Product Management",
        "context": "Domain: product development. Audience: [engineering team/stakeholders/users]. Goal: [feature specification/user research/roadmap planning]. Data sources: [customer feedback, analytics, competitive research].",
        "constraints": "Evidence-based claims only. No scope creep — stick to defined feature boundaries. Tone: analytical, PM-focused. Include success metrics for every recommendation.",
        "structure": "Format: structured specification. Include: Jobs-to-be-Done analysis, target user profiles, problem statement, success metrics, constraints, risk factors, acceptance criteria.",
        "checkpoints": "List assumptions about user behavior. Flag missing data points. Identify technical feasibility risks. Note dependencies requiring engineering validation.",
        "review": "Stakeholder alignment check. Engineering feasibility review. User research validation before development commitment.",
    },
    "compliance": {
        "label": "Compliance & Ops",
        "context": "Domain: compliance/operations. Audience: [operations team/auditors/regulators]. Goal: [SOP development/audit preparation/process documentation]. Data sources: [regulatory frameworks, internal policies, audit findings].",
        "constraints": "Exact regulatory citations required. No paraphrasing of legal requirements. Comply with documentation standards. Tone: precise, authoritative. Zero tolerance for ambiguity in process steps.",
        "structure": "Format: SOP/compliance document. Include: role definitions, input requirements, process steps, control points, escalation procedures, SLA specifications, documentation requirements, audit compliance.",
        "checkpoints": "Verify all regulatory citations. Flag process gaps. Identify single points of failure. Document all control points requiring human verification.",
        "review": "Legal/compliance review mandatory. Audit readiness check. Version control and change documentation required.",
    },
    "learning": {
        "label": "Learning & Dev",
        "context": "Domain: education/training. Audience: [learners — specify level and background]. Goal: [knowledge transfer/skill building/assessment]. Data sources: [curriculum standards, approved learning materials].",
        "constraints": "Accessibility: plain language, avoid cultural idioms. Age-appropriate content. No assumptions about prior knowledge unless specified. Include misconception awareness.",
        "structure": "Format: [lesson plan/assessment/learning module]. Include: learning objectives, content delivery, practice activities, assessment criteria, rubric. Bloom's taxonomy alignment.",
        "checkpoints": "Flag assumed prerequisite knowledge. Identify potential misconceptions. Accessibility review. Cultural sensitivity check.",
        "review": "Subject matter expert validation. Accessibility compliance check. Learner feedback integration.",
    },
}


# ─────────────────────────────────────────────
# SYSTEM PROMPTS
# ─────────────────────────────────────────────

SYSTEM_PROMPT_CCSCR = """You are a senior prompt engineer operating under the SAC framework (Supervision over Automation, Accountability Remains Human, Continuous Learning and Adjustment).

Your job: Take a user's rough draft prompt and transform it into a production-grade prompt using the CC-SC-R framework.

## CC-SC-R Framework

C — Context: Domain, audience, goal, data sources, brand voice, quality standards.
C — Constraints: Policies, compliance, PII handling, tone boundaries, prohibited content.
S — Structure: Required sections, format, length, organization, deliverable specs.
C — Checkpoints: Assumption flagging, risk identification, confidence levels, areas needing human review.
R — Review: Human approval points, escalation triggers, edit requirements, accountability chains.

## Your Enhancement Process

1. Analyze the draft prompt and any CC-SC-R fields provided
2. Score the original prompt (1-5 on each CC-SC-R dimension)
3. Enhance the prompt by filling gaps in each dimension
4. Score the enhanced prompt
5. Provide the enhanced prompt in a clean, ready-to-use format

## Output Format — return ONLY valid JSON, no markdown fences, no preamble:

{
  "original_scores": {"context": <1-5>, "constraints": <1-5>, "structure": <1-5>, "checkpoints": <1-5>, "review": <1-5>},
  "enhanced_scores": {"context": <1-5>, "constraints": <1-5>, "structure": <1-5>, "checkpoints": <1-5>, "review": <1-5>},
  "enhanced_prompt": "<the full enhanced prompt ready to use>",
  "changes_made": [{"dimension": "<CC-SC-R dimension>", "change": "<what was added/modified and why>"}],
  "guardrail_warnings": ["<any risks or missing safeguards detected>"],
  "clarifying_question": "<one question to further improve the prompt>"
}"""

SYSTEM_PROMPT_RCT = """You are a senior prompt engineer. Take a user's rough draft prompt and enhance it using the RCT framework (Role, Context, Task).

## RCT Framework

R — Role: Who should the AI act as? What expertise and perspective?
C — Context: What is the situation, audience, and background?
T — Task: What specific output is needed? Format, length, constraints?

## Your Enhancement Process

1. Analyze the draft prompt and any RCT fields provided
2. Score the original prompt (1-5 on each RCT dimension)
3. Enhance the prompt by filling gaps
4. Score the enhanced prompt

## Output Format — return ONLY valid JSON, no markdown fences, no preamble:

{
  "original_scores": {"role": <1-5>, "context": <1-5>, "task": <1-5>},
  "enhanced_scores": {"role": <1-5>, "context": <1-5>, "task": <1-5>},
  "enhanced_prompt": "<the full enhanced prompt ready to use>",
  "changes_made": [{"dimension": "<RCT dimension>", "change": "<what was added/modified and why>"}],
  "guardrail_warnings": ["<any risks or missing safeguards detected>"],
  "clarifying_question": "<one question to further improve the prompt>"
}"""


# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "max_tokens": 2048,
        "mode": "CC-SC-R",  # or "RCT"
        "sector": "custom",
        # CC-SC-R fields
        "ctx": "",
        "con": "",
        "stru": "",
        "chk": "",
        "rev": "",
        # RCT fields
        "role": "",
        "rct_context": "",
        "task": "",
        # Draft
        "draft": "",
        # Results
        "result": None,
        "versions": [],
        "session_log": [],
        # Test run
        "test_result": None,
        # Tracing
        "last_trace": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ─────────────────────────────────────────────
# HELPER: COST CALCULATION
# ─────────────────────────────────────────────
def calc_cost(provider, model_id, input_tokens, output_tokens):
    m = MODELS.get(provider, {}).get(model_id)
    if not m:
        return 0.0
    return (m["input_cost"] * input_tokens / 1_000_000) + (m["output_cost"] * output_tokens / 1_000_000)


# ─────────────────────────────────────────────
# HELPER: RADAR CHART
# ─────────────────────────────────────────────
def make_radar(original_scores, enhanced_scores, dimensions):
    fig = go.Figure()
    cats = dimensions + [dimensions[0]]  # close the polygon

    orig_vals = [original_scores.get(d.lower(), 0) for d in dimensions] + [original_scores.get(dimensions[0].lower(), 0)]
    enh_vals = [enhanced_scores.get(d.lower(), 0) for d in dimensions] + [enhanced_scores.get(dimensions[0].lower(), 0)]

    fig.add_trace(go.Scatterpolar(r=orig_vals, theta=cats, fill="toself", name="Before", line_color="#dc2626", opacity=0.6, fillcolor="rgba(220,38,38,0.08)"))
    fig.add_trace(go.Scatterpolar(r=enh_vals, theta=cats, fill="toself", name="After", line_color="#2563eb", opacity=0.7, fillcolor="rgba(37,99,235,0.1)"))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], dtick=1, gridcolor="#e5e7eb", linecolor="#e5e7eb", tickfont=dict(color="#999", size=10, family="IBM Plex Mono")),
            angularaxis=dict(gridcolor="#e5e7eb", linecolor="#e5e7eb", tickfont=dict(color="#555", size=11, family="IBM Plex Sans")),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=True,
        height=320,
        margin=dict(l=50, r=50, t=25, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12, family="IBM Plex Sans", color="#333"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(size=11, color="#666")),
    )
    return fig


# ─────────────────────────────────────────────
# HELPER: API CALLS
# ─────────────────────────────────────────────
def call_openai(api_key, model, system_prompt, user_message, temperature, max_tokens):
    client = OpenAI(api_key=api_key)
    start = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    latency = time.time() - start
    content = response.choices[0].message.content
    usage = {
        "input_tokens": response.usage.prompt_tokens if response.usage else 0,
        "output_tokens": response.usage.completion_tokens if response.usage else 0,
        "total_tokens": response.usage.total_tokens if response.usage else 0,
    }
    return content, usage, latency


def call_anthropic(api_key, model, system_prompt, user_message, temperature, max_tokens):
    client = Anthropic(api_key=api_key)
    start = time.time()
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
        temperature=temperature,
    )
    latency = time.time() - start
    content = response.content[0].text
    usage = {
        "input_tokens": response.usage.input_tokens if response.usage else 0,
        "output_tokens": response.usage.output_tokens if response.usage else 0,
        "total_tokens": (response.usage.input_tokens or 0) + (response.usage.output_tokens or 0),
    }
    return content, usage, latency


def call_model(api_key, provider, model, system_prompt, user_message, temperature, max_tokens):
    if provider == "openai":
        return call_openai(api_key, model, system_prompt, user_message, temperature, max_tokens)
    else:
        return call_anthropic(api_key, model, system_prompt, user_message, temperature, max_tokens)


def parse_json_response(content):
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    cleaned = cleaned.strip()
    return json.loads(cleaned)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Prompt Enhancer v2")

    # ── SECTION: Connection ──
    st.markdown('<div class="sidebar-section-label">Connection</div>', unsafe_allow_html=True)

    st.session_state.provider = st.radio(
        "Provider",
        ["openai", "anthropic"],
        format_func=lambda x: "OpenAI" if x == "openai" else "Anthropic",
        horizontal=True,
        label_visibility="collapsed",
    )

    api_key = st.text_input(
        "API Key",
        type="password",
        placeholder="sk-..." if st.session_state.provider == "openai" else "sk-ant-...",
        help="Session-only. Never stored.",
    )

    # ── SECTION: CREAM — Model Selection ──
    st.markdown('<div class="sidebar-section-label">CREAM — Model Selection</div>', unsafe_allow_html=True)

    provider_models = MODELS[st.session_state.provider]
    model_options = list(provider_models.keys())
    model_labels = [f"{provider_models[m]['name']}  [{provider_models[m]['type']}]" for m in model_options]

    selected_idx = st.selectbox(
        "Select model",
        range(len(model_options)),
        format_func=lambda i: model_labels[i],
        label_visibility="collapsed",
    )
    st.session_state.model = model_options[selected_idx]
    sel_model = provider_models[st.session_state.model]

    st.caption(f"{sel_model['cream']}")
    st.caption(f"${sel_model['input_cost']}/M in · ${sel_model['output_cost']}/M out · Verified {PRICING_DATE}")

    # ── SECTION: Parameters ──
    st.markdown('<div class="sidebar-section-label">Parameters</div>', unsafe_allow_html=True)

    st.session_state.temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.temperature,
        step=0.1,
        help="Lower = more consistent output. Higher = more varied. Default 0.0 for prompt enhancement.",
    )

    # ── SECTION: Framework Mode ──
    st.markdown('<div class="sidebar-section-label">Framework Mode</div>', unsafe_allow_html=True)

    st.session_state.mode = st.radio(
        "Mode",
        ["CC-SC-R", "RCT"],
        help="CC-SC-R: 5-field advanced. RCT: 3-field simple.",
        horizontal=True,
        label_visibility="collapsed",
    )

    # ── SECTION: Observability ──
    if st.session_state.session_log:
        st.markdown('<div class="sidebar-section-label">Observability</div>', unsafe_allow_html=True)

        logs = st.session_state.session_log
        total_tokens = sum(l["total_tokens"] for l in logs)
        total_cost = sum(l["cost"] for l in logs)
        avg_latency = sum(l["latency"] for l in logs) / len(logs)

        c1, c2 = st.columns(2)
        c1.metric("Calls", len(logs))
        c2.metric("Tokens", f"{total_tokens:,}")
        c3, c4 = st.columns(2)
        c3.metric("Cost", f"${total_cost:.6f}")
        c4.metric("Latency", f"{avg_latency:.1f}s")

    # ── Footer ──
    st.markdown("---")
    st.caption("SAC: AI assists. Humans decide.")


# ─────────────────────────────────────────────
# MAIN AREA — TABS
# ─────────────────────────────────────────────
tab_enhance, tab_results, tab_test, tab_observe, tab_learn = st.tabs(
    ["Enhance", "Results", "Test Run", "Observability", "Learn"]
)


# ═══════════════════════════════════════════════
# TAB 1: ENHANCE
# ═══════════════════════════════════════════════
with tab_enhance:

    if st.session_state.mode == "CC-SC-R":
        # Sector template selector — compact row
        sector_keys = list(SECTOR_TEMPLATES.keys())
        # Split into two rows of 4 for better fit
        row1_keys = sector_keys[:4]
        row2_keys = sector_keys[4:]

        cols1 = st.columns(len(row1_keys))
        for i, key in enumerate(row1_keys):
            with cols1[i]:
                if st.button(SECTOR_TEMPLATES[key]["label"], key=f"sector_{key}", use_container_width=True,
                             type="primary" if st.session_state.sector == key else "secondary"):
                    st.session_state.sector = key
                    st.session_state.ctx = SECTOR_TEMPLATES[key]["context"]
                    st.session_state.con = SECTOR_TEMPLATES[key]["constraints"]
                    st.session_state.stru = SECTOR_TEMPLATES[key]["structure"]
                    st.session_state.chk = SECTOR_TEMPLATES[key]["checkpoints"]
                    st.session_state.rev = SECTOR_TEMPLATES[key]["review"]
                    st.rerun()

        if row2_keys:
            cols2 = st.columns(len(row2_keys) + 1)  # extra col for spacing
            for i, key in enumerate(row2_keys):
                with cols2[i]:
                    if st.button(SECTOR_TEMPLATES[key]["label"], key=f"sector_{key}", use_container_width=True,
                                 type="primary" if st.session_state.sector == key else "secondary"):
                        st.session_state.sector = key
                        st.session_state.ctx = SECTOR_TEMPLATES[key]["context"]
                        st.session_state.con = SECTOR_TEMPLATES[key]["constraints"]
                        st.session_state.stru = SECTOR_TEMPLATES[key]["structure"]
                        st.session_state.chk = SECTOR_TEMPLATES[key]["checkpoints"]
                        st.session_state.rev = SECTOR_TEMPLATES[key]["review"]
                        st.rerun()

        # Two-column layout: CC-SC-R fields left, Draft right
        left_col, right_col = st.columns([1, 1], gap="large")

        with left_col:
            st.markdown("#### CC-SC-R Fields")
            st.session_state.ctx = st.text_area(
                "C — Context", value=st.session_state.ctx, height=85,
                help="Domain, audience, goal, data sources, brand voice",
            )
            st.session_state.con = st.text_area(
                "C — Constraints", value=st.session_state.con, height=85,
                help="Policies, compliance, PII handling, tone boundaries",
            )
            st.session_state.stru = st.text_area(
                "S — Structure", value=st.session_state.stru, height=85,
                help="Required sections, format, length, deliverable specs",
            )
            st.session_state.chk = st.text_area(
                "C — Checkpoints", value=st.session_state.chk, height=85,
                help="Assumptions, risks, confidence levels, human review areas",
            )
            st.session_state.rev = st.text_area(
                "R — Review", value=st.session_state.rev, height=85,
                help="Human approval points, escalation triggers, accountability",
            )

        with right_col:
            st.markdown("#### Draft Prompt")
            st.session_state.draft = st.text_area(
                "Paste your rough prompt here",
                value=st.session_state.draft,
                height=530,
                label_visibility="collapsed",
                placeholder="Write your rough prompt here.\n\nThe enhancer will transform it using the CC-SC-R framework on the left.",
            )

    else:  # RCT mode
        left_col, right_col = st.columns([1, 1], gap="large")

        with left_col:
            st.markdown("#### RCT Fields")
            st.session_state.role = st.text_input(
                "R — Role", value=st.session_state.role,
                help="Who should the AI act as? What expertise?",
                placeholder="e.g., a senior financial analyst with 10 years experience",
            )
            st.session_state.rct_context = st.text_area(
                "C — Context", value=st.session_state.rct_context, height=120,
                help="Situation, audience, background",
                placeholder="e.g., preparing quarterly earnings summary for the board",
            )
            st.session_state.task = st.text_area(
                "T — Task", value=st.session_state.task, height=120,
                help="Specific output needed, format, length, constraints",
                placeholder="e.g., produce a 2-page brief with key metrics, trends, and risks",
            )

        with right_col:
            st.markdown("#### Draft Prompt")
            st.session_state.draft = st.text_area(
                "Paste your rough prompt here",
                value=st.session_state.draft,
                height=340,
                label_visibility="collapsed",
                placeholder="Write your rough prompt here.\n\nThe enhancer will transform it using the RCT framework on the left.",
            )

    # Enhance button — full width below both columns
    col_btn, col_spacer = st.columns([1, 3])
    with col_btn:
        enhance_clicked = st.button("Enhance Prompt", type="primary", use_container_width=True)

    if enhance_clicked:
        if not api_key:
            st.error("Enter your API key in the sidebar.")
        elif not st.session_state.draft.strip():
            st.warning("Enter a draft prompt first.")
        else:
            # Build user message
            if st.session_state.mode == "CC-SC-R":
                system_prompt = SYSTEM_PROMPT_CCSCR
                user_message = f"""SECTOR: {SECTOR_TEMPLATES[st.session_state.sector]['label']}

CONTEXT: {st.session_state.ctx}
CONSTRAINTS: {st.session_state.con}
STRUCTURE: {st.session_state.stru}
CHECKPOINTS: {st.session_state.chk}
REVIEW: {st.session_state.rev}

USER DRAFT PROMPT:
{st.session_state.draft}

Enhance this prompt using the CC-SC-R framework. Return ONLY valid JSON."""
            else:
                system_prompt = SYSTEM_PROMPT_RCT
                user_message = f"""ROLE: {st.session_state.role}
CONTEXT: {st.session_state.rct_context}
TASK: {st.session_state.task}

USER DRAFT PROMPT:
{st.session_state.draft}

Enhance this prompt using the RCT framework. Return ONLY valid JSON."""

            with st.spinner(f"Enhancing with {sel_model['name']}..."):
                try:
                    content, usage, latency = call_model(
                        api_key,
                        st.session_state.provider,
                        st.session_state.model,
                        system_prompt,
                        user_message,
                        st.session_state.temperature,
                        st.session_state.max_tokens,
                    )

                    parsed = parse_json_response(content)
                    cost = calc_cost(
                        st.session_state.provider,
                        st.session_state.model,
                        usage["input_tokens"],
                        usage["output_tokens"],
                    )

                    # Save trace
                    st.session_state.last_trace = {
                        "system_prompt": system_prompt,
                        "user_message": user_message,
                        "raw_response": content,
                        "parsed": parsed,
                        "usage": usage,
                        "latency": latency,
                        "cost": cost,
                        "model": st.session_state.model,
                        "provider": st.session_state.provider,
                        "temperature": st.session_state.temperature,
                    }

                    # Save log
                    log_entry = {
                        "timestamp": time.strftime("%H:%M:%S"),
                        "provider": st.session_state.provider,
                        "model": st.session_state.model,
                        "mode": st.session_state.mode,
                        "input_tokens": usage["input_tokens"],
                        "output_tokens": usage["output_tokens"],
                        "total_tokens": usage["total_tokens"],
                        "cost": cost,
                        "latency": latency,
                        "version": len(st.session_state.versions) + 1,
                    }
                    st.session_state.session_log.append(log_entry)

                    # Save version
                    st.session_state.versions.append({
                        "draft": st.session_state.draft,
                        "result": parsed,
                        "log": log_entry,
                        "mode": st.session_state.mode,
                    })

                    st.session_state.result = parsed
                    st.success("Enhancement complete. See the Results tab.")

                except json.JSONDecodeError:
                    st.error("The model returned invalid JSON. Try again or switch models.")
                    st.session_state.last_trace = {
                        "system_prompt": system_prompt,
                        "user_message": user_message,
                        "raw_response": content,
                        "parsed": None,
                        "error": "JSON parse failed",
                    }
                except Exception as e:
                    st.error(f"Error: {e}")


# ═══════════════════════════════════════════════
# TAB 2: RESULTS
# ═══════════════════════════════════════════════
with tab_results:
    result = st.session_state.result

    if not result:
        st.info("Run an enhancement first to see results here.")
    else:
        # Radar chart
        if st.session_state.mode == "CC-SC-R":
            dims = ["Context", "Constraints", "Structure", "Checkpoints", "Review"]
        else:
            dims = ["Role", "Context", "Task"]

        st.markdown("#### Before / After Score")
        fig = make_radar(result.get("original_scores", {}), result.get("enhanced_scores", {}), dims)
        st.plotly_chart(fig, use_container_width=True)

        # Score summary
        orig_scores = result.get("original_scores", {})
        enh_scores = result.get("enhanced_scores", {})
        orig_avg = sum(orig_scores.values()) / len(orig_scores) if orig_scores else 0
        enh_avg = sum(enh_scores.values()) / len(enh_scores) if enh_scores else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Before (avg)", f"{orig_avg:.1f}/5")
        c2.metric("After (avg)", f"{enh_avg:.1f}/5")
        c3.metric("Improvement", f"+{enh_avg - orig_avg:.1f}")

        st.markdown("---")

        # Enhanced prompt
        st.markdown("#### Enhanced Prompt")
        st.code(result.get("enhanced_prompt", ""), language=None)
        if st.button("Copy to clipboard", key="copy_enhanced"):
            st.write("Copied!")
            st.toast("Prompt copied to clipboard")

        st.markdown("---")

        # Changes made
        st.markdown("#### What Changed and Why")
        changes = result.get("changes_made", [])
        for ch in changes:
            st.markdown(f"**{ch.get('dimension', '')}** — {ch.get('change', '')}")

        # Guardrail warnings
        warnings = result.get("guardrail_warnings", [])
        if warnings:
            st.markdown("---")
            st.markdown("#### Guardrail Warnings")
            for w in warnings:
                st.warning(w)

        # Clarifying question
        cq = result.get("clarifying_question", "")
        if cq:
            st.markdown("---")
            st.info(f"**Suggested clarification:** {cq}")

        # Call stats
        if st.session_state.session_log:
            log = st.session_state.session_log[-1]
            st.markdown("---")
            st.caption(
                f"{log['model']} | "
                f"{log['input_tokens']} in · {log['output_tokens']} out | "
                f"${log['cost']:.6f} | "
                f"{log['latency']:.1f}s"
            )


# ═══════════════════════════════════════════════
# TAB 3: TEST RUN
# ═══════════════════════════════════════════════
with tab_test:
    st.markdown("#### Test Your Enhanced Prompt")
    st.caption("Run the enhanced prompt against the selected model to see actual output quality.")

    if not st.session_state.result:
        st.info("Enhance a prompt first, then come here to test it.")
    else:
        enhanced = st.session_state.result.get("enhanced_prompt", "")
        st.text_area("Enhanced prompt to test", value=enhanced, height=150, disabled=True)

        test_input = st.text_area(
            "Optional: provide sample input for the prompt",
            height=85,
            placeholder="e.g., if your prompt expects a document, paste a sample here. Leave blank to test the prompt as-is.",
        )

        if st.button("Run Test", type="primary"):
            if not api_key:
                st.error("Enter your API key in the sidebar.")
            else:
                test_prompt = enhanced
                if test_input.strip():
                    test_prompt = f"{enhanced}\n\nINPUT:\n{test_input}"

                with st.spinner(f"Testing with {sel_model['name']}..."):
                    try:
                        content, usage, latency = call_model(
                            api_key,
                            st.session_state.provider,
                            st.session_state.model,
                            "You are a helpful assistant. Follow the user's prompt precisely.",
                            test_prompt,
                            st.session_state.temperature,
                            st.session_state.max_tokens,
                        )

                        cost = calc_cost(
                            st.session_state.provider,
                            st.session_state.model,
                            usage["input_tokens"],
                            usage["output_tokens"],
                        )

                        log_entry = {
                            "timestamp": time.strftime("%H:%M:%S"),
                            "provider": st.session_state.provider,
                            "model": st.session_state.model,
                            "mode": "test_run",
                            "input_tokens": usage["input_tokens"],
                            "output_tokens": usage["output_tokens"],
                            "total_tokens": usage["total_tokens"],
                            "cost": cost,
                            "latency": latency,
                            "version": "test",
                        }
                        st.session_state.session_log.append(log_entry)

                        st.markdown("#### Test Output")
                        st.write(content)

                        st.caption(
                            f"{log_entry['model']} | "
                            f"{log_entry['input_tokens']} in · {log_entry['output_tokens']} out | "
                            f"${cost:.6f} | "
                            f"{latency:.1f}s"
                        )

                    except Exception as e:
                        st.error(f"Test failed: {e}")


# ═══════════════════════════════════════════════
# TAB 4: OBSERVABILITY
# ═══════════════════════════════════════════════
with tab_observe:
    st.markdown("#### Session Observability")
    st.caption("Evals = did you build it right? | Monitoring = is it still working?")

    if not st.session_state.session_log:
        st.info("No calls yet. Enhance a prompt to start tracking.")
    else:
        logs = st.session_state.session_log

        # Summary metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total calls", len(logs))
        c2.metric("Total tokens", f"{sum(l['total_tokens'] for l in logs):,}")
        c3.metric("Total cost", f"${sum(l['cost'] for l in logs):.6f}")
        c4.metric("Avg latency", f"{sum(l['latency'] for l in logs) / len(logs):.1f}s")

        st.markdown("---")

        # Call log table
        st.markdown("#### Call Log")
        log_data = []
        for l in logs:
            log_data.append({
                "Time": l["timestamp"],
                "Provider": l["provider"],
                "Model": l["model"],
                "Type": l["mode"],
                "Tokens": l["total_tokens"],
                "Cost": f"${l['cost']:.6f}",
                "Latency": f"{l['latency']:.1f}s",
            })
        st.dataframe(log_data, use_container_width=True)

        # Version history
        if st.session_state.versions:
            st.markdown("---")
            st.markdown("#### Version History")

            for i, v in enumerate(st.session_state.versions):
                vlog = v["log"]
                orig = v["result"].get("original_scores", {})
                enh = v["result"].get("enhanced_scores", {})
                orig_avg = sum(orig.values()) / len(orig) if orig else 0
                enh_avg = sum(enh.values()) / len(enh) if enh else 0

                with st.expander(f"v{i+1} — {vlog['model']} — Score: {orig_avg:.1f} to {enh_avg:.1f} — {vlog['timestamp']}"):
                    st.markdown("**Draft:**")
                    st.text(v["draft"][:500])
                    st.markdown("**Enhanced:**")
                    st.text(v["result"].get("enhanced_prompt", "")[:500])

        # Pipeline trace (debug)
        if st.session_state.last_trace:
            st.markdown("---")
            st.markdown("#### Pipeline Trace (Debug)")
            trace = st.session_state.last_trace

            with st.expander("System prompt sent"):
                st.code(trace.get("system_prompt", ""), language=None)

            with st.expander("User message sent"):
                st.code(trace.get("user_message", ""), language=None)

            with st.expander("Raw API response"):
                st.code(trace.get("raw_response", "")[:3000], language=None)

            if trace.get("usage"):
                st.caption(
                    f"Model: {trace.get('model')} | "
                    f"Temp: {trace.get('temperature')} | "
                    f"Tokens: {trace['usage']['total_tokens']} | "
                    f"Latency: {trace.get('latency', 0):.1f}s | "
                    f"Cost: ${trace.get('cost', 0):.6f}"
                )


# ═══════════════════════════════════════════════
# TAB 5: LEARN
# ═══════════════════════════════════════════════
with tab_learn:
    st.markdown("#### Framework Reference")
    st.caption("The 7 frameworks from the C40 Accelerator — applied to prompt engineering.")

    with st.expander("CC-SC-R — Professional Prompting", expanded=True):
        st.markdown("""
**Context** — Domain, audience, goal, data sources, brand voice, quality standards.
**Constraints** — Policies, compliance, PII handling, tone boundaries, prohibited content.
**Structure** — Required sections, format, length, organization, deliverable specs.
**Checkpoints** — Assumption flagging, risk identification, confidence levels, human review areas.
**Review** — Human approval points, escalation triggers, edit requirements, accountability.

_Every enhanced prompt in this tool is scored against these 5 dimensions._
""")

    with st.expander("RCT — Simple Prompting"):
        st.markdown("""
**Role** — Who should the AI act as? What expertise and perspective?
**Context** — What is the situation, audience, and background?
**Task** — What specific output is needed? Format, length, constraints?

_Use RCT for quick, everyday prompts. Switch to CC-SC-R for production-grade work._
""")

    with st.expander("SAC — AI Management Philosophy"):
        st.markdown("""
**Supervision** — Humans oversee AI output. AI is the intern, you are the manager.
**Accountability** — The human remains accountable for all decisions. AI assists, humans decide.
**Continuous Learning** — Iterate prompts, review results, improve over time.

_This tool embeds SAC: it scores, explains, and flags — but YOU make the final call._
""")

    with st.expander("CREAM — Model Selection"):
        st.markdown("""
**C — Cost:** What's your budget per query / per month?
**R — Response Time:** Real-time or batch? Does speed matter?
**E — Expertise:** General knowledge or specialized domain?
**A — Accuracy:** What's the cost of being wrong?
**M — Modality:** Text only, or images/audio/video too?

_The sidebar model selector shows CREAM profiles for each model. Match model to task._
""")

    with st.expander("MWAPA — Application Architecture"):
        st.markdown("""
**Model** — The AI brain. Receives prompt, produces output. That's all.
**Workflow** — Business logic, pre/post processing, routing rules around the model.
**Agent** — Autonomous decision-maker with tools, memory, and goals.
**Platform** — Infrastructure: APIs, databases, auth, logging, cost management.
**Application** — The user-facing product.

_This tool is an Application (A) that helps you craft better inputs for the Model layer (M). 80% of AI product value lives outside the model._
""")

    with st.expander("Autonomy Levels — Agent Decision Framework"):
        st.markdown("""
**L1 Consultant** — AI gives advice. You decide and act. (e.g., ChatGPT answering a question)
**L2 Technician** — AI executes a single scoped task. (e.g., "send this email")
**L3 Contractor** — AI executes multi-step workflows autonomously. (e.g., research + synthesize + report)
**L4 Team** — Multiple AI agents coordinating in parallel. (e.g., monitor + draft + update CRM)

_Start at the lowest level that solves your problem. Higher autonomy = stricter Constraints, Checkpoints, and Review in your prompt._
""")

    with st.expander("Evals and Monitoring"):
        st.markdown("""
**Evals** — "Did you build it right?" Run before deployment. You control inputs, you know expected outputs. Pass/fail.
**Monitoring** — "Is it still working?" Runs after deployment, continuously. Users control inputs. Watch for drift.
**Observability = Evals + Monitoring + Tracing.**

_The Observability tab in this tool tracks tokens, cost, latency, and version history. The Pipeline Trace shows every step of the enhancement call for debugging._

**What to monitor:** Error rate, latency, output quality drift, user feedback, cost trends.
""")

    # If we have results, show contextual learning
    if st.session_state.result and st.session_state.mode == "CC-SC-R":
        st.markdown("---")
        st.markdown("#### Your Prompt Through the Frameworks")

        scores = st.session_state.result.get("original_scores", {})
        weakest = min(scores, key=scores.get) if scores else None
        strongest = max(scores, key=scores.get) if scores else None

        if weakest and strongest:
            st.markdown(
                f"Your draft prompt scored lowest on **{weakest.title()}** ({scores[weakest]}/5) "
                f"and highest on **{strongest.title()}** ({scores[strongest]}/5). "
                f"The enhancer filled the gaps — check the Results tab to see exactly what was added."
            )

            if scores.get("checkpoints", 5) <= 2:
                st.markdown(
                    "_Low Checkpoints score means your prompt didn't ask the AI to flag assumptions or risks. "
                    "For high-stakes tasks (healthcare, compliance, finance), this is critical._"
                )
            if scores.get("review", 5) <= 2:
                st.markdown(
                    "_Low Review score means no human approval points were specified. "
                    "SAC principle: accountability remains human. Add review gates._"
                )