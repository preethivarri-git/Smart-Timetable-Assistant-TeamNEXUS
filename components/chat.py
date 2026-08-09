import io
from contextlib import redirect_stdout

import streamlit as st

from backend.agent.scheduler_agent import confirm_conflict_schedule


SUGGESTIONS = ["Schedule a Class", "Move a Class", "Find Free Time Tomorrow", "Create Study Schedule"]


def render_agent(schedule):
    user_id = st.session_state.user_id
    st.markdown(
        """
        <div class='agent-shell'>
            <div class='agent-head'>
                <div class='agent-orb'>🤖</div>
                <div>
                    <b>AI Scheduling Assistant</b>
                    <div class='muted' style='font-size:.8rem'>Ask anything about your timetable.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [{"role": "assistant", "content": "What would you like to plan today?"}]
    if "pending_conflict" not in st.session_state:
        st.session_state.pending_conflict = None

    chat_box = st.container(height=280)
    with chat_box:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # If the last turn hit a scheduling conflict, show the confirmation UI here.
        if st.session_state.pending_conflict:
            conflict = st.session_state.pending_conflict
            with st.chat_message("assistant"):
                st.warning(f"⚠ Conflict with: {', '.join(conflict['conflicting_events'])}")
                suggested = conflict["suggested_start"].strftime("%A %d %b, %I:%M %p")
                st.write(f"Suggested time instead: **{suggested}**")
                yes_col, no_col = st.columns(2)
                if yes_col.button("Yes, use suggested time", key="conflict_yes", use_container_width=True):
                    response = confirm_conflict_schedule(
                        conflict["summary"], conflict["suggested_start"], conflict["suggested_end"], user_id
                    )
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    st.session_state.pending_conflict = None
                    st.rerun()
                if no_col.button("No, cancel", key="conflict_no", use_container_width=True):
                    st.session_state.chat_messages.append({"role": "assistant", "content": "Event cancelled."})
                    st.session_state.pending_conflict = None
                    st.rerun()

    def _fill_draft(text):
        st.session_state.chat_draft = text

    suggestion_columns = st.columns(4)
    for index, suggestion in enumerate(SUGGESTIONS):
        with suggestion_columns[index]:
            st.button(
                suggestion, key=f"suggestion_{index}", use_container_width=True,
                on_click=_fill_draft, args=(suggestion,),
            )

    def _submit_draft():
        draft = st.session_state.get("chat_draft", "").strip()
        if draft:
            st.session_state.pending_submit = draft
        st.session_state.chat_draft = ""

    input_col, send_col = st.columns([5, 1])
    with input_col:
        st.text_input(
            "Ask anything...", key="chat_draft", label_visibility="collapsed",
            placeholder="Ask anything...", on_change=_submit_draft,
        )
    with send_col:
        st.button("Send", use_container_width=True, on_click=_submit_draft)

    prompt = st.session_state.pop("pending_submit", None)
    if not prompt:
        return

    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with chat_box:
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.status("Thinking through your schedule...", expanded=False):
                output = io.StringIO()
                try:
                    with redirect_stdout(output):
                        result = schedule(prompt, user_id)
                except Exception as error:
                    result = f"I couldn't complete that request: {error}"

            if isinstance(result, dict) and result.get("status") == "conflict":
                st.session_state.pending_conflict = result
                st.rerun()
            else:
                response = result or output.getvalue().strip() or "Done. Your request has been processed."
                st.write_stream(f"{word} " for word in response.split())
                st.session_state.chat_messages.append({"role": "assistant", "content": response})