import random
import sqlite3
import time
import uuid
from datetime import datetime

import pandas as pd
import streamlit as st

DB_PATH = "cognitive_load.db"
TOTAL_TASKS = 8

st.set_page_config(page_title="Human Performance Simulation Lab", page_icon="🧠", layout="wide")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS participants (
            participant_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            consented INTEGER NOT NULL,
            notes TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            participant_id TEXT NOT NULL,
            condition_name TEXT NOT NULL,
            difficulty INTEGER NOT NULL,
            task_number INTEGER NOT NULL,
            task_type TEXT NOT NULL,
            prompt TEXT NOT NULL,
            expected_answer TEXT NOT NULL,
            selected_answer TEXT NOT NULL,
            correct INTEGER NOT NULL,
            response_time REAL NOT NULL,
            cognitive_load INTEGER NOT NULL,
            distraction_present INTEGER NOT NULL,
            switch_trial INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit(); conn.close()


def save_participant(participant_id, notes=""):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT OR IGNORE INTO participants VALUES (?, ?, ?, ?)",
                 (participant_id, datetime.now().isoformat(timespec="seconds"), 1, notes))
    conn.commit(); conn.close()


def save_response(r):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO sessions (
            session_id, participant_id, condition_name, difficulty, task_number,
            task_type, prompt, expected_answer, selected_answer, correct,
            response_time, cognitive_load, distraction_present, switch_trial, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tuple(r[k] for k in [
        "session_id","participant_id","condition_name","difficulty","task_number",
        "task_type","prompt","expected_answer","selected_answer","correct",
        "response_time","cognitive_load","distraction_present","switch_trial","created_at"
    ]))
    conn.commit(); conn.close()


def load_sessions():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM sessions ORDER BY created_at DESC", conn)
    conn.close(); return df


init_db()

CONDITIONS = {
    "Control": {"distraction_probability": 0.10, "memory_load": False, "stroop_probability": 0.15, "switch_probability": 0.10},
    "Moderate Load": {"distraction_probability": 0.40, "memory_load": True, "stroop_probability": 0.35, "switch_probability": 0.30},
    "High Load": {"distraction_probability": 0.75, "memory_load": True, "stroop_probability": 0.55, "switch_probability": 0.55},
}

MEDICATIONS = [
    ("Amoxicillin", "500 mg", "Oral", "Every 8 hours"),
    ("Metformin", "500 mg", "Oral", "Twice daily"),
    ("Lisinopril", "10 mg", "Oral", "Once daily"),
    ("Acetaminophen", "325 mg", "Oral", "Every 6 hours"),
    ("Atorvastatin", "20 mg", "Oral", "Once daily"),
]
COLORS = ["RED", "BLUE", "GREEN", "YELLOW"]


def anonymized_participant_id():
    return "P-" + uuid.uuid4().hex[:8].upper()


def make_medication_task(difficulty):
    medication, dose, route, frequency = random.choice(MEDICATIONS)
    correct = f"{medication} — {dose} — {route} — {frequency}"
    distractors = []
    for m, d, r, f in MEDICATIONS:
        distractors.extend([f"{m} — {d} — {r} — {f}", f"{m} — {dose} — {r} — {f}", f"{medication} — {d} — {route} — {f}"])
    distractors = [x for x in distractors if x != correct]
    random.shuffle(distractors)
    options = [correct] + distractors[: min(2 + difficulty, 5)]
    random.shuffle(options)
    return {"task_type":"Medication Match", "prompt":f"Select the label matching **{medication}**, **{dose}**, **{route}**, **{frequency}**.", "correct":correct, "options":options}


def make_stroop_task():
    word = random.choice(COLORS)
    simulated_ink = random.choice([c for c in COLORS if c != word])
    return {"task_type":"Stroop Interference", "prompt":f"The displayed word is **{word}**. Ignore the word and select the simulated ink color: **{simulated_ink}**.", "correct":simulated_ink, "options":COLORS.copy()}


def make_memory_task(memory_number):
    choices = [str(memory_number)]
    while len(choices) < 4:
        candidate = str(random.randint(10,99))
        if candidate not in choices: choices.append(candidate)
    random.shuffle(choices)
    return {"task_type":"Working Memory", "prompt":"Select the number you were asked to remember earlier.", "correct":str(memory_number), "options":choices}


def create_task(condition_name, difficulty, task_number, memory_number):
    cfg = CONDITIONS[condition_name]
    switch = random.random() < cfg["switch_probability"]
    if task_number == 3 and cfg["memory_load"]:
        task = make_memory_task(memory_number)
    elif switch or random.random() < cfg["stroop_probability"]:
        task = make_stroop_task()
    else:
        task = make_medication_task(difficulty)
    task["distraction_present"] = int(random.random() < cfg["distraction_probability"])
    task["switch_trial"] = int(switch)
    return task


def cohen_d(a, b):
    a, b = pd.Series(a).dropna(), pd.Series(b).dropna()
    if len(a) < 2 or len(b) < 2: return None
    pooled_den = len(a) + len(b) - 2
    pooled_num = ((len(a)-1)*a.var(ddof=1)) + ((len(b)-1)*b.var(ddof=1))
    if pooled_den <= 0: return None
    pooled_sd = (pooled_num / pooled_den) ** 0.5
    return 0.0 if pooled_sd == 0 else (a.mean() - b.mean()) / pooled_sd


