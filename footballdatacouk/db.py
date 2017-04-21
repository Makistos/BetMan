import csv
from prettytable import PrettyTable

# Match data

DIV = 'Div'
DATE = 'Date'           # Date, this is fixed to format yy/mm/dd for easier sorting
HOME_TEAM = 'HomeTeam'
AWAY_TEAM = 'AwayTeam'
REFEREE = 'Referee'     # Referee name
ATTENDANCE = 'ATTENDANCE'
HTHA = 'HTHA'           # Home team home attendance
HTAA = 'HTAA'           # Home team away attendance
ATHA = 'ATHA'           # Home team home attendance
ATAA = 'ATAA'           # Away team away attendance
MONTH = 'MONTH'         # Week the match was played on
WEEKDAY = 'WEEKDAY'     # Weekday the match was played on
FTR = 'FTR'             # Full-time result
FTHG = 'FTHG'           # Full-time home goals
FTAG = 'FTAG'           # Full-time away goals
HE = 'HE'               # Home ELO rating before match
HEC = 'HEC'             # Home ELO rating change from before
AE = 'AE'               # Away ELO rating before match
AEC = 'AEC'             # Away ELO rating change from before
HS = 'HS'               # Home team shots
AS = 'AS'               # Away team shots
HST = 'HST'             # Home team shots on target
AST = 'AST'             # Away team shots on target
HC = 'HC'               # Home team corners
HCC = 'HCC'             # Home team corners conceded
AC = 'AC'               # Away team corners
ACC = 'ACC'             # Away team corners conceded
HHW = 'HHW'             # Home team hit woodwork
AHW = 'AHW'             # Away team hit woodwork
HF = 'HF'               # Home team fouls commited
HFA = 'HFA'             # Home team fouls commited against
AF = 'AF'               # Away team fouls commited
AFA = 'AFA'             # Away team fouls commited against
HO = 'HO'               # Home team offsides
AO = 'AO'               # Away team offsides
HY = 'HY'               # Home team yellow cards
HYA = 'HYA'             # Home team yellow cards against
AY = 'AY'               # Away team yellow cards
AYA = 'AYA'             # Away team yellow cards against
HR = 'HR'               # Home team red cards
HRA = 'HRA'             # Home team red cards against
AR = 'AR'               # Away team red cards
ARA = 'ARA'             # Away team red cards against

HW = 'HW'             # Home wins for last x (for home team)
HD = 'HD'             # Home draws for last x (for home team)
THW = 'THW'           # Total wins for home team in last x
THD = 'THD'           # Total draws for home team in last x
AW = 'AW'             # Away wins for last x (for away team)
AD = 'AD'             # Away draws for last x (for away team)
TAW = 'THW'           # Total wins for away team in last x
TAD = 'THD'           # Total draws for away team in last x
FTHGS = 'FTHGS'       # Full-time goals scored for last x home games (home team)
FTHGC = 'FTHGC'       # Full-time goals conceded for last x home games (home team)
FTAGS = 'FTAGS'         # Full-time goals for last x away games (away team)
FTAGC = 'FTAGC'       # Full-time goals conceded for last x away games (away team)
FTTHGS = 'FTTHGS'       # Total number of goals scored by home team in last x
FTTHGC = 'FTTHGC'       # Total number of goals conceded by home team in last x
FTTAGS = 'FTTAGS'       # Total number of goals scored by away team in last x
FTTAGC = 'FTTAGC'       # Total number of goals conceded by away tem in last x

# Season data
SERIES = 'SERIES'
SEASON = 'SEASON'
HWIN = 'HWIN'
AWIN = 'AWIN'
DRAW = 'DRAW'
HGOALS = 'HGOALS'
AGOALS = 'AGOALS'
NUM_MATCHES = "NUM_MATCHES"

# Team date
TEAM = 'TEAM'
FORM_TABLE = [2, 4, 6, 10, 15]  # Match lengths to which to calculate the form parameters

# Fields that are written to db/txt/csv
ALL_FIELDS = [DATE, HOME_TEAM, AWAY_TEAM, FTR, FTHG, FTAG, HS, HST, AS, AST]
TXT_FIELDS = [DATE, FTR, HOME_TEAM, FTHG, FTAG, AWAY_TEAM, HE, AE, HEC, AEC, MONTH, WEEKDAY]
DB_FIELDS = ALL_FIELDS
CSV_FIELDS = TXT_FIELDS

SEASON_DB_FIELDS = [SERIES, SEASON, HWIN, AWIN, DRAW, HGOALS, AGOALS]
SEASON_TXT_FIELDS = [SERIES, SEASON, HWIN, AWIN, DRAW, HGOALS, AGOALS]
SEASON_CSV_FIELDS = [SERIES, SEASON, HWIN, AWIN, DRAW, HGOALS, AGOALS]


def map_value(data, field_map):
    for f in field_map:
        if f in data:
            yield data[f]


def matches_to_db(data, filename, output_type='text', do_filtering=False):
    """
    Saves the data in the parameter to "type" where type can be "text", "db" or "csv".
    """

    if not do_filtering:
        fields = list(data[0].keys())
    else:
        fields = TXT_FIELDS

    if output_type == 'text':
        tbl = PrettyTable(fields)
        [tbl.add_row([d[f] for f in fields]) for d in data]
        #map(tbl.add_row, [[x for x in map_value(d, fields)] for d in data])
        f = open(filename, 'w')
        f.write(tbl.get_string())
    elif output_type == 'db':
        pass
    elif output_type == 'csv':
        csvfile = open(filename, 'w')
        writer = csv.DictWriter(csvfile, delimiter=',', fieldnames=fields, restval='', extrasaction='ignore', dialect='excel')
        writer.writeheader()
        map(writer.writerow, data)
    else:
        print("Unknown writer type %s." % output_type)


def season_to_db(data, filename, output_type='text'):

    l = []

    if output_type == 'text':
        fields = SEASON_TXT_FIELDS
    elif output_type == 'db':
        fields = SEASON_DB_FIELDS
    else:
        fields = SEASON_CSV_FIELDS

    for ((k, v), d) in data.iteritems():
        l.append(list([k, v]) + [x for x in map_value(d, fields)])

    if output_type == 'text':
        tbl = PrettyTable(fields)
        map(tbl.add_row, l)
        f = open(filename, 'w')
        f.write(tbl.get_string())
    elif output_type == 'db':
        pass
    elif output_type == 'csv':
        l.insert(0, fields)    # Add header
        csvfile = open(filename, 'w')
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerows(l)
    else:
        print("Unknown writer type %s." % output_type)


def versus_to_db(data,filename, output_type='text'):
    pass