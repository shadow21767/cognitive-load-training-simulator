import random
import sqlite3
import time
import uuid
from datetime import datetime

import pandas as pd
import streamlit as st

DB_PATH = "cognitive_load.db"

st.set_page_config(
    page_title="Cognitive Load Training Simulator",
    page_icon="🧠",
    layout="wide",
)

# ---------------------------
# Database
# ---------------------------

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            participant TEXT NOT NULL,
            difficulty INTEGER NOT NULL,
            task_number INTEGER NOT NULL,
            prompt TEXT NOT NULL,
            expected_answer TEXT NOT NULL,
            selected_answer TEXT NOT NULL,
            correct INTEGER NOT NULL,
            response_time REAL NOT NULL,
            cognitive_load INTEGER,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_response(record):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        INSERT INTO sessions (
            session_id, participant, difficulty, task_number,
            prompt, expected_answer, selected_answer,
            correct, response_time, cognitive_load, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record["session_id"],
            record["participant"],
            record["difficulty"],
            record["task_number"],
            record["prompt"],
            record["expected_answer"],
            record["selected_answer"],
            record["correct"],
            record["response_time"],
            record["cognitive_load"],
            record["created_at"],
        ),
    )
    conn.commit()
    conn.close()


def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM sessions ORDER BY created_at DESC", conn)
    conn.close()
    return df


init_db()

# ---------------------------
# Experiment tasks
# ---------------------------

MEDICATIONS = [
    ("Amoxicillin", "500 mg", "Oral", "Every 8 hours"),
    ("Metformin", "500 mg", "Oral", "Twice daily"),
    ("Lisinopril", "10 mg", "Oral", "Once daily"),
    ("Acetaminophen", "325 mg", "Oral", "Every 6 hours"),
    ("Atorvastatin", "20 mg", "Oral", "Once daily"),
]


def make_task(difficulty):
    medication, dose, route, frequency = random.choice(MEDICATIONS)

    correct = f"{medication} — {dose} — {route} — {frequency}"

    distractor_pool = []
    for m, d, r, f in MEDICATIONS:
        distractor_pool.extend(
            [
                f"{m} — {d} — {r} — {f}",
                f"{m} — {dose} — {r} — {f}",
                f"{medication} — {d} — {route} — {f}",
            ]
        )

    distractor_pool = [x for x in distractor_pool if x != correct]
    random.shuffle(distractor_pool)

    option_count = min(3 + difficulty, 6)
    options = [correct] + distractor_pool[: option_count - 1]
    random.shuffle(options)

    prompt = (
        f"Select the label matching: **{medication}**, "
        f"**{dose}**, **{route}**, **{frequency}**."
    )

    return {
        "prompt": prompt,
        "correct": correct,
        "options": options,
    }


def score_session(results):
    if not results:
        return 0
    accuracy = sum(r["correct"] for r in results) / len(results)
    avg_rt = sum(r["response_time"] for r in results) / len(results)
    speed_score = max(0, min(1, 1 - ((avg_rt - 1.5) / 8)))
    return round((accuracy * 0.75 + speed_score * 0.25) * 100, 1)


def reset_session():
    keys = [
        "running",
        "participant",
        "difficulty",
        "task_index",
        "task",
        "task_started",
        "session_id",
        "results",
        "finished",
    ]
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]


# ---------------------------
# UI
# ---------------------------

st.title("🧠 Cognitive Load Training Simulator")
st.caption(
    "A human-factors research prototype for measuring accuracy, response time, "
    "and perceived cognitive load under increasing task difficulty."
)

page = st.sidebar.radio("Navigation", ["Experiment", "Analytics", "About"])