def reset_session():
    for key in list(st.session_state.keys()):
        if key.startswith("exp_") or key.startswith("answer_") or key.startswith("load_"):
            del st.session_state[key]


st.sidebar.title("🧠 Research Lab")
page = st.sidebar.radio("Navigation", ["Study Setup", "Experiment", "Analytics", "Research Methods", "About"])

st.title("Human Performance Simulation Lab")
st.caption("Human-factors research prototype for studying cognitive load, task switching, attention, working memory, and usability.")

if page == "Study Setup":
    st.subheader("Phase 3 — Research Setup")
    st.write("The study uses anonymous IDs and randomized conditions. No name or email is required.")
    with st.form("consent_form"):
        st.markdown("### Participant consent")
        st.write("I understand this is a student research prototype, not a clinical assessment or validated medical training system.")
        consent = st.checkbox("I agree to participate in this simulated study.")
        difficulty = st.slider("Base task difficulty", 1, 5, 2)
        notes = st.text_input("Optional study notes", placeholder="Example: pilot test")
        submitted = st.form_submit_button("Create Anonymous Study Session")
    if submitted:
        if not consent:
            st.error("Consent must be acknowledged before creating a study session.")
        else:
            pid = anonymized_participant_id(); condition = random.choice(list(CONDITIONS))
            save_participant(pid, notes)
            st.session_state.exp_participant_id = pid
            st.session_state.exp_condition = condition
            st.session_state.exp_difficulty = difficulty
            st.session_state.exp_session_id = str(uuid.uuid4())
            st.session_state.exp_task_index = 0
            st.session_state.exp_results = []
            st.session_state.exp_memory_number = random.randint(10,99)
            st.session_state.exp_running = False
            st.session_state.exp_finished = False
            st.success("Anonymous study session created.")
            st.code(f"Participant ID: {pid}\nAssigned condition: {condition}\nDifficulty: {difficulty}")
            st.info("Open the Experiment tab to begin.")

elif page == "Experiment":
    needed = ["exp_participant_id","exp_condition","exp_difficulty","exp_session_id"]
    if not all(k in st.session_state for k in needed):
        st.warning("Create a study session in Study Setup first.")
    else:
        st.write(f"**Participant:** `{st.session_state.exp_participant_id}` · **Condition:** `{st.session_state.exp_condition}` · **Difficulty:** `{st.session_state.exp_difficulty}`")
        if not st.session_state.get("exp_running", False) and not st.session_state.get("exp_finished", False):
            if CONDITIONS[st.session_state.exp_condition]["memory_load"]:
                st.info(f"Remember **{st.session_state.exp_memory_number}** during the experiment.")
            if st.button("Begin Experiment", type="primary"):
                st.session_state.exp_running = True
                st.session_state.exp_task_index = 0
                st.session_state.exp_task = create_task(st.session_state.exp_condition, st.session_state.exp_difficulty, 1, st.session_state.exp_memory_number)
                st.session_state.exp_task_started = time.time(); st.rerun()
        elif st.session_state.get("exp_running", False):
            current = st.session_state.exp_task_index + 1; task = st.session_state.exp_task
            st.progress(current / TOTAL_TASKS); st.write(f"### Trial {current} of {TOTAL_TASKS}"); st.caption(f"Task type: {task['task_type']}")
            if task["switch_trial"]: st.warning("TASK SWITCH: the task rule has changed.")
            if task["distraction_present"]: st.error("⚠ Simulated notification: Equipment alert — acknowledge later. Continue the current task.")
            st.markdown(task["prompt"])
            selected = st.radio("Response", task["options"], index=None, key=f"answer_{current}")
            load = st.slider("Mental demand for this trial", 1, 10, 5, key=f"load_{current}")
            if st.button("Submit Trial", type="primary", disabled=selected is None):
                r = {
                    "session_id":st.session_state.exp_session_id,
                    "participant_id":st.session_state.exp_participant_id,
                    "condition_name":st.session_state.exp_condition,
                    "difficulty":st.session_state.exp_difficulty,
                    "task_number":current,
                    "task_type":task["task_type"],
                    "prompt":task["prompt"],
                    "expected_answer":task["correct"],
                    "selected_answer":selected,
                    "correct":int(selected == task["correct"]),
                    "response_time":round(time.time()-st.session_state.exp_task_started,3),
                    "cognitive_load":load,
                    "distraction_present":task["distraction_present"],
                    "switch_trial":task["switch_trial"],
                    "created_at":datetime.now().isoformat(timespec="seconds")
                }
                save_response(r); st.session_state.exp_results.append(r)
                if current >= TOTAL_TASKS:
                    st.session_state.exp_running = False; st.session_state.exp_finished = True
                else:
                    st.session_state.exp_task_index += 1
                    st.session_state.exp_task = create_task(st.session_state.exp_condition, st.session_state.exp_difficulty, current+1, st.session_state.exp_memory_number)
                    st.session_state.exp_task_started = time.time()
                st.rerun()
        else:
            results = pd.DataFrame(st.session_state.exp_results)
            if not results.empty:
                c1,c2,c3,c4 = st.columns(4)
                c1.metric("Accuracy", f"{results['correct'].mean()*100:.1f}%")
                c2.metric("Avg. Response Time", f"{results['response_time'].mean():.2f}s")
                c3.metric("Avg. Cognitive Load", f"{results['cognitive_load'].mean():.1f}/10")
                switch_trials = results[results["switch_trial"]==1]
                switch_error = 0 if switch_trials.empty else (1-switch_trials["correct"].mean())*100
                c4.metric("Switch Error Rate", f"{switch_error:.1f}%")
                st.dataframe(results[["task_number","task_type","correct","response_time","cognitive_load","distraction_present","switch_trial"]], use_container_width=True, hide_index=True)
            if st.button("Create New Study Session"):
                reset_session(); st.rerun()

