import random
import time
import uuid

import pandas as pd
import streamlit as st

from db import init_db, execute, query_df, now_iso
from stats_utils import cohen_d, welch_t, repeated_measures_summary

TOTAL_TASKS = 8

st.set_page_config(
    page_title="Human Performance Simulation Lab",
    page_icon="🧠",
    layout="wide",
)

init_db()

CONDITIONS = {
    "Control": {
        "distraction_probability": 0.10,
        "memory_load": False,
        "stroop_probability": 0.15,
        "switch_probability": 0.10,
    },
    "Moderate Load": {
        "distraction_probability": 0.40,
        "memory_load": True,
        "stroop_probability": 0.35,
        "switch_probability": 0.30,
    },
    "High Load": {
        "distraction_probability": 0.75,
        "memory_load": True,
        "stroop_probability": 0.55,
        "switch_probability": 0.55,
    },
}

MEDICATIONS = [
    ("Amoxicillin", "500 mg", "Oral", "Every 8 hours"),
    ("Metformin", "500 mg", "Oral", "Twice daily"),
    ("Lisinopril", "10 mg", "Oral", "Once daily"),
    ("Acetaminophen", "325 mg", "Oral", "Every 6 hours"),
    ("Atorvastatin", "20 mg", "Oral", "Once daily"),
]

COLORS = ["RED", "BLUE", "GREEN", "YELLOW"]


def participant_id():
    return "P-" + uuid.uuid4().hex[:8].upper()


def log_event(event_type, target, page, value=None, task_number=None, elapsed_ms=None):
    if "exp_session_id" not in st.session_state:
        return
    execute("""
        INSERT INTO interaction_events (
            session_id, participant_id, event_type, target, page,
            task_number, value, elapsed_ms, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        st.session_state.exp_session_id,
        st.session_state.get("exp_participant_id", "unknown"),
        event_type,
        target,
        page,
        task_number,
        str(value) if value is not None else None,
        elapsed_ms,
        now_iso(),
    ))


def make_medication_task(difficulty):
    medication, dose, route, frequency = random.choice(MEDICATIONS)
    correct = f"{medication} — {dose} — {route} — {frequency}"

    distractors = []
    for m, d, r, f in MEDICATIONS:
        distractors.extend([
            f"{m} — {d} — {r} — {f}",
            f"{m} — {dose} — {r} — {f}",
            f"{medication} — {d} — {route} — {f}",
        ])

    distractors = [x for x in distractors if x != correct]
    random.shuffle(distractors)
    option_count = min(3 + difficulty, 6)
    options = [correct] + distractors[: option_count - 1]
    random.shuffle(options)

    return {
        "task_type": "Medication Match",
        "prompt": (
            f"Select the label matching **{medication}**, **{dose}**, "
            f"**{route}**, **{frequency}**."
        ),
        "correct": correct,
        "options": options,
    }


def make_stroop_task():
    word = random.choice(COLORS)
    ink = random.choice([c for c in COLORS if c != word])
    return {
        "task_type": "Stroop Interference",
        "prompt": (
            f"The word shown is **{word}**. Ignore the word itself and select "
            f"the simulated ink color: **{ink}**."
        ),
        "correct": ink,
        "options": COLORS.copy(),
    }


def make_memory_task(memory_number):
    options = [str(memory_number)]
    while len(options) < 4:
        candidate = str(random.randint(10, 99))
        if candidate not in options:
            options.append(candidate)
    random.shuffle(options)

    return {
        "task_type": "Working Memory",
        "prompt": "Select the number you were asked to remember earlier.",
        "correct": str(memory_number),
        "options": options,
    }


def make_keyboard_task():
    letter = random.choice(["A", "S", "D", "F"])
    return {
        "task_type": "Keyboard Response",
        "prompt": (
            f"Keyboard-only trial: type **{letter}** into the response field "
            f"and press Enter."
        ),
        "correct": letter,
        "options": [],
    }


def create_task(condition, difficulty, task_number, memory_number):
    cfg = CONDITIONS[condition]
    switch_trial = random.random() < cfg["switch_probability"]
    distraction = random.random() < cfg["distraction_probability"]

    if task_number == 3 and cfg["memory_load"]:
        task = make_memory_task(memory_number)
    elif task_number == 6:
        task = make_keyboard_task()
    elif random.random() < cfg["stroop_probability"] or switch_trial:
        task = make_stroop_task()
    else:
        task = make_medication_task(difficulty)

    task["switch_trial"] = int(switch_trial)
    task["distraction_present"] = int(distraction)
    return task


def save_trial(record):
    execute("""
        INSERT INTO sessions (
            session_id, participant_id, condition_name, difficulty,
            task_number, task_type, prompt, expected_answer,
            selected_answer, correct, response_time, cognitive_load,
            distraction_present, switch_trial, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record["session_id"],
        record["participant_id"],
        record["condition_name"],
        record["difficulty"],
        record["task_number"],
        record["task_type"],
        record["prompt"],
        record["expected_answer"],
        record["selected_answer"],
        record["correct"],
        record["response_time"],
        record["cognitive_load"],
        record["distraction_present"],
        record["switch_trial"],
        record["created_at"],
    ))


