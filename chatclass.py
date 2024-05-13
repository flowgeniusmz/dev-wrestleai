import streamlit as st
from openai import OpenAI
import pandas as pd
from tempfile import NamedTemporaryFile
import base64
import time
import json
from tavily import TavilyClient
import cv2


def tavily_search(query):
    search_results = TavilyClient(api_key=st.secrets.tavily.api_key).get_search_context(query=query, search_depth="advanced", max_tokens=8000)
    return search_results


class chat_assistant():
    def __init__(self):
        self.client = OpenAI(api_key=st.secrets.openai.api_key)
        self.get_assistant()
        self.get_thread()

    
    def get_assistant(self):
        self.assistant_id = st.secrets.openai.assistant_id
        self.assistant = self.client.beta.assistants.retrieve(assistant_id=self.assistant_id)
    
    def get_thread(self):
        self.thread_id = st.secrets.openai.thread_id
        self.thread = self.client.beta.threads.retrieve()
        self.thread_id = self.thread.id
        
    def create_message(self, prompt):
        self.user_message_content = prompt
        self.display_message(type="user")
        self.message = self.client.beta.threads.messages.create(thread_id=self.thread_id, role="user", content=self.formatted_prompt)
        self.message_id = self.message.id
        self.user_message_id = self.message_id
        
    def create_run(self, additional_instructions=None):
        self.run = self.client.beta.threads.runs.create(thread_id=self.thread_id, assistant_id=self.assistant_id, additional_instructions=additional_instructions)
        self.run_id = self.run.id
        self.run_status = self.run.status
        self.add_message_to_chat_history(type="user")

    def retrieve_run(self):
        self.run = self.client.beta.threads.runs.retrieve(run_id=self.run_id, thread_id=self.thread_id)
        self.run_status = self.run.status
        
    def wait_on_run(self):
        while self.run_status != "completed":
            time.sleep(3)
            self.retrieve_run()
            if self.run_status == "completed":
                self.get_thread_messages()
                self.get_response_messages()
                break
            elif self.run_status == "requires_action":
                self.tool_calls = self.run.required_action.submit_tool_outputs.tool_calls
                self.requires_action_type = self.run.required_action.type # should be submit_tool_outputs
                self.submit_tool_outputs()
                if self.tool_outputs:
                    self.retrieve_run()
                
    def submit_tool_outputs(self):
        self.tool_outputs = []
        for tool_call in self.tool_calls:
            toolname = tool_call.function.name
            toolargs = json.loads(tool_call.function.arguments)
            toolid = tool_call.id
            if toolname == "tavily_search":
                toolarg = toolargs['query']
                tooloutput = tavily_search(query=toolarg)
                toolcalloutput = {"tool_call_id": toolid, "output": tooloutput}
                self.tool_outputs.append(toolcalloutput)
    
    def get_thread_messages(self):
        self.thread_messages = self.client.beta.threads.messages.list(thread_id=self.thread_id)
    
    def get_response_messages(self):
        for thread_message in self.thread_messages:
            if thread_message.role == "assistant" and thread_message.run_id == self.run_id:
                #response_message = st.session_state.chat_history.add_assistant_message(prompt=thread_message.content[0].text.value, messageid=thread_message.id, assistantid=self.assistant_id, threadid=self.thread_id, runid=self.run_id)          
                self.assistant_message_id = thread_message.id
                self.assistant_message_content = thread_message.content[0].text.value
    
    def add_and_display_message(self, type):
        if type == "user":
            self.add_message_to_chat_history(type="user")
            self.display_message(type="user")
        else:
            self.add_message_to_chat_history(type="assistant")
            self.display_message(type="assistant")
            
    def add_message_to_chat_history(self, type):
        if type == "user":
            st.session_state.chat_history.add_user_message(prompt=self.user_message_content, assistantid = self.assistant_id, threadid = self.thread_id, messageid = self.user_message_id, runid = self.run_id)    
        else:
            st.session_state.chat_history.add_assistant_message(prompt=self.assistant_message_content, assistantid = self.assistant_id, threadid = self.thread_id, messageid = self.assistant_message_id, runid = self.run_id)

    def display_and_get_prompt(self, chat_container):
        prompt_container = st.container(border=False, height=200)
        with prompt_container:
            self.prompt = st.chat_input(placeholder="Ask Daddy here and watch him cook...", key="_WrestleAssistantPrompt")
            if self.prompt:
                with chat_container:
                    self.run_assistant(prompt=self.prompt)

    def display_message(self, type):
        if type == "user":
            role = "user"
            content = self.user_message_content
        else:
            role = "assistant"
            content = self.assistant_message_content
        with st.chat_message(name=role):
            st.markdown(body=content)
        
    def run_assistant(self, prompt, file_ids=None):
        self.create_message(prompt=prompt)
        self.create_run()
        self.wait_on_run()
        self.add_and_display_message(type="assistant")

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
        
    def encode_images(self, video):
        self.base64frames = []
        while video.isOpened():
            success, frame = video.read()
            if not success:
                break
            _, buffer = cv2.imencode(".jpg", frame)
            self.base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
        video.release()
        print(len(self.base64Frames), "frames read.")


    def get_vision_prompt_message(self, prompt):
        self.vision_prompt = [
            {
                "role": "user",
                "content": [
                    f"{prompt}",
                    *map(lambda x: {"image": x, "resize": 768}, self.base64frames[0::100])
                ],
            },
        ]


