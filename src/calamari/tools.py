from datetime import date, datetime, timedelta

def validate_date(user_input):
  try:
    date.fromisoformat(user_input)
  except ValueError:
    print("Incorrect data format, should be YYYY-MM-DD")
    exit()

def prepare_workweek_dict(workweek):
  workweek_dict={}
  t_format = '%H:%M:%S'

  for day in workweek['workingDays']:
    if day['isWorkingDay']:
      if day['startTime'] and day['finishTime']:
        start_time = datetime.strptime(day['startTime'][:8], t_format)
        finish_time = datetime.strptime(day['finishTime'][:8], t_format)
        t_delta = finish_time - start_time

        if t_delta.seconds != day['duration']:
          new_finish_time = start_time + timedelta(hours=day['duration']/60/60)
          day['finishTime'] = new_finish_time.strftime('%H:%M:%S.000')
      elif day['duration']:
        day['startTime'] = '09:00:00.000'
        finish_time = datetime.strptime(day['startTime'][:8], t_format) + timedelta(hours=day['duration']/60/60)
        day['finishTime'] = finish_time.strftime('%H:%M:%S.000')
      workweek_dict[day['dayName']] = { 
        'start_time': day['startTime'], 
        'finish_time': day['finishTime'] 
      }
  return workweek_dict

def prepare_holidays_list(holidays):
  holidays_list=[]
  for holiday in holidays:
    start_date=datetime.strptime(holiday['start'], '%Y-%m-%d')
    end_date=datetime.strptime(holiday['end'], '%Y-%m-%d')
    delta = end_date - start_date 
    for i in range(delta.days + 1):
      day = start_date + timedelta(days=i)
      holidays_list.append(day)
  return holidays_list 

def prepare_leave_list(leaves):
  leave_list=[]
  for leave in leaves:
    if (leave['status'] in ['ACCEPTED', 'PENDING', 'PENDING_CANCELLATION']) and leave['absenceCategory'] == 'TIMEOFF':
      start_date=datetime.strptime(leave['from'], '%Y-%m-%d')
      end_date=datetime.strptime(leave['to'], '%Y-%m-%d')
      delta = end_date - start_date 
      for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        leave_list.append(day)
  return leave_list

def prepare_shift_list(shifts):
  shift_list=[]
  for shift in shifts:
    start_date=datetime.strptime(shift['started'][:10], '%Y-%m-%d')
    if shift['finished'] is None: # handle ongoing shift
      end_date=datetime.strptime(shift['started'][:10], '%Y-%m-%d')
    else:
      end_date=datetime.strptime(shift['finished'][:10], '%Y-%m-%d')
    delta = end_date - start_date 
    for i in range(delta.days + 1):
      day = start_date + timedelta(days=i)
      shift_list.append(day)
  return shift_list
