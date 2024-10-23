import requests
import json
from ratelimit import limits, sleep_and_retry

MAX_CALLS_PER_SECOND=10
MAX_CALLS_PER_HOUR=720

@sleep_and_retry
@limits(calls=MAX_CALLS_PER_HOUR, period=3600)
@sleep_and_retry
@limits(calls=MAX_CALLS_PER_SECOND, period=1)
def get_users(base_url, auth_basic, page):
  endpoint_url=base_url+'employees/v1/list'
  payload = {
      "page":  page
  }

  response = requests.post(
     endpoint_url,
     json=payload,
     auth=auth_basic
  )
  if response.status_code != 200:
    print('Error getting users Error: [',response.status_code,']: ',response.text)
    response.raise_for_status()
  
  return response.json()

@sleep_and_retry
@limits(calls=MAX_CALLS_PER_HOUR, period=3600)
@sleep_and_retry
@limits(calls=MAX_CALLS_PER_SECOND, period=1)
def get_user(base_url, auth_basic, user, archived):
  endpoint_url=base_url+'employees/v1/search'
  payload = {
    "employee": user,
    "contractTypes": [],
    "positions": [],
    "teams": [],
    "withArchived": archived
  }

  response = requests.post(
     endpoint_url,
     json=payload,
     auth=auth_basic
  )
  if response.status_code != 200:
    print('Error getting user',user,'Error: [',response.status_code,']: ',response.text)
  
  return response

def archive_user(base_url, auth_basic, user):
  endpoint_url=base_url+'employees/v1/archive'
  payload = {
    "employee": user,
  }

  response = requests.post(
     endpoint_url,
     json=payload,
     auth=auth_basic
  )
  if response.status_code != 204:
    print('Error archiving user',user,'Error: [',response.status_code,']: ',response.text)
  
  return response

def get_all_users(base_url, auth_basic):
  page=0
  employee_list=[]

  while True:
    response=get_users(base_url, auth_basic, page)
    for employee in response['employees']:
      employee_list.append(employee)

    page+=1
    if page == response['totalPages']:
      break

  return employee_list
