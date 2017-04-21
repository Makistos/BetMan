#!/usr/bin/python
import csv
from os import listdir
from os.path import isfile, join
from datetime import datetime
from itertools import imap, groupby
import re
import db
import sys
import sqlite3
import pprint

'''
  File for reading and handling football-data.co.uk's CSV files.
'''
DEBUG = True

DATE_FORMAT = '%Y/%m/%d'
FIELDS = [db.DIV, db.DATE, db.HOME_TEAM, db.AWAY_TEAM, db.FTR, db.FTHG, db.FTAG, db.HS, db.HST, db.AS, db.AST, db.HHW, db.HC,
db.AC, db.HF, db.AF, db.HY, db.AY, db.HR, db.AR, db.ATTENDANCE]

DEFAULT_DB = 'test.db'
# Extract some keys from a dict (the whole match dict is very big, this helps debugging)
extract_dict = lambda keys, dict: reduce(lambda x, y: x.update({y[0]: y[1]}) or x,
                                         map(None, keys, map(dict.get, keys)), {})


def extract_name_date(filename):
    match = re.match(r'(.+)_(\d{4}\-\d{4})(.*)', filename)
    return (match.group(1), match.group(2)), filename


def read_file(file_name):
    matches =[]
    f = open(file_name)
    reader = csv.DictReader(f)
    for line in reader:
        # Make the dict a bit shorter, at least for now. This will be removed later.
        short_dict = extract_dict(FIELDS, line)
        if short_dict['Date'] == '':
            continue
        short_dict['Date'] = datetime.strptime(short_dict[db.DATE], '%d/%m/%y').strftime(DATE_FORMAT)

        matches.append(short_dict)
    f.close()
    return matches


def open_files(data_dir):
    """
      Open csv files (and .csv$ only)
    """

    #return matches


def save_to_db(db_file, data, league, season):
    conn = sqlite3.connect(db_file)
    # We assume one file only includes data for one league (and level)
    if not check_if_exists(conn, 'League', 'csv_name', league):
        print('League missing from database!')
        exit(0)

    c = conn.cursor()
    match_num = {}
    for row in data:
        # Check if teams already exist and if not, add them
        if not check_if_exists(conn, 'Team', 'short_name', row['HomeTeam']):
            home_id = add_team(conn, row['HomeTeam'], row['Div'])
        else:
            cmd = 'SELECT rowid FROM Team WHERE short_name = \"%s\"' % row['HomeTeam']
            c.execute(cmd)
            home_id = c.fetchone()[0]
        if not check_if_exists(conn, 'Team', 'short_name', row['AwayTeam']):
            away_id = add_team(conn, row['AwayTeam'], row['Div'])
        else:
            cmd = 'SELECT rowid FROM Team where short_name = \"%s\"' % row['AwayTeam']
            c.execute(cmd)
            away_id = c.fetchone()[0]

        # Keep record of match numbers
        if not (home_id, 't') in match_num:
            match_num[(home_id, 't')] = 1
        else:
            match_num[(home_id, 't')] += 1
        if not (away_id, 't') in match_num:
            match_num[(away_id, 't')] = 1
        else:
            match_num[(away_id, 't')] += 1

        if not (home_id, 'h') in match_num:
            match_num[(home_id, 'h')] = 1
        else:
            match_num[(home_id, 'h')] += 1
        if not (away_id, 'a') in match_num:
            match_num[(away_id, 'a')] = 1
        else:
            match_num[(away_id, 'a')] += 1

        # Insert home team match data
        cmd = 'INSERT INTO MatchTeam(team, GF, GA, venue, matchno, matchnov) VALUES(?,?,?,?,?,?)'
        values = (home_id, row['FTHG'], row['FTAG'], 'h', match_num[(home_id, 't')], match_num[(home_id, 'h')])
        #if DEBUG: print cmd
        c.execute(cmd, values)
        home_mt = c.lastrowid

        # Insert away team match data
        cmd = 'INSERT INTO MatchTeam(team, GF, GA, venue, matchno, matchnov) VALUES(?,?,?,?,?,?)'
        values = (away_id, row['FTAG'], row['FTHG'], 'a', match_num[(away_id, 't')], match_num[(away_id, 'a')])
        #if DEBUG: print cmd
        c.execute(cmd, values)
        away_mt = c.lastrowid

        cmd = 'INSERT INTO Match(date, season, home_team, away_team) VALUES(?,?,?,?)'
        values = (str(row['Date']), season, home_mt, away_mt)
        #if DEBUG: print "%s:%s" % (cmd, values)
        c.execute(cmd, values)

        cmd = 'INSERT INTO MatchTeamVar (matchteam, elo, GF, GA, GFv, GAv) VALUES(?,?,?,?,?,?)'
        values = (home_mt, 0, 0, 0, 0, 0)
        c.execute(cmd, values)
        values = (away_mt, 0, 0, 0, 0, 0)
        c.execute(cmd, values)
    conn.commit()
    conn.close()


def check_if_exists(conn, table, key, target):
    c = conn.cursor()
    cmd = 'SELECT COUNT(*) from ' + table + ' where ' + key + ' = ' + '\'' + target + '\''
    #print cmd
    c.execute(cmd)
    count = c.fetchone()[0]
    if count == 0:
        return False
    else:
        return True


def add_team(conn, name, league):
    print('Adding team %s to database' % name)
    c = conn.cursor()

    c.execute('SELECT rowid FROM League WHERE csv_name = \"%s\"' % league)
    league_id = c.fetchone()[0]
    cmd = 'INSERT INTO Team (short_name, league) VALUES (?,?)'
    values = (name, league_id)
    #if DEBUG: print "%s:%s" % (cmd, values)
    c.execute(cmd, values)
    return c.lastrowid


def import_files_to_db(args):
    if len(args) < 1:
        print('Directory for data files expected.')
        exit(0)

    data_dir = args[0]
    if DEBUG: print('Directory: %s' % data_dir)
    csv_files = sorted([f for f in listdir(data_dir) if isfile(join(data_dir, f)) and f.endswith(".csv")])

    if DEBUG: print("Using files: " + str(csv_files))

    #match_files = dict(imap(extract_name_date, csv_files))

    if len(args) > 1:
        db = args[1]
    else:
        db = DEFAULT_DB

    for f in csv_files:
        print("File: %s" % f)
        csv_data = read_file(data_dir + '/' + f)
        match = re.match(r'(.+)_(\d{4})-(\d{4}.csv)', f)
        save_to_db(db, csv_data, match.group(1), match.group(2))

    #pprint.pprint(csv_data)


if __name__ == '__main__':
    import_files_to_db(sys.argv[1:])