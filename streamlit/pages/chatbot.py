import streamlit as st
from pydantic import BaseModel
import sys
import time
import datetime
import os

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
sessionId  = "fitcloud-02"

# st.set_page_config(initial_sidebar_state="collapsed")
# st.markdown(
#     """
# <style>
#     [data-testid="collapsedControl"] {
#         display: none
#     }
# </style>
# """,
#     unsafe_allow_html=True,
# )

st.title("FitCloud Chatbot")
accountId = fitInfo.accountId
token = fitInfo.token

# chat history 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun 
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("2023년 9월 자원 사용량은? 형식으로 입력해 주세요"):

    year = datetime.date.today().year
    month = datetime.date.today().month
    day = datetime.date.today().day

    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        
        message_placeholder = st.empty()
        completion = ""
        
        start_time = time.time()

        # prompt = f"""Today's date information looks like this
        # <year>{year}</year> 
        # <month>{month}</month> 
        # <day>{day}</day>
        # If the start_month and end_month information is not available, use the following rules to generate it
        # 1. use the information between <year></year> as the year.
        # 2. convert the inferred month using the <emxample></example> information below.
        # <example>
        # January: 01
        # Feburary: 02
        # November: 11
        # December: 12
        # </example>.
        # 3. Create start_month and end_month as the sum of the year and month from 1 and 2 in the form '%Y%m'.
        # That is, if the year is 2024 and the month is 01, the start_month and end_month will be '202401'.""" + prompt
        
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
            inputText=prompt
        )

        # print("resp: ", resp)
        
        for event in resp.get('completion'):
            # print(event)
            chunk = event['chunk']
            # print(chunk)
            completion = completion + chunk['bytes'].decode()

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")
        print(completion)
        message_placeholder.markdown(completion)
        
    st.session_state.messages.append({"role": "assistant", "content": completion})