elif page == "Analytics":
    st.subheader("Phase 3 — Research Analytics")
    df = load_sessions()
    if df.empty:
        st.info("Complete at least one experiment session first.")
    else:
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Recorded Trials", len(df)); c2.metric("Overall Accuracy", f"{df['correct'].mean()*100:.1f}%")
        c3.metric("Mean Response Time", f"{df['response_time'].mean():.2f}s"); c4.metric("Mean Cognitive Load", f"{df['cognitive_load'].mean():.1f}/10")
        summary = df.groupby("condition_name").agg(Trials=("id","count"), Accuracy=("correct","mean"), Avg_Response_Time=("response_time","mean"), Avg_Cognitive_Load=("cognitive_load","mean")).reset_index()
        summary["Accuracy"] *= 100
        st.markdown("### Experimental conditions"); st.dataframe(summary, use_container_width=True, hide_index=True)
        st.markdown("### Accuracy by condition"); st.bar_chart(summary.set_index("condition_name")["Accuracy"])
        st.markdown("### Response time by condition"); st.bar_chart(summary.set_index("condition_name")["Avg_Response_Time"])
        task_summary = df.groupby("task_type").agg(Trials=("id","count"), Accuracy=("correct","mean"), Avg_Response_Time=("response_time","mean"), Avg_Load=("cognitive_load","mean")).reset_index(); task_summary["Accuracy"]*=100
        st.markdown("### Task-type analysis"); st.dataframe(task_summary, use_container_width=True, hide_index=True)
        if set(df["distraction_present"].unique()) >= {0,1}:
            d_rt = cohen_d(df.loc[df.distraction_present==1,"response_time"], df.loc[df.distraction_present==0,"response_time"])
            d_load = cohen_d(df.loc[df.distraction_present==1,"cognitive_load"], df.loc[df.distraction_present==0,"cognitive_load"])
            a,b = st.columns(2)
            a.metric("Distraction RT effect", "N/A" if d_rt is None else f"Cohen's d = {d_rt:.2f}")
            b.metric("Distraction load effect", "N/A" if d_load is None else f"Cohen's d = {d_load:.2f}")
            st.caption("Rule of thumb: |d| ≈ 0.2 small, 0.5 medium, 0.8 large. Interpret cautiously for small pilot samples.")
        st.download_button("Download anonymized CSV", df.to_csv(index=False), "human_performance_study.csv", "text/csv")

elif page == "Research Methods":
    st.subheader("Research Design")
    st.markdown("""
### Research question
**How do distraction, task switching, working-memory demands, and interference affect accuracy, response time, and perceived cognitive load during simulated healthcare-training tasks?**

### Independent variables
- Experimental condition: Control, Moderate Load, High Load
- Distraction present vs. absent
- Task-switch trial vs. standard trial
- Task type
- Base difficulty

### Dependent variables
- Accuracy
- Response time
- Perceived cognitive load
- Error rate
- Switch-related performance cost

### Randomization
Each new anonymous participant is randomly assigned to one of three conditions. Trial types and distraction events are randomized within that condition.

### Suggested pilot
1. Recruit 8–15 volunteers for a classroom/usability pilot.
2. Have each participant complete one session.
3. Export the anonymized CSV.
4. Compare accuracy and response time across conditions.
5. Examine whether distraction trials increase response time or cognitive load.
6. Report descriptive results and effect sizes without making clinical claims.

**Limitation:** This is a student research prototype, not an IRB-approved clinical study, validated cognitive assessment, or medical device.
""")

elif page == "About":
    st.subheader("Project Scope")
    st.markdown("""
### Phase 1 — MVP ✅
Timed tasks, difficulty levels, performance logging, SQLite, dashboard.

### Phase 2 — Human Factors ✅
Stroop-style interference, working-memory task, distraction events, task switching, human-factors telemetry.

### Phase 3 — Research Layer ✅
Consent, anonymous IDs, randomized conditions, research methods, condition comparisons, effect sizes, CSV export.

### Phase 4 — Optional Web Expansion
Mouse-path telemetry, click heatmaps, accessibility testing, keyboard-only tasks, FastAPI multi-user collection, or external eye-tracking integration.
""")
