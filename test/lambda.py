import json
import requests
import pandas as pd

fitcloud_url = "https://aws-dev.fitcloud.co.kr"
corpId = "KDjAqAG0TnEAAAFK5eqDUL0A"

# account 별 월 별 사용량 (saving plan 포함)
# type: usage - ApplySavingsPlanCompute
def corp_month(
    start_month: str, 
    end_month: str,
    token: str,
    groupBy="account",
    ):
  api_url = fitcloud_url + "/service/trend/corp/month"
  cookies = {
    "JSESSIONID": token,
  }

  data = {
      "from": start_month,
      "to": end_month,
      "groupBy": groupBy,
  }

  resp = requests.post(api_url, json=data, cookies=cookies)

  if resp.status_code == 200:
    # 일반 월 사용량에서 SavingPlan 가격을 제함
    return pd.DataFrame(resp.json())

  else:
    print("error")
#------------------------------------------------------------------------------------
# 월 입력값이  from: '201901', to: '202210'형태일 경우
# 시작 월부터 종료 월까지 리스트로 출력
from datetime import datetime, timedelta

def month_range(start_month, end_month):
    # Create datetime objects for start and end dates
    start_date = datetime.strptime(start_month, "%Y%m")
    end_date = datetime.strptime(end_month, "%Y%m")

    # Initialize list to store months
    months_list = []

    # Iterate over months and add them to the list
    current_month = start_date
    while current_month <= end_date:
        months_list.append(current_month.strftime("%Y%m"))
        current_month = (current_month + timedelta(days=32)).replace(day=1)

    return months_list
#-------------------------------------------------------------------------------------
# account 일자별 사용량을 반환
def ondemand_account_day(
    accountId: str, 
    day_from: str, 
    day_to: str, 
    token: str) -> float:
  api_url = fitcloud_url + "/ondemand/account/day"
  cookies = {
    "JSESSIONID": token,
  }

  data = {
      "from": day_from,
      "to": day_to,
      "accountId": accountId,
  }
  resp = requests.post(api_url, json=data, cookies=cookies)

  if resp.status_code == 200:
    # JSON 형식으로 응답을 파싱 후 usageFee 합계를 구하기 위해 dataframe 의 변환
    df = pd.DataFrame(resp.json())
    usage_sum = round( df['usage_fee'].astype("Float32").sum(), 2)
    return usage_sum

  else:
    print("error")
    
def corp_month_internal(start_month: str, end_month: str, accountId: str, token: str):
  print(start_month, end_month, accountId, token)
  json_data = corp_month(start_month, end_month, token)
  print('json_data: ', json_data)
  df = pd.DataFrame(json_data)
  # accountId = accountId
  # account에 관련된 데이터 추출
  # df = df.query("accountId==@accountId")
  df = df[df['accountId'] == accountId]
  # 기간 내 월 리스트 추출
  month_list = month_range(start_month, end_month)
  # 월 column의 data type을 numeric으로 변환
  df_acc = df.copy()
  df_acc[month_list] = df_acc[month_list].apply(pd.to_numeric)
  # 내부 사용자용 filter: 합산에 포함시킬 항목
  internal_filter = ['Usage','ApplySavingsPlanCompute', 'ApplyRI' ]
  # internal_filter = ['Usage','ApplySavingsPlanCompute']
  df_int = df_acc.query("type in @internal_filter")
  sum = round(df_int[month_list].sum().sum(), 2
  return sum
  

def lambda_handler(event, context):
    # TODO implement
    print(event)
    sessionAttributes = event.get('sessionAttributes')
    accountId = sessionAttributes.get('accountId')
    token = sessionAttributes.get('token')
    params = event.get('parameters')
    param_dict= {}
    for data in params:
      param_dict[data['name']] = data['value']
    
    start_month = param_dict['start_month']
    end_month = param_dict['end_month']
    
    sum = corp_month_internal(start_month, end_month, accountId, token)
    # sum = corp_month_internal(**param_dict)
    
    response_json = {"total_sum": sum }
    response_body = {"application/json": {"body": json.dumps(response_json)}}
    
    action_response = {
        "actionGroup": event["actionGroup"],
        "apiPath": event["apiPath"],
        "httpMethod": event["httpMethod"],
        "parameters": event["parameters"],
        "httpStatusCode": 200,
        "responseBody": response_body,
    }

    session_attributes = event["sessionAttributes"]
    prompt_session_attributes = event["promptSessionAttributes"]

    return {
        "messageVersion": "1.0",
        "response": action_response,
        "sessionAttributes": session_attributes,
        "promptSessionAttributes": prompt_session_attributes,
    }