import random
import time
import uuid
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from auth import valid_credentials
from config import api_base_url, load_study_config
from eye_tracking import adapter_notes, fixation_summary, validate_gaze_dataframe
from models import init_db
from repository import (
    add_audit,
    add_event,
    add_gaze_samples,
    add_participant,
    add_trial,
    audits_df,
    events_df,
    gaze_df,
    participants_df,
    trials_df,
)
from stats_utils import (
    bootstrap_mean_ci,
    cohen_d,
    correlation_matrix,
    one_way_anova,
    repeated_measures_summary,
    welch_test,
)
from task_engine import create_task

st.set_page_config(page_title="Human Performance Simulation Lab", page_icon="🧠", layout="wide")
init_db()
CONFIG = load_study_config()
STUDY = CONFIG["study"]
CONDITIONS = CONFIG["conditions"]
TOTAL_TASKS = int(STUDY["total_tasks"])


def new_participant_id():
    return "P-" + uuid.uuid4().hex[:8].upper()


def log_event(event_type, target, page, value=None, task_number=None, elapsed_ms=None):
    sid = st.session_state.get("exp_session_id")
    pid = st.session_state.get("exp_participant_id")
    if not sid or not pid:
        return
    add_event(
        session_id=sid,
        participant_id=pid,
        event_type=event_type,
        target=target,
        page=page,
        task_number=task_number,
        value=str(value) if value is not None else None,
        elapsed_ms=elapsed_ms,
    )


def researcher_gate():
    if st.session_state.get("researcher_authenticated"):
        return True

    with st.form("researcher_login"):
        st.write("### Researcher Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in")

    if submitted:
        if valid_credentials(username, password):
            st.session_state.researcher_authenticated = True
            st.success("Authenticated.")
            st.rerun()
        else:
            st.error("Invalid credentials.")
    return False


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
        "Eye Tracking",
        "Accessibility Audit",
        "Admin View",
        "Study Configuration",
        "About",
    ],
)

st.title("Human Performance Simulation Lab")
st.caption(f"{STUDY['name']} · Study ID: {STUDY['id']} · Version {STUDY['version']}")

if page == "Study Setup":
    st.subheader("Anonymous Research Session")

    with st.form("study_setup"):
        consent = st.checkbox(
            "I understand this is a student research prototype and agree to participate."
        )
        difficulty = st.slider("Base task difficulty", 1, 5, 2)
        mode = st.selectbox("Study mode", ["Randomized condition", "Repeated-measures pilot"])
        notes = st.text_input("Optional notes")
        submitted = st.form_submit_button("Create Session")

    if submitted:
        if not consent:
            st.error("Consent is required.")
        else:
            pid = new_participant_id()
            condition = random.choice(list(CONDITIONS.keys()))
            sid = str(uuid.uuid4())

            add_participant(participant_id=pid, consented=True, notes=notes)

            st.session_state.exp_participant_id = pid
            st.session_state.exp_session_id = sid
            st.session_state.exp_condition = condition
            st.session_state.exp_difficulty = difficulty
            st.session_state.exp_mode = mode
            st.session_state.exp_memory_number = random.randint(10, 99)
            st.session_state.exp_task_index = 0
            st.session_state.exp_results = []
            st.session_state.exp_running = False
            st.session_state.exp_finished = False

            log_event("session", "create_session", "Study Setup", condition)
            st.success("Session created.")
            st.code(f"Participant: {pid}\nSession: {sid}\nCondition: {condition}")