def reset_study():
    for key in list(st.session_state.keys()):
        if key.startswith("exp_") or key.startswith("answer_") or key.startswith("load_"):
            del st.session_state[key]


st.sidebar.title("🧠 Research Platform")
page = st.sidebar.radio(
    "Navigation",
    [
        "Study Setup",
        "Experiment",
        "Analytics",
        "Interaction Telemetry",
        "Accessibility Audit",
        "Research Methods",
        "Admin View",
        "About",
    ],
)

st.title("Human Performance Simulation Lab")
st.caption(
    "Human-factors research platform for studying cognitive load, interaction behavior, "
    "task switching, attention, working memory, and usability."
)

if page == "Study Setup":
    st.subheader("Create an Anonymous Research Session")
    with st.form("study_setup"):
        consent = st.checkbox(
            "I understand this is a student research prototype and agree to participate."
        )
        difficulty = st.slider("Base task difficulty", 1, 5, 2)
        study_mode = st.selectbox(
            "Study mode",
            ["Randomized condition", "Repeated-measures pilot"],
        )
        notes = st.text_input("Optional notes")
        submitted = st.form_submit_button("Create Session")

    if submitted:
        if not consent:
            st.error("Consent is required.")
        else:
            pid = participant_id()
            condition = random.choice(list(CONDITIONS.keys()))
            execute("""
                INSERT OR IGNORE INTO participants
                (participant_id, created_at, consented, notes)
                VALUES (?, ?, ?, ?)
            """, (pid, now_iso(), 1, notes))

            st.session_state.exp_participant_id = pid
            st.session_state.exp_condition = condition
            st.session_state.exp_difficulty = difficulty
            st.session_state.exp_session_id = str(uuid.uuid4())
            st.session_state.exp_study_mode = study_mode
            st.session_state.exp_memory_number = random.randint(10, 99)
            st.session_state.exp_task_index = 0
            st.session_state.exp_results = []
            st.session_state.exp_running = False
            st.session_state.exp_finished = False

            log_event("session", "create_session", "Study Setup", condition)
            st.success("Study session created.")
            st.code(
                f"Participant: {pid}\n"
                f"Condition: {condition}\n"
                f"Mode: {study_mode}"
            )

