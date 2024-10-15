import requests
import json
from ratelimit import limits, sleep_and_retry

MAX_CALLS_PER_SECOND=10
MAX_CALLS_PER_HOUR=720

@sleep_and_retry
@limits(calls=MAX_CALLS_PER_HOUR, period=3600)
@sleep_and_retry
@limits(calls=MAX_CALLS_PER_SECOND, period=1)
def get_all_working_weeks(base_url, auth_basic):
  endpoint_url=base_url+'working-week/v1/all'

  payload = { }

  response = requests.post(
     endpoint_url,
     json=payload,
     auth=auth_basic
  )

  response.raise_for_status()

  return response

def get_working_week(work_week_id, work_weeks_list):
  for work_week in work_weeks_list:
    if work_week['id'] == work_week_id:
      return work_week
  print('Work week with id',work_week_id,'not found!')
  return {}