elif page == "Experiment":
    required = ["exp_participant_id", "exp_session_id", "exp_condition"]
    if not all(k in st.session_state for k in required):
        st.warning("Create a study session first.")
    else:
        if not st.session_state.get("exp_running") and not st.session_state.get("exp_finished"):
            st.write(
                f"**Participant:** `{st.session_state.exp_participant_id}` · "
                f"**Condition:** `{st.session_state.exp_condition}`"
            )
            cfg = CONDITIONS[st.session_state.exp_condition]
            if cfg.get("memory_load"):
                st.info(f"Remember this number: **{st.session_state.exp_memory_number}**")

            if st.button("Begin Experiment", type="primary"):
                log_event("click", "begin_experiment", "Experiment")
                st.session_state.exp_running = True
                st.session_state.exp_task_index = 0
                st.session_state.exp_task = create_task(
                    cfg,
                    st.session_state.exp_difficulty,
                    1,
                    st.session_state.exp_memory_number,
                )
                st.session_state.exp_task_started = time.time()
                st.rerun()

        elif st.session_state.get("exp_running"):
            current = st.session_state.exp_task_index + 1
            task = st.session_state.exp_task
            st.progress(current / TOTAL_TASKS)
            st.write(f"### Trial {current}/{TOTAL_TASKS}")
            st.caption(task["task_type"])

            if task["switch_trial"]:
                st.warning("TASK SWITCH: the response rule has changed.")
            if task["distraction_present"]:
                st.error("⚠ Simulated equipment alert. Ignore it and finish the current task.")

            st.markdown(task["prompt"])

            if task["task_type"] == "Keyboard Response":
                selected = st.text_input("Keyboard response", key=f"answer_{current}", max_chars=1).upper().strip()
            else:
                selected = st.radio("Response", task["options"], index=None, key=f"answer_{current}")

            load = st.slider("Mental demand", 1, 10, 5, key=f"load_{current}")

            if st.button("Submit Trial", type="primary", disabled=not selected):
                elapsed = round(time.time() - st.session_state.exp_task_started, 3)
                correct = selected == task["correct"]

                add_trial(
                    session_id=st.session_state.exp_session_id,
                    participant_id=st.session_state.exp_participant_id,
                    study_id=STUDY["id"],
                    condition_name=st.session_state.exp_condition,
                    difficulty=st.session_state.exp_difficulty,
                    task_number=current,
                    task_type=task["task_type"],
                    prompt=task["prompt"],
                    expected_answer=task["correct"],
                    selected_answer=selected,
                    correct=correct,
                    response_time=elapsed,
                    cognitive_load=load,
                    distraction_present=task["distraction_present"],
                    switch_trial=task["switch_trial"],
                )

                log_event(
                    "response",
                    task["task_type"],
                    "Experiment",
                    value=selected,
                    task_number=current,
                    elapsed_ms=elapsed * 1000,
                )

                st.session_state.exp_results.append({
                    "task_number": current,
                    "task_type": task["task_type"],
                    "correct": correct,
                    "response_time": elapsed,
                    "cognitive_load": load,
                })

                if current >= TOTAL_TASKS:
                    st.session_state.exp_running = False
                    st.session_state.exp_finished = True
                    log_event("session", "complete_experiment", "Experiment")
                else:
                    st.session_state.exp_task_index += 1
                    next_num = st.session_state.exp_task_index + 1
                    st.session_state.exp_task = create_task(
                        CONDITIONS[st.session_state.exp_condition],
                        st.session_state.exp_difficulty,
                        next_num,
                        st.session_state.exp_memory_number,
                    )
                    st.session_state.exp_task_started = time.time()
                st.rerun()

        else:
            results = pd.DataFrame(st.session_state.exp_results)
            st.success("Experiment complete.")
            if not results.empty:
                a, b, c = st.columns(3)
                a.metric("Accuracy", f"{results['correct'].mean() * 100:.1f}%")
                b.metric("Avg Response Time", f"{results['response_time'].mean():.2f}s")
                c.metric("Avg Cognitive Load", f"{results['cognitive_load'].mean():.1f}/10")
                st.dataframe(results, use_container_width=True, hide_index=True)
            if st.button("New Study Session"):
                reset_study()
                st.rerun()

