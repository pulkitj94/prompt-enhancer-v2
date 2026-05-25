# Prompt Enhancer v2

Transforms rough prompts into production-grade prompts using the CC-SC-R and RCT frameworks.

## Frameworks Used

- **CC-SC-R** — Context, Constraints, Structure, Checkpoints, Review
- **RCT** — Role, Context, Task (simple mode)
- **SAC** — Supervision, Accountability, Continuous Learning
- **CREAM** — Cost, Response Time, Expertise, Accuracy, Modality (model selection)
- **MWAPA** — Model, Workflow, Agent, Platform, Application
- **Autonomy Levels** — L1 Consultant to L4 Team
- **Evals & Monitoring** — Observability = Evals + Monitoring + Tracing

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Features

- Dual provider support (OpenAI + Anthropic)
- CC-SC-R advanced mode / RCT simple mode toggle
- Sector templates with pre-filled fields
- Before/after radar chart scoring
- Change explanations and guardrail warnings
- Test Run panel — run enhanced prompts and see output
- Observability dashboard — tokens, cost, latency, version history
- Pipeline tracing for debugging
- Learn tab — all 7 frameworks explained with contextual insights

## Model Pricing

Prices verified May 2026. Update the `MODELS` dict in `app.py` when pricing changes.