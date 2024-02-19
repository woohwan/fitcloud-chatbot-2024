import streamlit as st
from pydantic import BaseModel
import sys
sys.path.append("..")

from tools import FitInfo
# Read the JSON data from the file
with open("fitInfo.json", "r") as file:
    fitinfo_json = file.read()

# Convert the JSON string back into a Pydantic model instance
fitInfo = FitInfo.parse_raw(fitinfo_json)

import boto3

# Create Bedrock Agent Runtime
session = boto3.session.Session(region_name='us-east-1')
br_agnet_client = session.client(
    service_name='bedrock-agent-runtime'
)

# Agent Info
agentId = "IUFLFZG1TW"
agentAliasId='GDOGYNUEF9'
sessionId  = "fitcloud"

st.set_page_config(initial_sidebar_state="collapsed")
st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title("FitCloud Chatbot Test")
accountId = fitInfo.accountId
token = fitInfo.token

# chat history 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun 
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

completion = ""
# React to user input
if prompt := st.chat_input("2023년 9월 자원 사용량은? 형식으로 입력해 주세요"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):

        resp = br_agnet_client.invoke_agent(
            sessionState = {
                'sessionAttributes': {
                    "token": token,
                    "accountId": accountId,
                },
            },
            agentId=agentId,
            agentAliasId=agentAliasId,
            sessionId=sessionId, 
            inputText=prompt  )
        print("prompt: ", prompt)
        print("resp: ", resp)
        
        for event in resp.get('completion'):
            # print(event)
            chunk = event['chunk']
            # print(chunk)
            completion = completion + chunk['bytes'].decode()
        print(completion)
        
    st.session_state.messages.append({"role": "assistant", "content": completion})
