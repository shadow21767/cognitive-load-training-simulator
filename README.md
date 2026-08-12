# 🧠 Human Performance Simulation Lab

A web-based **human-factors research platform** for studying how cognitive load, distraction, task switching, working memory, interference, and interface interaction patterns affect human performance in simulated healthcare-training tasks.

> Built as a student research prototype inspired by healthcare simulation, usability research, cognitive science, and human-computer interaction.

---

## 🚀 Live Demo

**[Try the Human Performance Simulation Lab](https://cognitive-load-training-simulator.streamlit.app)**

No installation required.

> Replace `YOUR_STREAMLIT_APP_URL` with your deployed Streamlit Community Cloud URL.

### Recommended Demo Flow

1. Open **Study Setup**
2. Accept the research-prototype consent
3. Create an anonymous participant session
4. Open **Experiment**
5. Complete the 8 experimental trials
6. Review results in **Analytics**
7. Explore **Interaction Telemetry**
8. Review the **Session Replay**
9. Complete the **Accessibility Audit**
10. Explore the **Admin View**

---

## 🎯 Project Goal

The goal of this project is to explore how software can be used to study **human performance and usability** in simulation-based training environments.

The platform measures:

- Accuracy
- Response time
- Cognitive-load ratings
- Task-switching performance
- Distraction effects
- Working-memory performance
- Interaction frequency
- Accessibility and usability indicators

The project focuses on the intersection of:

**Software Engineering · Healthcare Simulation · Human Factors · Cognitive Science · HCI · Research Analytics**

---

## 🔬 Research Question

> **How do distraction, task switching, working-memory demands, interference, and interface interaction patterns affect accuracy, response time, and perceived cognitive load during simulated healthcare-training tasks?**

---

# ✨ Features

## Phase 1 — MVP ✅

The first version established the experimental foundation.

- Timed simulation tasks
- Adjustable difficulty levels
- Accuracy measurement
- Response-time tracking
- Cognitive-load self-rating
- SQLite data persistence
- Research analytics dashboard
- CSV data export

---

## Phase 2 — Human Factors ✅

The second phase introduced cognitive-science and human-factors concepts.

### Stroop-Style Interference

Participants must respond to conflicting information designed to simulate attention interference.

### Working Memory

Participants are asked to retain information while completing other tasks.

### Simulated Distractions

Trials may include notification-style alerts that participants must ignore while completing the primary task.

### Task Switching

Certain trials require users to adapt to a changed response rule.

### Human-Factors Telemetry

Each trial records:

- Task type
- Difficulty
- Correctness
- Response time
- Cognitive-load rating
- Distraction status
- Task-switch status

---

## Phase 3 — Research Layer ✅

Phase 3 transformed the application from a simple simulator into a structured research prototype.

### Anonymous Participant IDs

Participants receive randomly generated identifiers such as:

```text
P-A82F194C
```

No name or email address is required.

### Consent Workflow

Participants must acknowledge that the application is a student research prototype before beginning.

### Randomized Experimental Conditions

Participants are assigned to one of three conditions:

- **Control**
- **Moderate Load**
- **High Load**

Each condition changes the probability of:

- distractions
- task switching
- working-memory requirements
- interference tasks

### Research Analytics

The platform includes:

- descriptive statistics
- condition comparisons
- participant-level summaries
- Cohen's d effect-size calculations
- Welch t statistics
- CSV research-data export

---

## Phase 4 — Web Research Platform ✅

Phase 4 adds research-platform and usability-engineering capabilities.

### Interaction Telemetry

The platform records high-level interaction events including:

- experiment start
- trial submission
- task type
- interface target
- session ID
- participant ID
- response timing

### Interaction Heatmap

The application produces an **element-level click-frequency heatmap** showing which interface controls receive the most interaction.

Example:

```text
submit_trial         █████████████
begin_experiment     █████
Medication Match     ███████████
Stroop Interference  ███████
Keyboard Response    ████
```

The system intentionally avoids storing raw mouse coordinates.

### Session Replay

Researchers can reconstruct the interaction sequence for an experimental session.

Example:

```text
Session Created
      ↓
Experiment Started
      ↓
Medication Match Response
      ↓
Trial Submitted
      ↓
Stroop Response
      ↓
Task Switch
      ↓
Experiment Completed
```

### Keyboard Accessibility Task

One experimental trial requires keyboard-only interaction to evaluate alternate input methods.

### Accessibility Audit

The platform includes a lightweight usability and accessibility evaluation covering:

- keyboard navigation
- readable labels
- clear system feedback
- unnecessary visual clutter
- adequate response time

### Research Administrator View

Researchers can inspect:

- participants
- experimental trials
- interaction events
- accessibility audits

---

# 🏗️ Architecture

```text
                      Participant
                           │
                           ▼
                Streamlit Research UI
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
  Experiment Engine   Interaction       Accessibility
                     Telemetry             Audit
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                    SQLite Database
                           │
            ┌──────────────┼───────────────┐
            │              │               │
            ▼              ▼               ▼
        Analytics     Session Replay     Admin View
            │
            ▼
       CSV Data Export
            │
            ▼
      Optional FastAPI API
```

---

# 🧪 Experimental Tasks

The experiment currently includes several task types.

## Medication Matching

Participants identify the correct simulated medication label from increasingly similar choices.

Measured variables:

- accuracy
- response time
- difficulty
- cognitive load

---

## Stroop Interference

Participants respond to conflicting visual/verbal information.

Purpose:

- attention testing
- interference measurement
- cognitive-control analysis

---

## Working Memory

Participants retain a number while completing another task and later recall it.

Purpose:

- memory-load measurement
- divided-attention testing

---

## Task Switching

Participants receive a changed response rule during selected trials.

Purpose:

- cognitive flexibility
- switch-cost measurement
- error analysis

---

## Keyboard Response

Participants complete a task using keyboard input instead of mouse interaction.

Purpose:

- accessibility testing
- alternative interaction analysis

---

# 📊 Research Variables

## Independent Variables

- Experimental condition
- Difficulty level
- Distraction presence
- Task-switch status
- Task type

## Dependent Variables

- Accuracy
- Response time
- Cognitive-load rating
- Error frequency
- Interaction frequency
- Accessibility audit score

---

# 📈 Analytics

The research dashboard supports analysis of:

- overall accuracy
- average response time
- average cognitive load
- performance by condition
- performance by task type
- distraction effects
- task-switching effects
- participant-level summaries

The project also includes basic effect-size and group-comparison calculations.

---

# 🗄️ Data Model

The platform stores several types of research data.

## Participants

```text
participant_id
created_at
consented
notes
```

## Experimental Trials

```text
session_id
participant_id
condition_name
difficulty
task_number
task_type
expected_answer
selected_answer
correct
response_time
cognitive_load
distraction_present
switch_trial
created_at
```

## Interaction Events

```text
session_id
participant_id
event_type
target
page
task_number
value
elapsed_ms
created_at
```

## Accessibility Audits

```text
participant_id
session_id
keyboard_navigation
readable_labels
clear_feedback
low_distraction
adequate_time
score
created_at
```

---

# 💻 Tech Stack

### Application

- Python
- Streamlit

### Backend / API

- FastAPI
- Pydantic

### Data

- SQLite
- Pandas

### Research Analytics

- Descriptive statistics
- Cohen's d
- Welch t statistic
- Repeated-measures summaries

---

# ▶️ Run Locally

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the Streamlit application:

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

---

# 🔌 Optional FastAPI Backend

The project also includes an optional research API.

Start it with:

```bash
uvicorn research_api:app --reload --port 8000
```

Then open the interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

Example API endpoints include:

```text
GET  /health
GET  /participants
GET  /sessions
GET  /events
POST /events
GET  /analytics/summary
```

---

# ☁️ Public Deployment

The Streamlit application can be deployed using **Streamlit Community Cloud**.

Typical deployment configuration:

```text
Repository:
shadow21767/cognitive-load-training-simulator

Branch:
main

Main file:
app.py
```

After deployment, replace the placeholder in the **Live Demo** section with your public application URL.

---

# 📁 Project Structure

```text
human-performance-simulation-lab/
│
├── app.py
├── db.py
├── stats_utils.py
├── research_api.py
├── requirements.txt
├── README.md
├── PROJECT_PLAN.md
└── .gitignore
```

---

# 🛣️ Development Roadmap

## Completed

- [x] Phase 1 — MVP
- [x] Phase 2 — Human Factors
- [x] Phase 3 — Research Layer
- [x] Phase 4 — Web Research Platform

## Future Engineering Improvements

- [ ] PostgreSQL backend
- [ ] Docker containerization
- [ ] Automated unit tests
- [ ] GitHub Actions CI/CD
- [ ] Researcher authentication
- [ ] Configurable experiments
- [ ] Multi-user deployments
- [ ] Browser-native interaction telemetry
- [ ] Eye-tracking integration
- [ ] Advanced statistical analysis

---

# 💼 Portfolio Summary

**Human Performance Simulation Lab — Python, Streamlit, FastAPI, SQLite**

Developed a human-factors research platform for studying cognitive load, attention, working memory, task switching, and interaction behavior under randomized experimental conditions. Implemented trial-level telemetry, session replay, UI interaction heatmaps, keyboard-accessibility testing, anonymized participant tracking, repeated-measures analysis, effect-size calculations, research dashboards, and an optional FastAPI backend.

---

# ⚠️ Research Disclaimer

This application is a **student research and usability prototype**.

It is **not**:

- a medical device
- a clinical decision-support system
- a validated cognitive assessment
- a validated medical training platform
- an IRB-approved clinical study

The software should not be used to make clinical or diagnostic decisions.

---

## 📌 Project Motivation

This project explores how emerging software technologies can support research in:

- healthcare simulation
- human factors
- cognitive science
- usability engineering
- human-computer interaction
- training-system design

The long-term goal is to better understand how interface design and cognitive workload can influence human performance during simulation-based training.