elif page == "Analytics":
    df = trials_df()
    st.subheader("Advanced Research Analytics")

    if df.empty:
        st.info("No study data yet.")
    else:
        df["correct"] = df["correct"].astype(float)
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
        st.dataframe(summary, use_container_width=True, hide_index=True)

        distracted = df.loc[df["distraction_present"] == True, "response_time"]
        clean = df.loc[df["distraction_present"] == False, "response_time"]
        d = cohen_d(distracted, clean)
        welch = welch_test(distracted, clean)
        anova = one_way_anova(df, "response_time", "condition_name")
        ci = bootstrap_mean_ci(df["response_time"])

        a, b, c, dcol = st.columns(4)
        a.metric("Cohen's d", "N/A" if d is None else f"{d:.2f}")
        b.metric("Welch p-value", "N/A" if welch is None else f"{welch['p']:.4f}")
        c.metric("ANOVA p-value", "N/A" if anova is None else f"{anova['p']:.4f}")
        dcol.metric("95% bootstrap CI", "N/A" if ci is None else f"{ci[0]:.2f}–{ci[1]:.2f}s")

        st.markdown("### Participant-level repeated measures")
        st.dataframe(repeated_measures_summary(df), use_container_width=True, hide_index=True)

        st.markdown("### Correlation matrix")
        corr = correlation_matrix(df)
        if not corr.empty:
            st.dataframe(corr.round(3), use_container_width=True)

        st.download_button(
            "Download trials CSV",
            df.to_csv(index=False),
            "research_trials.csv",
            "text/csv",
        )

elif page == "Interaction Telemetry":
    st.subheader("Browser-Native Interaction Telemetry")

    if "exp_session_id" in st.session_state:
        html_path = Path("telemetry/browser_telemetry.html")
        html = html_path.read_text(encoding="utf-8")
        api = api_base_url()
        sid = st.session_state.exp_session_id
        pid = st.session_state.exp_participant_id
        # The component is sandboxed; telemetry applies to the embedded component itself.
        iframe_html = html.replace(
            "<script>",
            f"<script>history.replaceState(null, '', '?api={quote(api)}&session={quote(sid)}&participant={quote(pid)}');"
        )
        components.html(iframe_html, height=80)
        st.caption(
            "The embedded component records page visibility, viewport changes, and sampled "
            "pointer activity. Full-page Streamlit DOM capture would require a custom component."
        )
    else:
        st.info("Create a study session to attach telemetry to a session.")

    events = events_df()
    if not events.empty:
        st.markdown("### Event frequency")
        heat = events.groupby(["page", "target"]).size().reset_index(name="count").sort_values("count", ascending=False)
        st.dataframe(heat, use_container_width=True, hide_index=True)
        st.bar_chart(heat.head(15).set_index("target")["count"])

        st.markdown("### Session replay")
        sid = st.selectbox("Session", sorted(events["session_id"].unique()))
        replay = events[events["session_id"] == sid].sort_values(["created_at", "id"])
        st.dataframe(replay, use_container_width=True, hide_index=True)

elif page == "Eye Tracking":
    st.subheader("Eye-Tracking Integration")
    st.write(adapter_notes())
    st.caption(
        "This version provides a vendor-neutral gaze-data ingestion and analysis layer. "
        "It does not activate a webcam or collect gaze data automatically."
    )

    uploaded = st.file_uploader("Upload gaze CSV", type=["csv"])
    if uploaded:
        gaze = pd.read_csv(uploaded)
        valid, message = validate_gaze_dataframe(gaze)
        if not valid:
            st.error(message)
        else:
            st.success("Gaze data validated.")
            st.dataframe(gaze.head(20), use_container_width=True)

            summary = fixation_summary(gaze)
            st.markdown("### Fixation-density grid")
            pivot = summary.pivot(index="y_bin", columns="x_bin", values="samples").fillna(0)
            st.dataframe(pivot, use_container_width=True)

            if "exp_session_id" in st.session_state and st.button("Store gaze samples"):
                samples = []
                for _, row in gaze.iterrows():
                    samples.append({
                        "session_id": st.session_state.exp_session_id,
                        "participant_id": st.session_state.exp_participant_id,
                        "timestamp_ms": float(row["timestamp_ms"]),
                        "x_norm": float(row["x_norm"]),
                        "y_norm": float(row["y_norm"]),
                        "confidence": float(row["confidence"]) if "confidence" in gaze.columns and pd.notna(row["confidence"]) else None,
                        "source": str(row["source"]) if "source" in gaze.columns else "uploaded",
                    })
                count = add_gaze_samples(samples)
                st.success(f"Stored {count} gaze samples.")

    stored = gaze_df()
    if not stored.empty:
        st.markdown("### Stored gaze-data summary")
        st.dataframe(
            stored.groupby(["session_id", "source"]).size().reset_index(name="samples"),
            use_container_width=True,
            hide_index=True,
        )

