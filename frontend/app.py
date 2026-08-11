"""Simple Streamlit client for the Think9 Brain API."""

import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Think9 Brain")
st.title("Think9 Brain")

question = st.text_area("Question", placeholder="Ask a question about the available evidence.")
if st.button("Verify", type="primary"):
    if not question.strip():
        st.warning("Enter a question first.")
    else:
        try:
            response = requests.post(f"{API_URL}/verify", json={"question": question}, timeout=130)
            response.raise_for_status()
            result = response.json()
            st.subheader("Answer")
            st.write(result["answer"])
            st.write(f"Confidence: {result['confidence']}")
            st.write(f"Categories: {', '.join(result['categories'])}")
            st.write(f"Sources: {', '.join(result['sources']) or 'None'}")
            st.write(f"Status: {result['status']}")
            if result["status"] == "pending_review":
                st.warning("Human review required.")
        except requests.RequestException:
            st.error("Think9 Brain is unavailable. Start the backend and try again.")

st.divider()
st.header("Review Queue")
try:
    response = requests.get(f"{API_URL}/review", timeout=10)
    response.raise_for_status()
    pending = response.json()["decisions"]
    if not pending:
        st.caption("No decisions require review.")
    for decision in pending:
        with st.container(border=True):
            st.write(f"**#{decision['decision_id']}** — {decision['question']}")
            st.write(decision["answer"])
            approve, reject = st.columns(2)
            if approve.button("Approve", key=f"approve-{decision['decision_id']}"):
                requests.post(f"{API_URL}/review/{decision['decision_id']}/approve", timeout=30).raise_for_status()
                st.rerun()
            if reject.button("Reject", key=f"reject-{decision['decision_id']}"):
                requests.post(f"{API_URL}/review/{decision['decision_id']}/reject", timeout=30).raise_for_status()
                st.rerun()
except requests.RequestException:
    st.info("Start the backend to load the review queue.")
