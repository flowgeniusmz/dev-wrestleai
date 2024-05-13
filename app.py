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
chat_container = st.container(height=400, border=True)
with chat_container:
    for msg in initial_thread_messages:
        with st.chat_message(name=msg.role):
            st.markdown(msg.content[0].text.value)

if prompt := st.chat_input("Enter your question here..."):
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