elif page == "Experiment":
    required = ["exp_participant_id", "exp_condition", "exp_session_id"]
    if not all(k in st.session_state for k in required):
        st.warning("Create a study session first.")
    else:
        if not st.session_state.get("exp_running", False) and not st.session_state.get("exp_finished", False):
            st.write(
                f"**Participant:** `{st.session_state.exp_participant_id}` · "
                f"**Condition:** `{st.session_state.exp_condition}`"
            )
            if CONDITIONS[st.session_state.exp_condition]["memory_load"]:
                st.info(
                    f"Remember this number during the experiment: "
                    f"**{st.session_state.exp_memory_number}**"
                )
            if st.button("Begin Experiment", type="primary"):
                log_event("click", "begin_experiment", "Experiment")
                st.session_state.exp_running = True
                st.session_state.exp_task_index = 0
                st.session_state.exp_task = create_task(
                    st.session_state.exp_condition,
                    st.session_state.exp_difficulty,
                    1,
                    st.session_state.exp_memory_number,
                )
                st.session_state.exp_task_started = time.time()
                st.rerun()

        elif st.session_state.get("exp_running", False):
            current = st.session_state.exp_task_index + 1
            task = st.session_state.exp_task

            st.progress(current / TOTAL_TASKS)
            st.write(f"### Trial {current}/{TOTAL_TASKS}")
            st.caption(f"Task type: {task['task_type']}")

            if task["switch_trial"]:
                st.warning("TASK SWITCH: the response rule has changed.")
            if task["distraction_present"]:
                st.error(
                    "⚠ Simulated alert: Equipment notification. Ignore it and finish the current task."
                )

            st.markdown(task["prompt"])

            if task["task_type"] == "Keyboard Response":
                selected = st.text_input(
                    "Keyboard response",
                    key=f"answer_{current}",
                    max_chars=1,
                    placeholder="Type the requested key",
                ).upper().strip()
            else:
                selected = st.radio(
                    "Response",
                    task["options"],
                    index=None,
                    key=f"answer_{current}",
                )

            load = st.slider(
                "Mental demand",
                1,
                10,
                5,
                key=f"load_{current}",
            )

            if st.button(
                "Submit Trial",
                type="primary",
                disabled=(not selected),
            ):
                elapsed = time.time() - st.session_state.exp_task_started
                elapsed_ms = elapsed * 1000

                log_event(
                    "response",
                    task["task_type"],
                    "Experiment",
                    value=selected,
                    task_number=current,
                    elapsed_ms=elapsed_ms,
                )
                log_event(
                    "click",
                    "submit_trial",
                    "Experiment",
                    task_number=current,
                    elapsed_ms=elapsed_ms,
                )

                record = {
                    "session_id": st.session_state.exp_session_id,
                    "participant_id": st.session_state.exp_participant_id,
                    "condition_name": st.session_state.exp_condition,
                    "difficulty": st.session_state.exp_difficulty,
                    "task_number": current,
                    "task_type": task["task_type"],
                    "prompt": task["prompt"],
                    "expected_answer": task["correct"],
                    "selected_answer": selected,
                    "correct": int(selected == task["correct"]),
                    "response_time": round(elapsed, 3),
                    "cognitive_load": load,
                    "distraction_present": task["distraction_present"],
                    "switch_trial": task["switch_trial"],
                    "created_at": now_iso(),
                }
                save_trial(record)
                st.session_state.exp_results.append(record)

                if current >= TOTAL_TASKS:
                    st.session_state.exp_running = False
                    st.session_state.exp_finished = True
                    log_event("session", "complete_experiment", "Experiment")
                else:
                    st.session_state.exp_task_index += 1
                    next_number = st.session_state.exp_task_index + 1
                    st.session_state.exp_task = create_task(
                        st.session_state.exp_condition,
                        st.session_state.exp_difficulty,
                        next_number,
                        st.session_state.exp_memory_number,
                    )
                    st.session_state.exp_task_started = time.time()
                st.rerun()

        else:
            results = pd.DataFrame(st.session_state.exp_results)
            st.success("Experiment complete.")
            if not results.empty:
                c1, c2, c3 = st.columns(3)
                c1.metric("Accuracy", f"{results['correct'].mean() * 100:.1f}%")
                c2.metric("Avg Response Time", f"{results['response_time'].mean():.2f}s")
                c3.metric("Avg Cognitive Load", f"{results['cognitive_load'].mean():.1f}/10")

                st.dataframe(
                    results[[
                        "task_number",
                        "task_type",
                        "correct",
                        "response_time",
                        "cognitive_load",
                        "distraction_present",
                        "switch_trial",
                    ]],
                    use_container_width=True,
                    hide_index=True,
                )

            if st.button("New Study Session"):
                reset_study()
                st.rerun()

