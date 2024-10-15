# shift-ctl
Manage calamari.io shifts from command line

## Disclaimer
This software is provided "AS IS", without waranty of any kind. In no event shall the calamari.io company be liable for any claim, damages or other liability. USE AT YOUR OWN RISK!

## Prerequisites
For successfull installation you need [pipenv](https://pipenv.pypa.io/en/latest/). Type:

```pip3 install pipenv```

## Installation

Clone this repository:

```git clone https://github.com/calamari-io/shift-ctl.git```

To install all requirements, simply type:

```pipenv install``` 

*Do it in the main repository directory - the one with file named `Pipfile`.*

## Usage

To use this script you need Calamari API key and your Base URL. You can find detailed instruction on [calamari.io blog](https://help.calamari.io/en/collections/5990-api).

You can check all available script options using `--help` parameter. Simply run:
```
# pipenv run ./shift-ctl.py --help
usage: shifts_ctl.py [options]

positional arguments:
  {list,delete,create}  Action to perform

options:
  -h, --help            show this help message and exit
  -k API_KEY, --api-key API_KEY
                        API Key - can be found in Configuration->Integrations->API
  -b BASE_URL, --base-url BASE_URL
                        API Base URL - can be found in Configuration->Integrations->API. I.e. https://sample-tenant.us.calamari.io/api/
  -f DATE_FROM, --date-from DATE_FROM
                        Start date in 'YYYY-MM-DD' format
  -t DATE_TO, --date-to DATE_TO
                        End data. Today's date if empty
  --force               Force delete without any prompts for confirmation
  -e EMPLOYEES, --employees EMPLOYEES
                        Comma-separated list of employees emails. Can't be used with -a
  -a, --all             Run for all users. Can't be used with -e
```

### Listing shifts
Listing shifts for specific users(s):

```
# pipenv run ./shifts_ctl.py list -k '<API_KEY>' -b '<BASE_URL>' -f '<START_DATE>' -t '<END_DATE>' -e user1@yourdomain.io,user2@yourdomain.io
```
`<START_DATE>/<END_DATE>` - dates in `YYYY-MM-DD` format

Listing shifts for all users in organization:

```
# pipenv run ./shifts_ctl.py list -k '<API_KEY>' -b '<BASE_URL>' -f '<START_DATE>' -t '<END_DATE>' -a
```

### Creating shifts

Shifts will be created according to users work schedule.

Create shifts for specific user(s):

```
# pipenv run ./shifts_ctl.py create -k '<API_KEY>' -b '<BASE_URL>' -f '<START_DATE>' -t '<END_DATE>' -e user1@yourdomain.io,user2@yourdomain.io
```

Create shifts for all users in organization:

```
# pipenv run ./shifts_ctl.py list -k '<API_KEY>' -b '<BASE_URL>' -f '<START_DATE>' -t '<END_DATE>' -a
```

### Delete shifts

Script will ask you to review shifts that you're planning to delete and to confirm deletion. If you shure that you know what you're doing add `--force`

Delete shifts for specific user(s):

```
# pipenv run ./shifts_ctl.py delete -k '<API_KEY>' -b '<BASE_URL>' -f '<START_DATE>' -t '<END_DATE>' -e user1@yourdomain.io,user2@yourdomain.io
```

Delete shifts for specific user(s), no questions asked:

```
# pipenv run ./shifts_ctl.py delete -k '<API_KEY>' -b '<BASE_URL>' -f '<START_DATE>' -t '<END_DATE>' -e user1@yourdomain.io,user2@yourdomain.io --force
```

Delete shifts for all users in organization:

```
# pipenv run ./shifts_ctl.py delete -k '<API_KEY>' -b '<BASE_URL>' -f '<START_DATE>' -t '<END_DATE>' -a
```
