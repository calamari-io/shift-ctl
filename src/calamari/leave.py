import requests
import json
from ratelimit import limits, sleep_and_retry

MAX_CALLS_PER_SECOND=10
MAX_CALLS_PER_HOUR=720

@sleep_and_retry
@limits(calls=MAX_CALLS_PER_HOUR, period=3600)
@sleep_and_retry
@limits(calls=MAX_CALLS_PER_SECOND, period=1)
def get_leave(base_url, auth_basic, date_from, date_to, employee):

  endpoint_url=base_url+'leave/request/v1/find'

  payload = {
      "from": date_from,
      "to": date_to,
      "employee":  employee
  }

  response = requests.post(
     endpoint_url,
     json=payload,
     auth=auth_basic
  )

  response.raise_for_status()

  return response
