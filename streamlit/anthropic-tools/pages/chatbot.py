import streamlit as st
import datetime
import time
from fit_tools import time_tool_user

st.title("FitCloud Chatbot")


# chat history 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun 
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if user_prompt := st.chat_input("2023년 9월 자원 사용량은? 형식으로 입력해 주세요"):

    accountId = st.session_state['accountId']
    token = st.session_state['token']
    print("accountId and token in chatbot.py: ", accountId, token)
    user_input = ""

    year = datetime.date.today().year
    month = datetime.date.today().month
    day = datetime.date.today().day
    
    claude_prompt = f"""accountId는 {accountId} 이고, token은 {token}입니다, 
        start_month와 end_month format은 '%Y%m'입니다.
        오늘은 {year}년 {month}월 {day}일 입니다. 
        year 정보가 없을 경우 <year></year>사이의 정보를 사용하세요
        <year>{year}</year>
        month 정보가 하나일 경우, start_month와 end_month는 동일합니다.
        지난 달의 의미 previous month 이고, 작년의 의미는 year-1 입니다.
        year 정보만 있을 경우, 당해 1월 부터 현재까지의 사용량을 계산하세요.
        답변 시 반드시 한국어를 사용하고 계정(account) 정보는 사용하지 마세요.
        {user_prompt}"""

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_prompt)
    
    with st.chat_message("assistant"):
        
        message_placeholder = st.empty()
        completion = ""
        
        start_time = time.time()
        messages = [ {'role': 'user', 'content': claude_prompt}]
        #  string으로  반환
        resp = time_tool_user.use_tools(messages, execution_mode="automatic")
        print(resp)
        
        # for event in resp.get('completion'):
        #     # print(event)
        #     chunk = event['chunk']
        #     # print(chunk)
        #     completion = completion + chunk['bytes'].decode()

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {round(execution_time, 2)} seconds")
        # print(completion)
        message_placeholder.markdown(resp)
        
    st.session_state.messages.append({"role": "assistant", "content": resp})
