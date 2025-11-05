"""
Streamlit command center for Lewis's First Project.

Provides a unified UI to trigger orchestrator tasks and monitor progress.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

import requests
import streamlit as st

st.set_page_config(page_title="Lewis AI Command Center", layout="wide")

st.title("Lewis AI Command Center")
st.caption("Interact with the autonomous three-layer AI system.")

if "task_history" not in st.session_state:
    st.session_state.task_history = []

if "active_task" not in st.session_state:
    st.session_state.active_task = None


def api_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"} if token else {}


def create_task(api_url: str, token: str, goal: str, name: str, sync: bool) -> Dict[str, Any]:
    response = requests.post(
        f"{api_url}/tasks",
        json={"goal": goal, "name": name or None, "sync": sync},
        headers=api_headers(token),
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def fetch_status(api_url: str, token: str, task_id: str) -> Dict[str, Any]:
    response = requests.get(f"{api_url}/tasks/{task_id}", headers=api_headers(token), timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_events(api_url: str, token: str, task_id: str) -> List[Dict[str, Any]]:
    response = requests.get(
        f"{api_url}/tasks/{task_id}/events",
        headers=api_headers(token),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


with st.sidebar:
    st.header("Backend Configuration")
    api_base = st.text_input("FastAPI Base URL", value="http://localhost:8000")
    api_token = st.text_input("API Token", value="", type="password")
    sync_mode = st.checkbox("Synchronous execution", value=True)
    poll_interval = st.slider("Status refresh (seconds)", 1, 10, 2)

st.subheader("Launch a Task")
with st.form("task_form"):
    task_name = st.text_input("Task name", value="")
    goal = st.text_area("Describe the objective", height=150)
    submitted = st.form_submit_button("Start Orchestration")

if submitted:
    if not goal.strip():
        st.error("Please provide a goal for the orchestrator.")
    else:
        with st.spinner("Submitting task to orchestrator..."):
            try:
                result = create_task(api_base, api_token, goal.strip(), task_name.strip(), sync_mode)
                task_id = result["task_id"]
                st.session_state.active_task = task_id
                st.session_state.task_history.append(task_id)
                st.success(f"Task {task_id} submitted.")
            except requests.HTTPError as exc:
                st.error(f"API error: {exc.response.text}")
            except Exception as exc:  # pragma: no cover - UI safety
                st.error(f"Failed to submit task: {exc}")

active_task = st.session_state.active_task

if active_task:
    st.subheader(f"Active Task: {active_task}")
    status_placeholder = st.empty()

    status_data = None
    try:
        status_data = fetch_status(api_base, api_token, active_task)
    except requests.HTTPError as exc:
        st.error(f"Failed to fetch status: {exc.response.text}")
    except Exception as exc:  # pragma: no cover
        st.error(f"Status retrieval error: {exc}")

    if status_data:
        status_placeholder.markdown(
            f"**Status:** {status_data['status']}  |  Started: {status_data['started_at']}  |  Finished: {status_data['finished_at']}"
        )
        if status_data.get("result_summary"):
            with st.expander("Result Summary", expanded=True):
                st.json(status_data["result_summary"])
        if status_data.get("error_message"):
            st.error(status_data["error_message"])

    try:
        events = fetch_events(api_base, api_token, active_task)
        with st.expander("Event Log", expanded=True):
            for event in events:
                st.write(f"[{event['created_at']}] **{event['event_type']}**")
                st.json(event.get("payload", {}))
    except Exception as exc:  # pragma: no cover
        st.error(f"Could not load events: {exc}")

    if status_data and status_data["status"] not in {"completed", "failed", "cancelled"}:
        st.info("Task is still running. This page will refresh automatically.")
        time.sleep(poll_interval)
        st.experimental_rerun()

if st.session_state.task_history:
    st.subheader("Previous Tasks")
    cols = st.columns(len(st.session_state.task_history))
    for idx, task_id in enumerate(reversed(st.session_state.task_history[-5:])):
        with cols[idx % len(cols)]:
            if st.button(task_id, key=f"history_{task_id}"):
                st.session_state.active_task = task_id
                st.experimental_rerun()

