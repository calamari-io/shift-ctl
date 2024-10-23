#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from src.calamari import employees, timesheet, holidays, workweeks, leave, tools

MAX_CALLS_PER_SECOND=10
MAX_CALLS_PER_HOUR=720
API_LOGIN="calamari"

week_days_mapping = ("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY")

def main(args):
  #global base_url, api_key, auth_basic
  base_url = args.base_url
  api_key = args.api_key
  auth_basic=HTTPBasicAuth(API_LOGIN, api_key)

  # validate user input
  tools.validate_date(args.date_from)

  if not args.date_to:
    date_to=date.today().strftime("%Y-%m-%d")
  else:
    date_to=args.date_to

  if base_url[-1] != '/':
    base_url+='/'
  
  # build user email list
  employees_list=[]
  if args.all:
    response=employees.get_all_users(base_url, auth_basic)
    for employee in response:
      employees_list.append(employee['email'])
  else:
    if ',' in args.employees:
      employees_list=args.employees.strip().replace(' ','').split(',')
    else:
      employees_list.append(args.employees.strip().replace(' ',''))


  for employee in employees_list:
    # validate user
    if '@' not in employee:
      print('Error',employee,'doesn\'t seem to be valid email address. Skipping.')
      continue 
    user=employees.get_user(base_url, auth_basic, employee, args.archived)
    if user.status_code != 200:
      continue

    shifts=timesheet.get_shifts(base_url, auth_basic, args.date_from, date_to, employees=[ employee ])

    if shifts.status_code != 200:
      print('Error retrieving shifts for',employee,'. Error: [',shifts.status_code,']: ',shifts.text)
      continue

    if (args.action in ['list', 'delete']):
      if len(shifts.json()) == 0:
        print('No shifts found for',employee,'between',args.date_from,'and',date_to+'. Skipping!')
        continue
    
    if args.action == 'list':
      print("Shifts for",employee)
      print(json.dumps(shifts.json(), indent=4))
    elif args.action == 'delete':
      print("Deleting shifts for",employee)
      timesheet.delete_shifts(base_url, auth_basic, shifts.json(), force=args.force)
    elif args.action == 'create':
      print("Creating shifts for",employee)

      # check employee contract start and termination date (1/2)
      contract_termination_date = user.json()['employees'][0]['plannedFiring']
      contract_start_date = user.json()['employees'][0]['hireDate']
      if contract_termination_date is not None:
        if contract_termination_date < args.date_from:
           print('Employment contract has been terminated',contract_termination_date+'. Skipping.')
           continue
        if contract_termination_date < date_to:
          print('Employment contract will be terminated at',contract_termination_date+'. Adding shifts only to that date.')
          end_date=datetime.strptime(contract_termination_date, '%Y-%m-%d')
        else:
          end_date=datetime.strptime(date_to, '%Y-%m-%d')
      else:
        end_date=datetime.strptime(date_to, '%Y-%m-%d')
     
      if contract_start_date is not None:
        if contract_start_date > date_to:
          print('Employment contract start date is set to',contract_start_date+'. Skipping.')
          continue
        if contract_start_date > args.date_from:
          print('Employment contract will start from',contract_start_date+'. Adding shifts starting from that date.')
          start_date=datetime.strptime(contract_start_date, '%Y-%m-%d')
        else:
          start_date=datetime.strptime(args.date_from, '%Y-%m-%d')
      else:
          start_date=datetime.strptime(args.date_from, '%Y-%m-%d')

      # check employee work week schedule
      work_week_id=user.json()['employees'][0]['workingWeek']['id']
      response=workweeks.get_all_working_weeks(base_url, auth_basic)
      workweek=workweeks.get_working_week(work_week_id,response.json())
      workweek_dict=tools.prepare_workweek_dict(workweek)

      # holidays
      response=holidays.get_holiday(base_url, auth_basic, args.date_from, date_to, employee)
      holidays_list = tools.prepare_holidays_list(response.json())

      # leaves
      response = leave.get_leave(base_url, auth_basic, args.date_from, date_to, employee)
      leave_list = tools.prepare_leave_list(response.json())

      # existing shifts
      shift_list = tools.prepare_shift_list(shifts.json())
      
      # here all the magic happens
      delta = end_date - start_date 

      for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        # skip holidays
        if day in holidays_list:
          print(day.strftime("%Y-%m-%d"),'-> holiday. Skipping.')
          continue;
        # skip leave days
        if day in leave_list:
          print(day.strftime("%Y-%m-%d"),'-> leave request. Skipping.')
          continue;
        # skip existing shifts
        if day in shift_list:
          print(day.strftime("%Y-%m-%d"),'-> shift already exist. Skipping.')
          continue;
        # check user workweek and add shift accordingly
        if week_days_mapping[day.weekday()] in workweek_dict:
          if workweek_dict[week_days_mapping[day.weekday()]]['start_time'] and workweek_dict[week_days_mapping[day.weekday()]]['finish_time']:
            shift_start= day.strftime("%Y-%m-%d")+"T"+workweek_dict[week_days_mapping[day.weekday()]]['start_time']
            shift_end= day.strftime("%Y-%m-%d")+"T"+workweek_dict[week_days_mapping[day.weekday()]]['finish_time']
            response=timesheet.create_shift(base_url, auth_basic, shift_start, shift_end, employee)
            if response.status_code != 200:
              print('Error creating shift for '+day.strftime("%Y-%m-%d")+'. Error: [',response.status_code,']: ',response.text)
            else:
              print('Added shift',response.json()['id'],': ',shift_start,'-',shift_end)
          else:
            print('Employee has undefined work schedule. Skipping!')
  

if __name__ == '__main__':
  parser = argparse.ArgumentParser(prog='shifts_ctl.py', usage='%(prog)s [options]')
  parser.add_argument('action', choices=['list','delete','create'], help="Action to perform")
  parser.add_argument('-k','--api-key', required=True, help='API Key - can be found in Configuration->Integrations->API')
  parser.add_argument('-b','--base-url', required=True, help='API Base URL - can be found in Configuration->Integrations->API. I.e. https://sample-tenant.us.calamari.io/api/')
  parser.add_argument('-f', '--date-from', required=True, help='Start date in \'YYYY-MM-DD\' format') 
  parser.add_argument('-t', '--date-to', required=False, help='End data. Today\'s date if empty') 
  parser.add_argument('--force', required=False, action='store_true', default=False,  help="Force delete without any prompts for confirmation")
  parser.add_argument('--archived', required=False, action='store_true', default=False,  help="Take into account archived users.")
  users = parser.add_mutually_exclusive_group(required=True) 
  users.add_argument('-e', '--employees', help='Comma-separated list of employees emails. Can\'t be used with -a')
  users.add_argument('-a', '--all', action='store_true', default=False,  help='Run for all users. Can\'t be used with -e')
  args, unknown = parser.parse_known_args()
  main(args)
