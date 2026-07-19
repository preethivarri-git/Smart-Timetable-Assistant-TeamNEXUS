import io
from contextlib import redirect_stdout

import streamlit as st


SUGGESTIONS = ["Schedule a meeting tomorrow", "Find free time this week", "Move my DBMS class", "Add assignment deadline"]


def render_agent(schedule):
    st.markdown("<div class='agent-shell'><div class='agent-head'><div class='agent-orb'>AI</div><div><b>Scheduler Agent</b><div class='muted' style='font-size:.8rem'>Context-aware planning assistant</div></div></div></div>", unsafe_allow_html=True)
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [{"role": "assistant", "content": "What would you like to plan today?"}]
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    suggestion_columns = st.columns(2)
    for index, suggestion in enumerate(SUGGESTIONS):
        with suggestion_columns[index % 2]:
            if st.button(suggestion, key=f"suggestion_{index}", use_container_width=True):
                st.session_state.pending_prompt = suggestion
    prompt = st.chat_input("Ask Smart Scheduler anything...") or st.session_state.pop("pending_prompt", None)
    if not prompt:
        return
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        with st.status("Thinking through your schedule...", expanded=False):
            output = io.StringIO()
            try:
                with redirect_stdout(output):
                    result = schedule(prompt)
                response = result or output.getvalue().strip() or "Done. Your request has been processed."
            except Exception as error:
                response = f"I couldn't complete that request: {error}"
        st.write_stream(f"{word} " for word in response.split())
    st.session_state.chat_messages.append({"role": "assistant", "content": response})
