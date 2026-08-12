# Cognitive Load Training Simulator

A lightweight healthcare-simulation research prototype for studying how task
difficulty affects accuracy, response time, and perceived cognitive load.

## Why this project

The project demonstrates several skills relevant to healthcare simulation and
human-factors research:

- Python application development
- Experimental task design
- Human-computer interaction
- Cognitive load measurement
- Response-time telemetry
- SQLite data persistence
- Research analytics
- Testing and documentation

## Features

- Five-task experiment sessions
- Difficulty levels from 1–5
- Increasingly similar answer choices
- Optional distraction cues at higher difficulty
- Per-task cognitive-load self-rating
- Accuracy and response-time tracking
- Automatic SQLite logging
- Analytics dashboard
- CSV export

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Suggested experiment

**Research question:** How does increasing task difficulty affect user accuracy,
response time, and perceived cognitive load?

Run several sessions at difficulty levels 1–5. Compare:

- Accuracy
- Mean response time
- Mean cognitive-load rating
- Error frequency

## Portfolio improvements

1. Add randomized visual/auditory distractions.
2. Add Stroop-style interference tasks.
3. Add adaptive difficulty.
4. Add participant anonymization and study consent flow.
5. Add statistical significance testing.
6. Add a Unity/C# front end that sends telemetry to the Python analytics layer.

## Disclaimer

This project is a research and usability prototype only. It is not medical
advice, a clinical decision system, or a validated medical training product.