elif page == "Analytics":
    df = query_df("SELECT * FROM sessions ORDER BY created_at DESC")
    st.subheader("Research Analytics")

    if df.empty:
        st.info("No study data yet.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Trials", len(df))
        c2.metric("Participants", df["participant_id"].nunique())
        c3.metric("Accuracy", f"{df['correct'].mean() * 100:.1f}%")
        c4.metric("Avg Response", f"{df['response_time'].mean():.2f}s")

        summary = (
            df.groupby("condition_name")
            .agg(
                trials=("id", "count"),
                accuracy=("correct", "mean"),
                avg_response_time=("response_time", "mean"),
                avg_load=("cognitive_load", "mean"),
            )
            .reset_index()
        )
        summary["accuracy"] *= 100

        st.markdown("### Condition comparison")
        st.dataframe(summary, use_container_width=True, hide_index=True)

        st.markdown("### Accuracy by condition")
        st.bar_chart(summary.set_index("condition_name")["accuracy"])

        st.markdown("### Response time by condition")
        st.bar_chart(summary.set_index("condition_name")["avg_response_time"])

        distracted = df.loc[df["distraction_present"] == 1, "response_time"]
        clean = df.loc[df["distraction_present"] == 0, "response_time"]

        d = cohen_d(distracted, clean)
        t = welch_t(distracted, clean)

        col1, col2 = st.columns(2)
        col1.metric(
            "Distraction effect size",
            "N/A" if d is None else f"Cohen's d = {d:.2f}",
        )
        col2.metric(
            "Welch t statistic",
            "N/A" if t is None else f"t = {t:.2f}",
        )

        st.markdown("### Repeated-measures summary")
        rm = repeated_measures_summary(df)
        st.dataframe(rm, use_container_width=True, hide_index=True)

        st.download_button(
            "Download research CSV",
            df.to_csv(index=False),
            "research_trials.csv",
            "text/csv",
        )

elif page == "Interaction Telemetry":
    st.subheader("Interaction Telemetry & Click-Frequency Heatmap")
    events = query_df("""
        SELECT *
        FROM interaction_events
        ORDER BY created_at DESC
    """)

    if events.empty:
        st.info("Complete an experiment to generate telemetry.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Interaction Events", len(events))
        c2.metric("Sessions", events["session_id"].nunique())
        c3.metric("Participants", events["participant_id"].nunique())

        heatmap = (
            events.groupby(["page", "target"])
            .size()
            .reset_index(name="interaction_count")
            .sort_values("interaction_count", ascending=False)
        )

        st.markdown("### UI interaction heatmap")
        st.caption(
            "This is an element-level click-frequency heatmap: it shows which interface "
            "targets receive the most interactions without storing raw screen coordinates."
        )
        st.dataframe(heatmap, use_container_width=True, hide_index=True)

        top_targets = heatmap.head(12).set_index("target")["interaction_count"]
        st.bar_chart(top_targets)

        st.markdown("### Session replay")
        session_ids = events["session_id"].dropna().unique().tolist()
        selected_session = st.selectbox("Session", session_ids)

        replay = events[events["session_id"] == selected_session].copy()
        replay = replay.sort_values(["created_at", "id"])
        st.dataframe(
            replay[[
                "created_at",
                "event_type",
                "page",
                "target",
                "task_number",
                "value",
                "elapsed_ms",
            ]],
            use_container_width=True,
            hide_index=True,
        )

