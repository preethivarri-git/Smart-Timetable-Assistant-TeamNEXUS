import io
from contextlib import redirect_stdout

import streamlit as st

from backend.agent.scheduler_agent import confirm_conflict_schedule


SUGGESTIONS = [
    "Schedule a Class",
    "Move a Class",
    "Find Free Time Tomorrow",
    "Create Study Schedule",
]


def render_agent(schedule):
    user_id = st.session_state.user_id

    st.markdown(
        """
        <div class='agent-shell'>
            <div class='agent-head'>
                <div class='agent-orb'>🤖</div>
                <div>
                    <b>AI Scheduling Assistant</b>
                    <div class='muted' style='font-size:.8rem'>
                        Ask anything about your timetable.
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "What would you like to plan today?"}
        ]

    if "pending_conflict" not in st.session_state:
        st.session_state.pending_conflict = None

    if "last_conflict" not in st.session_state:
        st.session_state.last_conflict = None

    if "last_conflict_outcome" not in st.session_state:
        st.session_state.last_conflict_outcome = None

    chat_box = st.container(height=280)

    with chat_box:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        if st.session_state.pending_conflict:
            conflict = st.session_state.pending_conflict

            with st.chat_message("assistant"):
                conflicting_events = ", ".join(conflict["conflicting_events"])
                st.warning(f"⚠ Conflict with: {conflicting_events}")

                suggested = conflict["suggested_start"].strftime(
                    "%A %d %b, %I:%M %p"
                )
                st.write(f"Suggested time instead: **{suggested}**")

                yes_col, no_col = st.columns(2)

                if yes_col.button(
                    "Yes, use suggested time",
                    key="conflict_yes",
                    use_container_width=True,
                ):
                    response = confirm_conflict_schedule(
                        conflict["summary"],
                        conflict["suggested_start"],
                        conflict["suggested_end"],
                        user_id,
                    )

                    st.session_state.chat_messages.append(
                        {"role": "assistant", "content": response}
                    )
                    st.session_state.last_conflict_outcome = "accepted"
                    st.session_state.pending_conflict = None
                    st.rerun()

                if no_col.button(
                    "No, cancel",
                    key="conflict_no",
                    use_container_width=True,
                ):
                    st.session_state.chat_messages.append(
                        {"role": "assistant", "content": "Event cancelled."}
                    )
                    st.session_state.last_conflict_outcome = "cancelled"
                    st.session_state.pending_conflict = None
                    st.rerun()

    # Do not allow a new message until the user chooses Yes or No.
    if st.session_state.pending_conflict:
        st.info(
            "Please choose Yes or No for the scheduling conflict before "
            "sending another message."
        )
        return

    def _fill_draft(text):
        st.session_state.chat_draft = text

    suggestion_columns = st.columns(4)

    for index, suggestion in enumerate(SUGGESTIONS):
        with suggestion_columns[index]:
            st.button(
                suggestion,
                key=f"suggestion_{index}",
                use_container_width=True,
                on_click=_fill_draft,
                args=(suggestion,),
            )

    with st.form("chat_form", clear_on_submit=True):
        input_col, send_col = st.columns([5, 1])

        with input_col:
            draft = st.text_input(
                "Ask anything...",
                key="chat_draft",
                label_visibility="collapsed",
                placeholder="Ask anything...",
            )

        with send_col:
            submitted = st.form_submit_button(
                "Send",
                use_container_width=True,
            )

    if submitted and draft.strip():
        st.session_state.pending_submit = draft.strip()

    prompt = st.session_state.pop("pending_submit", None)

    if not prompt:
        return

    st.session_state.chat_messages.append(
        {"role": "user", "content": prompt}
    )

    message = prompt.lower().strip()
    conflict = st.session_state.last_conflict
    outcome = st.session_state.last_conflict_outcome
    response = None

    # Answer questions using the real saved conflict details.
    if message in {
        "what was the conflict",
        "what was the conflict?",
        "what conflict",
        "what conflict?",
        "explain the conflict",
    }:
        if conflict and conflict.get("requested_start"):
            conflicting_events = ", ".join(conflict["conflicting_events"])
            requested_time = conflict["requested_start"].strftime(
                "%A %d %b, %I:%M %p"
            )
            suggested_time = conflict["suggested_start"].strftime(
                "%A %d %b, %I:%M %p"
            )

            response = (
                f"Your requested time, {requested_time}, conflicted with "
                f"{conflicting_events}. The suggested time was {suggested_time}."
            )

            if outcome == "accepted":
                response += " You approved that suggested time, so the event was scheduled."

            elif outcome == "cancelled":
                response += " You declined that suggested time, so the event was not created."

        else:
            response = "There is no recent scheduling conflict for me to explain."

    elif (
        "didn't approve" in message
        or "did not approve" in message
        or "didnt approve" in message
    ):
        if outcome == "cancelled":
            response = (
                "Correct. You did not approve the suggested time, "
                "so that event was not created."
            )

        elif outcome == "accepted":
            response = (
                "The suggested time was approved earlier, "
                "so the event was created."
            )

        else:
            response = "There is no approval decision waiting right now."

    if response:
        with chat_box:
            with st.chat_message("user"):
                st.write(prompt)

            with st.chat_message("assistant"):
                st.write(response)

        st.session_state.chat_messages.append(
            {"role": "assistant", "content": response}
        )
        return

    # All other messages go to the scheduler.
    with chat_box:
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.status(
                "Thinking through your schedule...",
                expanded=False,
            ):
                output = io.StringIO()

                try:
                    with redirect_stdout(output):
                        result = schedule(prompt, user_id)

                except Exception as error:
                    result = f"I couldn't complete that request: {error}"

            if isinstance(result, dict) and result.get("status") == "conflict":
                st.session_state.pending_conflict = result
                st.session_state.last_conflict = result
                st.session_state.last_conflict_outcome = None
                st.rerun()

            else:
                response = (
                    result
                    or output.getvalue().strip()
                    or "Done. Your request has been processed."
                )

                st.write_stream(f"{word} " for word in response.split())

                st.session_state.chat_messages.append(
                    {"role": "assistant", "content": response}
                )