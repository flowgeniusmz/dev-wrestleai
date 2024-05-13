import streamlit as st
from openai import OpenAI
import time

st.set_page_config(layout="wide")
client = OpenAI(api_key=st.secrets.openai.api_key)
thread_id = st.secrets.openai.thread_id
assistant_id = st.secrets.openai.assistant_id
initial_thread_messages = client.beta.threads.messages.list(thread_id=thread_id, order="asc")



st.title("WrestleAI Assistant")
st.divider()
st.header("Yazdani v Brooks")
st.divider()
tab1, tab2 = st.tabs(tabs=["Existing Chat", "New Chat"])
with tab1:
    chat_container = st.container(height=400, border=True)
    with chat_container:
        for msg in initial_thread_messages:
            with st.chat_message(name=msg.role):
                st.markdown(msg.content[0].text.value)

    if prompt := st.chat_input("Enter your question here...", key="adfad"):
        new_message = client.beta.threads.messages.create(role="user", thread_id=thread_id, content=prompt)
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
        run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)
        while run.status != "completed":
            time.sleep(2)
            run = client.beta.threads.runs.retrieve(run_id=run.id, thread_id=thread_id)
            if run.status == "completed":
                thread_messages = client.beta.threads.messages.list(thread_id=thread_id, run_id=run.id)
                for msg in thread_messages:
                    if msg.role == "assistant":
                        with chat_container:
                            with st.chat_message(name="assistant"):
                                st.markdown(msg.content[0].text.value)

with tab2:
    chatcontainer2 = st.container(height=400, border=True)
    with chatcontainer2:
        with st.chat_message("assistant"):
            st.markdown("I am WrestleAI - how can I help you today?")
    if prompt2 := st.chat_input("Enter your question here...", key="dafd"):
        thread2 = client.beta.threads.create()
        thread2_id = thread2.id
        message2 = client.beta.threads.messages.create(role="user", content=prompt2, thread_id=thread2_id)
        with chatcontainer2:
            with st.chat_message("user"):
                st.markdown(prompt2)
        run = client.beta.threads.runs.create(thread_id=thread2_id, assistant_id=assistant_id)
        while run.status != "completed":
            time.sleep(2)
            run = client.beta.threads.runs.retrieve(thread_id=thread2_id, run_id=run.id)
            if run.status == "completed":
                tmessages = client.beta.threads.messages.list(thread_id=thread2_id, run_id=run.id)
                for tms in tmessages:
                    if tms.role =="assistant":
                        with chatcontainer2:
                            with st.chat_message("assistant"):
                                st.markdown(tms.content[0].text.value)