elif page == "Accessibility Audit":
    st.subheader("Accessibility & Usability Audit")
    st.write(
        "Use this lightweight audit after a session to record whether the research "
        "interface supports core accessibility and usability goals."
    )

    with st.form("accessibility"):
        keyboard_navigation = st.checkbox("Core tasks can be completed with keyboard input")
        readable_labels = st.checkbox("Controls have clear, readable labels")
        clear_feedback = st.checkbox("Success/error feedback is easy to understand")
        low_distraction = st.checkbox("The interface avoids unnecessary visual clutter")
        adequate_time = st.checkbox("Users have enough time to understand and respond")
        notes = st.text_area("Audit notes")
        submitted = st.form_submit_button("Save Audit")

    if submitted:
        checks = [
            keyboard_navigation,
            readable_labels,
            clear_feedback,
            low_distraction,
            adequate_time,
        ]
        score = sum(checks) / len(checks) * 100
        pid = st.session_state.get("exp_participant_id", "AUDIT-ONLY")
        sid = st.session_state.get("exp_session_id")

        execute("""
            INSERT INTO accessibility_audits (
                participant_id, session_id, keyboard_navigation,
                readable_labels, clear_feedback, low_distraction,
                adequate_time, notes, score, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pid,
            sid,
            int(keyboard_navigation),
            int(readable_labels),
            int(clear_feedback),
            int(low_distraction),
            int(adequate_time),
            notes,
            score,
            now_iso(),
        ))

        st.metric("Accessibility Audit Score", f"{score:.0f}%")

    audits = query_df("""
        SELECT *
        FROM accessibility_audits
        ORDER BY created_at DESC
    """)
    if not audits.empty:
        st.markdown("### Audit history")
        st.dataframe(audits, use_container_width=True, hide_index=True)

elif page == "Research Methods":
    st.subheader("Research Methods")
    st.markdown("""
### Research question

How do distraction, task switching, working-memory demands, interference,
and interface interaction patterns affect accuracy, response time, and
perceived cognitive load?

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

### Phase 4 telemetry
The application records high-level interaction events such as session start,
trial submission, response type, page, and UI target. It intentionally avoids
collecting raw mouse coordinates or personally identifying information.

### Analysis
- Descriptive statistics
- Condition comparisons
- Cohen's d
- Welch t statistic
- Participant-level repeated-measures summaries

### Limitation
This is a student research prototype and not a validated cognitive or clinical
assessment.
""")

elif page == "Admin View":
    st.subheader("Research Administrator View")

    participants = query_df("""
        SELECT *
        FROM participants
        ORDER BY created_at DESC
    """)
    sessions = query_df("""
        SELECT *
        FROM sessions
        ORDER BY created_at DESC
    """)
    events = query_df("""
        SELECT *
        FROM interaction_events
        ORDER BY created_at DESC
    """)

    c1, c2, c3 = st.columns(3)
    c1.metric("Participants", len(participants))
    c2.metric("Trials", len(sessions))
    c3.metric("Events", len(events))

    st.markdown("### Participants")
    st.dataframe(participants, use_container_width=True, hide_index=True)

    st.markdown("### Recent trials")
    st.dataframe(sessions.head(50), use_container_width=True, hide_index=True)

    st.markdown("### Recent events")
    st.dataframe(events.head(100), use_container_width=True, hide_index=True)

elif page == "About":
    st.subheader("Project Status")
    st.markdown("""
### Phase 1 — MVP ✅
- Timed tasks
- Accuracy and response-time logging
- Cognitive-load ratings
- SQLite persistence
- Analytics

### Phase 2 — Human Factors ✅
- Stroop interference
- Working memory
- Distraction trials
- Task switching

### Phase 3 — Research Layer ✅
- Consent
- Anonymous IDs
- Randomized conditions
- Research methods
- Effect-size analysis
- CSV export

### Phase 4 — Web Research Platform ✅
- Interaction-event telemetry
- Element-level click-frequency heatmap
- Session replay
- Keyboard-only task
- Accessibility audit
- Research admin dashboard
- Repeated-measures summaries
- Optional FastAPI backend

### Future upgrades
- Real multi-device deployment
- Authentication for researcher/admin roles
- PostgreSQL
- Browser-native event capture
- Eye-tracking integration
- IRB-ready study configuration
""")