elif page == "Accessibility Audit":
    st.subheader("Accessibility & Usability Audit")
    with st.form("audit"):
        keyboard_navigation = st.checkbox("Core tasks support keyboard interaction")
        readable_labels = st.checkbox("Controls have readable labels")
        clear_feedback = st.checkbox("Feedback is clear")
        low_distraction = st.checkbox("Visual clutter is controlled")
        adequate_time = st.checkbox("Users have adequate response time")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Save Audit")

    if submitted:
        values = [keyboard_navigation, readable_labels, clear_feedback, low_distraction, adequate_time]
        score = sum(values) / len(values) * 100
        add_audit(
            participant_id=st.session_state.get("exp_participant_id", "AUDIT-ONLY"),
            session_id=st.session_state.get("exp_session_id"),
            keyboard_navigation=keyboard_navigation,
            readable_labels=readable_labels,
            clear_feedback=clear_feedback,
            low_distraction=low_distraction,
            adequate_time=adequate_time,
            notes=notes,
            score=score,
        )
        st.metric("Accessibility Score", f"{score:.0f}%")

    audits = audits_df()
    if not audits.empty:
        st.dataframe(audits, use_container_width=True, hide_index=True)

elif page == "Admin View":
    if researcher_gate():
        st.subheader("Research Administrator")
        participants = participants_df()
        trials = trials_df()
        events = events_df()
        audits = audits_df()

        a, b, c, d = st.columns(4)
        a.metric("Participants", len(participants))
        b.metric("Trials", len(trials))
        c.metric("Events", len(events))
        d.metric("Audits", len(audits))

        st.markdown("### Participants")
        st.dataframe(participants, use_container_width=True, hide_index=True)
        st.markdown("### Recent trials")
        st.dataframe(trials.tail(100), use_container_width=True, hide_index=True)
        st.markdown("### Recent events")
        st.dataframe(events.tail(100), use_container_width=True, hide_index=True)

        if st.button("Sign out researcher"):
            st.session_state.researcher_authenticated = False
            st.rerun()

elif page == "Study Configuration":
    if researcher_gate():
        st.subheader("Configurable Study Protocol")
        st.caption("The active protocol is loaded from `config/default_study.yaml`.")
        st.json(CONFIG)
        st.write(
            "Edit the YAML file to change condition probabilities, study metadata, "
            "or enabled task modules without rewriting the experiment engine."
        )

elif page == "About":
    st.subheader("Engineering Improvements")
    st.markdown("""
### Completed
- PostgreSQL-ready persistence through SQLAlchemy
- SQLite fallback for local development
- Docker and Docker Compose
- Automated tests
- GitHub Actions CI
- Researcher authentication
- YAML-configurable studies
- Multi-user-safe participant/session IDs
- Browser telemetry ingestion API
- Embedded browser-event capture
- Vendor-neutral eye-tracking data adapter
- Advanced statistics: effect sizes, Welch testing, ANOVA, bootstrap confidence intervals
- FastAPI research service

### Scope note
The eye-tracking layer accepts normalized gaze streams from tools such as
WebGazer, Tobii, or Pupil Labs. Automatic webcam-based gaze tracking is not
enabled by default because it requires explicit participant consent and
browser/device-specific integration.
""")
