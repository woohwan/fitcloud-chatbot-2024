import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import fit_tools as fit
import datetime

class Session(BaseModel):
  accountId: str
  token: str
  user_input: str

app = FastAPI()

# CORS 설정
origins = [ 
  "localhost:5317",
  "fitchat.steve-aws.com",
  ]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Prompt info
def create_prompt(accountId, token, user_input):
  year = datetime.date.today().year
  month = datetime.date.today().month
  day = datetime.date.today().day

  cladue_prompt = f"""accountId는 {accountId} 이고, token은 {token}입니다, 
          start_month와 end_month format은 '%Y%m'입니다.
          오늘은 {year}년 {month}월 {day}일 입니다. 
          year 정보가 부족할 경우 <year></year>사이의 정보를 사용하세요
          <year>{year}</year>
          month 정보가 하나일 경우, start_month와 end_month는 동일합니다.
          지난 달의 의미 previous month 이고, 작년의 의미는 last year이고 계산은 {year}-1 입니다.
          답변 시 반드시 한국어를 사용하고, 계정(account) 정보는 사용하지 마세요.
          {user_input}"""
  
  return cladue_prompt


def get_response_claude(prompt) -> str:
  # Retruns claude streaming response

  # Parameters
  # prompt: prompt
  # accountId: fitcloud api를 호출할 때 사용한는 id
  # toek: fitcloud sesssion cookie

  try:
    messages = [ {'role': 'user', 'content': prompt}]
    response = fit.time_tool_user.use_tools(messages, execution_mode="automatic")
    return response
  except Exception as e:
    print("Error in creating campains from Bedrock Claude")
    raise HTTPException(503, "Claude server is busy.")

@app.get("/")
async def read_root():
  return {"Hello": "World"}

@app.post("/chat/")
async def usage_amount(session: Session):
  session_dict = session.model_dump()
  accountId = session_dict['accountId']
  token = session_dict['token']
  uesr_input = session_dict['user_input']
  
  prompt = create_prompt(accountId=accountId, token=token, user_input=uesr_input)
  completions = get_response_claude(prompt)

  print(completions)
  return json.dumps({
    "output": completions
  })