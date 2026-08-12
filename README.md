# Human Performance Simulation Lab

A web-based human-factors research platform for studying how cognitive load,
distraction, task switching, working memory, interference, and interface
interaction patterns affect task performance.

## Project Status

### Phase 1 — MVP ✅
- Timed tasks
- Accuracy tracking
- Response-time measurement
- Cognitive-load self-rating
- SQLite persistence
- Analytics dashboard

### Phase 2 — Human Factors ✅
- Stroop-style interference
- Working-memory trials
- Simulated distraction events
- Task-switch trials

### Phase 3 — Research Layer ✅
- Consent workflow
- Anonymous participant IDs
- Randomized conditions
- Effect-size calculations
- Research CSV export
- Research-method documentation

### Phase 4 — Web Research Platform ✅
- Interaction-event telemetry
- Element-level click-frequency heatmap
- Session replay
- Keyboard-only response task
- Accessibility/usability audit
- Research administrator dashboard
- Repeated-measures summaries
- Optional FastAPI research API

## Architecture

```text
Participant
   |
   v
Streamlit Research UI
   |
   +--> Experiment Engine
   |      +-- Medication Match
   |      +-- Stroop
   |      +-- Working Memory
   |      +-- Keyboard Response
   |
   +--> Interaction Telemetry
   |
   +--> Accessibility Audit
   |
   v
SQLite Research Database
   |
   +--> Analytics Dashboard
   +--> Session Replay
   +--> Admin View
   +--> CSV Export
   |
   v
Optional FastAPI Research API
```

## Run the Streamlit App

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Windows:

```bash
.venv\Scripts\activate
```

## Run the Optional FastAPI Backend

In a second terminal:

```bash
source .venv/bin/activate
uvicorn research_api:app --reload --port 8000
```

Then visit the interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

## Research Variables

### Independent variables
- Experimental condition
- Distraction presence
- Task-switch status
- Task type
- Difficulty

### Dependent variables
- Accuracy
- Response time
- Cognitive-load rating
- Interaction frequency
- Accessibility audit score

## Interaction Heatmap

Phase 4 uses an **element-level click-frequency heatmap** rather than storing raw
screen coordinates. This is simpler, more privacy-preserving, and still useful
for identifying which UI targets receive the most interaction.

## Portfolio Description

**Human Performance Simulation Lab — Python, Streamlit, FastAPI, SQLite**

Developed a human-factors research platform for studying cognitive load,
attention, working memory, task switching, and interaction behavior under
randomized experimental conditions. Built trial-level telemetry, session replay,
UI interaction heatmaps, keyboard-accessibility testing, anonymized participant
tracking, repeated-measures analysis, effect-size calculations, and an optional
FastAPI backend for multi-user research data access.

## Disclaimer

This is a student research and usability prototype. It is not a medical device,
validated cognitive assessment, clinical decision-support tool, or IRB-approved
clinical study.
