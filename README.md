# Human Performance Simulation Lab

A web-based human-factors research prototype for studying how cognitive load, distraction, task switching, working memory, and interference affect task performance in simulated healthcare-training scenarios.

## Project Status

### Phase 1 — MVP ✅
- Timed tasks
- Difficulty levels
- Accuracy tracking
- Response-time measurement
- Cognitive-load self-rating
- SQLite persistence
- Analytics dashboard

### Phase 2 — Human Factors ✅
- Stroop-style interference tasks
- Working-memory trials
- Simulated distraction events
- Task-switch trials
- Trial-level human-factors telemetry

### Phase 3 — Research Layer ✅
- Participant consent flow
- Anonymous participant IDs
- Randomized experimental conditions
- Condition-level research analysis
- Cohen's d effect-size calculations
- Anonymized CSV export
- Research-method documentation

## Research Question

> How do distraction, task switching, working-memory demands, and interference affect accuracy, response time, and perceived cognitive load during simulated healthcare-training tasks?

## Tech Stack

- Python
- Streamlit
- SQLite
- Pandas

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Experimental Conditions

Participants are randomly assigned to Control, Moderate Load, or High Load conditions. Conditions vary the probability of distractions, Stroop interference, working-memory demands, and task switching.

## Recorded Variables

- anonymous participant ID
- experimental condition
- task type
- difficulty
- correctness
- response time
- cognitive-load rating
- distraction presence
- task-switch indicator
- timestamp

## Portfolio Description

**Human Performance Simulation Lab — Python, Streamlit, SQLite**

Developed a human-factors research platform that measures accuracy, response time, cognitive load, and task-switching performance under randomized experimental conditions. Implemented Stroop-style interference, working-memory tasks, distraction trials, anonymized participant tracking, persistent telemetry, effect-size analysis, and research-data export.

## Disclaimer

This project is a student research and usability prototype. It is not a medical device, validated cognitive assessment, clinical decision-support system, or IRB-approved clinical study.
