import requests
import json
from ratelimit import limits, sleep_and_retry

MAX_CALLS_PER_SECOND=10
MAX_CALLS_PER_HOUR=720


@sleep_and_retry
@limits(calls=MAX_CALLS_PER_HOUR, period=3600)
@sleep_and_retry
@limits(calls=MAX_CALLS_PER_SECOND, period=1)
def get_shifts(base_url, auth_basic, date_from, date_to, teams=[], positions=[], contract_types=[], employees=[]):

  endpoint_url=base_url+'clockin/timesheetentries/v1/find'

  payload = {
      "from": date_from,
      "to": date_to,
      "teams": teams,
      "positions": positions,
      "contractTypes": contract_types,
      "employees":  employees
  }

  response = requests.post(
     endpoint_url,
     json=payload,
     auth=auth_basic
  )

  response.raise_for_status()

  return response

@sleep_and_retry
@limits(calls=MAX_CALLS_PER_HOUR, period=3600)
@sleep_and_retry
@limits(calls=MAX_CALLS_PER_SECOND, period=1)
def delete_shift(base_url, auth_basic, shift_id):
  endpoint_url=base_url+'clockin/timesheetentries/v1/delete'
  payload = { "id": shift_id }
  response = requests.post(
     endpoint_url,
     json=payload,
     auth=auth_basic
  )
  if response.status_code != 200:
    print('Error deleting shift',shift_id,'. Error: [',response.status_code,']: ',response.text)
  return response

def delete_shifts(base_url, auth_basic, shift_list=[], force=False):
  user_response=''
  failed_deletion=[]
  # List shifts before deleting it. It will be skipped if run with --force
  while (user_response not in ['y','n', 'Y', 'N']) and not force:
    user_response=(input('Found '+str(len(shift_list))+' shift entries? Do you want to review it before deletion [y/N]:').strip() or 'n')
  if user_response in  ['y' or 'Y']:
    print(json.dumps(shift_list, indent=4))

  # delte shifts
  user_response=''
  while (user_response not in ['y','n', 'Y', 'N']) and not force: # this loop will be skipped if run with --force
    user_response=(input('Delete '+str(len(shift_list))+' shift entries? [y/N]:').strip() or 'n')
  if user_response in  ['y' or 'Y'] or force:
    for shift in shift_list:
      response=delete_shift(base_url, auth_basic, shift['id'])
      if response.status_code != 200:
        failed_deletion.append(shift['id'])
  else:
    return []

  if failed_deletion:
    print('Failed to deleted',len(failed_deletion),'shift(s):',failed_deletion)
  else:
    print('Successfully deleted',len(shift_list),'shift(s)')

  return failed_deletion

@sleep_and_retry
@limits(calls=MAX_CALLS_PER_HOUR, period=3600)
@sleep_and_retry
@limits(calls=MAX_CALLS_PER_SECOND, period=1)
def create_shift(base_url, auth_basic, date_from, date_to, employee, projects=[], breaks=[], description=''):

  endpoint_url=base_url+'clockin/timesheetentries/v1/create'

  payload = {
      "person": employee,
      "shiftStart": date_from,
      "shiftEnd": date_to,
      "breaks": breaks,
      "projects": projects,
      "descrpiton": description
  }

  response = requests.post(
     endpoint_url,
     json=payload,
     auth=auth_basic
  )

  return response