if page == "Experiment":
    if "running" not in st.session_state:
        st.session_state.running = False
    if "finished" not in st.session_state:
        st.session_state.finished = False

    if not st.session_state.running and not st.session_state.finished:
        st.subheader("Start a training session")

        col1, col2 = st.columns(2)
        with col1:
            participant = st.text_input("Participant ID", value="Participant-001")
        with col2:
            difficulty = st.slider(
                "Difficulty level",
                min_value=1,
                max_value=5,
                value=2,
                help="Higher levels display more similar answer choices.",
            )

        st.info(
            "This prototype is for simulation/usability research only. "
            "It is not medical advice and does not validate clinical competence."
        )

        if st.button("Start Experiment", type="primary"):
            st.session_state.running = True
            st.session_state.finished = False
            st.session_state.participant = participant.strip() or "Anonymous"
            st.session_state.difficulty = difficulty
            st.session_state.task_index = 0
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.results = []
            st.session_state.task = make_task(difficulty)
            st.session_state.task_started = time.time()
            st.rerun()

    elif st.session_state.running:
        total_tasks = 5
        current = st.session_state.task_index + 1

        st.progress(current / total_tasks)
        st.write(
            f"**Participant:** {st.session_state.participant} · "
            f"**Difficulty:** {st.session_state.difficulty} · "
            f"**Task:** {current}/{total_tasks}"
        )

        if st.session_state.difficulty >= 3:
            st.warning("Distraction: Complete the task quickly while ignoring this message.")

        if st.session_state.difficulty >= 4:
            st.caption(
                f"Secondary memory cue: remember the number "
                f"**{(st.session_state.task_index * 7 + 13) % 100}**."
            )

        task = st.session_state.task
        st.markdown("### Task")
        st.markdown(task["prompt"])

        selected = st.radio(
            "Choose the matching label",
            task["options"],
            index=None,
            key=f"answer_{st.session_state.task_index}",
        )

        cognitive_load = st.slider(
            "How mentally demanding did this task feel?",
            min_value=1,
            max_value=10,
            value=5,
            key=f"load_{st.session_state.task_index}",
        )

        if st.button("Submit Response", type="primary", disabled=selected is None):
            elapsed = round(time.time() - st.session_state.task_started, 3)
            correct = int(selected == task["correct"])

            record = {
                "session_id": st.session_state.session_id,
                "participant": st.session_state.participant,
                "difficulty": st.session_state.difficulty,
                "task_number": current,
                "prompt": task["prompt"],
                "expected_answer": task["correct"],
                "selected_answer": selected,
                "correct": correct,
                "response_time": elapsed,
                "cognitive_load": cognitive_load,
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }

            save_response(record)
            st.session_state.results.append(record)

            if current >= total_tasks:
                st.session_state.running = False
                st.session_state.finished = True
            else:
                st.session_state.task_index += 1
                st.session_state.task = make_task(st.session_state.difficulty)
                st.session_state.task_started = time.time()

            st.rerun()

    else:
        results = st.session_state.results
        accuracy = 100 * sum(r["correct"] for r in results) / len(results)
        avg_rt = sum(r["response_time"] for r in results) / len(results)
        avg_load = sum(r["cognitive_load"] for r in results) / len(results)
        overall_score = score_session(results)

        st.success("Session complete.")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Accuracy", f"{accuracy:.0f}%")
        c2.metric("Avg. Response Time", f"{avg_rt:.2f}s")
        c3.metric("Avg. Cognitive Load", f"{avg_load:.1f}/10")
        c4.metric("Performance Score", f"{overall_score}/100")

        session_df = pd.DataFrame(results)[
            ["task_number", "correct", "response_time", "cognitive_load"]
        ]
        session_df["correct"] = session_df["correct"].map({1: "Yes", 0: "No"})
        st.dataframe(session_df, use_container_width=True, hide_index=True)

        if st.button("Run Another Session"):
            reset_session()
            st.rerun()

elif page == "Analytics":
    st.subheader("Research Analytics Dashboard")
    df = load_data()

    if df.empty:
        st.info("No experiment data yet. Complete a session first.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Responses", len(df))
        col2.metric("Accuracy", f"{df['correct'].mean() * 100:.1f}%")
        col3.metric("Avg. Response Time", f"{df['response_time'].mean():.2f}s")
        col4.metric("Avg. Cognitive Load", f"{df['cognitive_load'].mean():.1f}/10")

        st.markdown("### Performance by difficulty")
        by_difficulty = (
            df.groupby("difficulty")
            .agg(
                accuracy=("correct", "mean"),
                avg_response_time=("response_time", "mean"),
                avg_cognitive_load=("cognitive_load", "mean"),
                responses=("id", "count"),
            )
            .reset_index()
        )
        by_difficulty["accuracy"] = by_difficulty["accuracy"] * 100

        st.dataframe(
            by_difficulty.rename(
                columns={
                    "difficulty": "Difficulty",
                    "accuracy": "Accuracy (%)",
                    "avg_response_time": "Avg Response Time (s)",
                    "avg_cognitive_load": "Avg Cognitive Load",
                    "responses": "Responses",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("#### Accuracy vs. difficulty")
            st.line_chart(
                by_difficulty.set_index("difficulty")["accuracy"],
                y_label="Accuracy (%)",
                x_label="Difficulty",
            )

        with chart_col2:
            st.markdown("#### Response time vs. difficulty")
            st.line_chart(
                by_difficulty.set_index("difficulty")["avg_response_time"],
                y_label="Seconds",
                x_label="Difficulty",
            )

        st.markdown("### Recent experiment responses")
        display_cols = [
            "participant",
            "difficulty",
            "task_number",
            "correct",
            "response_time",
            "cognitive_load",
            "created_at",
        ]
        st.dataframe(
            df[display_cols].head(50),
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download experiment data as CSV",
            data=df.to_csv(index=False),
            file_name="cognitive_load_experiment_data.csv",
            mime="text/csv",
        )

elif page == "About":
    st.subheader("Research Concept")
    st.markdown(
        """
This prototype studies how increasing interface complexity and distraction may
affect human performance during a simulated label-matching task.

**Independent variable**
- Difficulty level

**Measured variables**
- Accuracy
- Response time
- Perceived cognitive load
- Error frequency

**Potential research question**

> How does increasing task difficulty affect user accuracy, response time,
> and perceived cognitive load during a simulated healthcare training task?

The application is intentionally non-clinical and should be treated as a
human-factors / usability research prototype rather than a medical training
or decision-support system.
"""
    )
