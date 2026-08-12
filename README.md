# 🧠 Human Performance Simulation Lab

A production-style, web-based human-factors research platform for studying how
cognitive load, distraction, task switching, working memory, interference,
accessibility, and interaction behavior affect performance in simulated
healthcare-training tasks.

## Live Demo

```text
https://cognitive-load-training-simulator.streamlit.app/
```

## Phase 5 Engineering Upgrade

The platform now includes:

- PostgreSQL-ready persistence with SQLAlchemy
- SQLite fallback for local development
- Docker and Docker Compose
- Automated pytest coverage
- GitHub Actions CI
- Researcher login
- YAML-configurable study protocols
- Multi-user-safe participant and session IDs
- Browser telemetry ingestion through FastAPI
- Embedded browser-event telemetry component
- Eye-tracking data ingestion/analysis adapter
- Advanced statistical analysis
- FastAPI research API

## Architecture

```text
Participants
    |
    v
Streamlit Research UI
    |
    +---- Experiment Engine
    +---- Accessibility Audit
    +---- Browser Telemetry Component
    +---- Eye-Tracking Data Import
    |
    v
SQLAlchemy Persistence Layer
    |
    +---- SQLite (local)
    |
    +---- PostgreSQL (Docker / deployment)
    |
    v
Analytics + Admin Dashboard
    |
    +---- FastAPI Research API
    +---- CSV Export
    +---- Statistical Analysis
```

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

In a second terminal:

```bash
source .venv/bin/activate
uvicorn research_api:app --reload --port 8000
```

## Run with Docker + PostgreSQL

```bash
docker compose up --build
```

Then open:

```text
Streamlit: http://localhost:8501
FastAPI:   http://localhost:8000/docs
```

The Docker stack runs:

- Streamlit app
- FastAPI service
- PostgreSQL database

## Researcher Authentication

For local development the defaults are:

```text
Username: admin
Password: change-me
```

Change them before deployment using environment variables:

```bash
export RESEARCHER_USERNAME="your-user"
export RESEARCHER_PASSWORD="your-strong-password"
```

Never commit production credentials.

## Configurable Study Protocols

The active experiment is defined in:

```text
config/default_study.yaml
```

You can modify:

- study metadata
- number of tasks
- condition probabilities
- distraction probability
- task-switch probability
- Stroop probability
- working-memory behavior

without modifying the experiment engine.

## Browser Telemetry

The FastAPI endpoint accepts browser-native events including:

- visibility changes
- viewport changes
- sampled pointer coordinates
- custom interaction events

The included Streamlit component demonstrates telemetry inside its own sandboxed
iframe.

Full capture of arbitrary Streamlit DOM events would require a dedicated
Streamlit custom component.

## Eye-Tracking Integration

The project includes a vendor-neutral gaze-data adapter.

Supported input schema:

```text
timestamp_ms
x_norm
y_norm
confidence (optional)
source (optional)
```

This allows normalized gaze exports from systems such as:

- WebGazer
- Tobii
- Pupil Labs
- other eye-tracking systems

The application validates gaze samples and creates a fixation-density grid.

Automatic webcam capture is intentionally not enabled by default.

## Advanced Statistics

The analytics layer includes:

- descriptive statistics
- Cohen's d
- Welch's t-test
- one-way ANOVA
- bootstrap 95% confidence intervals
- repeated-measures participant summaries
- correlation matrices

These are exploratory analyses and should not be treated as clinical validation.

## Testing

Run:

```bash
pytest -q
```

Lint:

```bash
ruff check .
```

## GitHub Actions

Every push to `main` runs:

1. dependency installation
2. Ruff linting
3. pytest
4. Python compilation validation

Workflow:

```text
.github/workflows/ci.yml
```


## CI/CD

Two GitHub Actions workflows are included.

### Continuous Integration

`.github/workflows/ci.yml` runs on pushes and pull requests:

- Ruff linting
- pytest
- Python compilation validation

### Container Delivery

`.github/workflows/docker-publish.yml` builds and publishes two container images
to GitHub Container Registry whenever `main` is updated:

- `human-performance-app`
- `human-performance-api`

It also publishes version-tagged images when you push Git tags such as `v1.0.0`.

This gives the repository a repeatable deployment artifact instead of relying on
a developer's local environment.

## Project Structure

```text
.
├── app.py
├── auth.py
├── config.py
├── eye_tracking.py
├── models.py
├── repository.py
├── research_api.py
├── stats_utils.py
├── task_engine.py
├── config/
│   └── default_study.yaml
├── telemetry/
│   └── browser_telemetry.html
├── sample_data/
│   └── gaze_sample.csv
├── tests/
│   ├── test_config.py
│   ├── test_eye_tracking.py
│   └── test_stats.py
├── .github/workflows/
│   ├── ci.yml
│   └── docker-publish.yml
├── Dockerfile
├── Dockerfile.api
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── .env.example
└── README.md
```

## Deployment Notes

### Streamlit Community Cloud

The Streamlit UI can run on Community Cloud, but PostgreSQL should be hosted
externally if you want persistent multi-user data.

Configure:

```text
DATABASE_URL
RESEARCHER_USERNAME
RESEARCHER_PASSWORD
API_BASE_URL
```

as deployment secrets/environment variables.

### Production database

Use a managed PostgreSQL service rather than the SQLite fallback for persistent
multi-user research data.

## Privacy

The project uses anonymous participant IDs and does not require names or email
addresses.

Browser and gaze telemetry should only be collected with explicit participant
consent and an appropriate approved research protocol when used beyond a
student/demo context.

## Disclaimer

This is a student research and usability prototype.

It is not:

- a medical device
- a validated cognitive assessment
- a clinical decision-support tool
- a validated medical training platform
- an IRB-approved clinical study
